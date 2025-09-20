
import time
import sqlite3
from jnius import autoclass, PythonJavaClass, java_method

# --- Database Logic ---
def add_clip_to_db(text, db_path):
    """Adds a new clip to the database if it's not a duplicate."""
    if not text or not text.strip():
        return
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Check for duplicates
        c.execute("SELECT 1 FROM clips WHERE content = ?", (text,))
        if c.fetchone() is None:
            c.execute("INSERT INTO clips (content) VALUES (?)", (text,))
            conn.commit()
            print(f"Service: Added to DB: {text[:30]}...")
        conn.close()
    except Exception as e:
        print(f"Service: Database error: {e}")

# --- Android Service Setup ---
PythonService = autoclass('org.kivy.android.PythonService')
Context = autoclass('android.content.Context')
NotificationChannel = autoclass('android.app.NotificationChannel')
NotificationManager = autoclass('android.app.NotificationManager')
NotificationBuilder = autoclass('android.app.Notification$Builder')
R_drawable = autoclass('android.R$drawable')

# Get the application context
context = PythonService.mService.getApplication().getApplicationContext()

# --- Notification for Foreground Service ---
CHANNEL_ID = "clipboard_manager_channel"
# API level 26+ requires a NotificationChannel.
channel = NotificationChannel(CHANNEL_ID, "Clipboard Manager Service", NotificationManager.IMPORTANCE_LOW)
notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE)
notificationManager.createNotificationChannel(channel)

icon = R_drawable.ic_dialog_info
notification = NotificationBuilder(context, CHANNEL_ID) \
    .setContentTitle("Clipboard Manager") \
    .setContentText("Monitoring clipboard...") \
    .setSmallIcon(icon) \
    .build()

# Start the service in the foreground
PythonService.mService.startForeground(101, notification)


# --- Clipboard Listener ---
class ClipboardListener(PythonJavaClass):
    __javainterfaces__ = ['android/content/ClipboardManager$OnPrimaryClipChangedListener']
    __javacontext__ = 'app'

    def __init__(self, db_path):
        super(ClipboardListener, self).__init__()
        self.db_path = db_path

    @java_method('()V')
    def onPrimaryClipChanged(self):
        try:
            clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE)
            if not clipboard.hasPrimaryClip():
                return

            clip_data = clipboard.getPrimaryClip()
            if clip_data.getItemCount() > 0:
                item = clip_data.getItemAt(0)
                text = item.coerceToText(context)
                if text:
                    add_clip_to_db(str(text), self.db_path)
        except Exception as e:
            print(f"Service: Error in onPrimaryClipChanged: {e}")

# --- Main Service Loop ---
if __name__ == "__main__":
    # The service and the app run in the same process, so they share the same data directory.
    # We get the absolute path to the database file.
    db_path = context.getFilesDir().getAbsolutePath() + '/clipboard.db'
    
    # Initialize the database table in case the service starts before the app
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS clips
            (id INTEGER PRIMARY KEY AUTOINCREMENT,
             content TEXT NOT NULL,
             timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Service: DB init error: {e}")

    listener = ClipboardListener(db_path)
    clipboard_manager = context.getSystemService(Context.CLIPBOARD_SERVICE)
    clipboard_manager.addPrimaryClipChangedListener(listener)

    print("Service: Clipboard listener started.")

    # The service is event-driven, so we just need to keep it alive.
    while True:
        time.sleep(3600)
