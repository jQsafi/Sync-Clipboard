import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.clipboard import Clipboard
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.label import Label
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior

# KV Language string for UI definition
kv_string = """
<ClipLabel>:
    font_size: '16sp'
    halign: 'left'
    valign: 'middle'
    padding_x: '10dp'
    text_size: self.width, None
    size_hint_y: None
    height: self.texture_size[1] + dp(20)
    canvas.before:
        Color:
            rgba: (0.2, 0.4, 0.7, 1) if self.selected else (0.25, 0.25, 0.25, 1)
        Rectangle:
            pos: self.pos
            size: self.size

<ClipboardManagerLayout>:
    orientation: 'vertical'
    padding: '5dp'
    spacing: '5dp'
    Label:
        text: 'Clipboard History'
        font_size: '20sp'
        size_hint_y: None
        height: '40dp'
    RecycleView:
        id: rv
        viewclass: 'ClipLabel'
        scroll_type: ['bars', 'content']
        bar_width: 10
        RecycleBoxLayout:
            default_size: None, dp(56)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
            spacing: dp(2)
"""

# Database setup function
def setup_database():
    # The database will be created in the app's internal storage directory
    conn = sqlite3.connect('clipboard.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS clips
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         content TEXT NOT NULL,
         timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    """)
    conn.commit()
    return conn

# View class for items in the RecycleView
class ClipLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(ClipLabel, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(ClipLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        if is_selected:
            Clipboard.copy(self.text)
            print(f"Copied to clipboard: {self.text}")
            # Deselect after copying
            rv.layout_manager.deselect_node(index)


# Main layout for the app
class ClipboardManagerLayout(BoxLayout):
    pass

from kivy.utils import platform

# Main application class
class ClipboardManagerApp(App):
    def build(self):
        Builder.load_string(kv_string)
        self.conn = setup_database()
        self.layout = ClipboardManagerLayout()
        self.load_clips()
        return self.layout

    def on_start(self):
        # For demonstration, I'll add a test clip.
        self.add_clip("Welcome to your Clipboard Manager!")
        
        # Start the background service on Android
        if platform == 'android':
            try:
                from jnius import autoclass
                service_name = u'{}.Service{}'.format('org.gemini.clipboardmanager', 'service'.capitalize())
                service = autoclass(service_name)
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                service.start(mActivity, '')
                print("App: Started service.")
            except Exception as e:
                print(f"App: Error starting service: {e}")

    def on_resume(self):
        # Reload clips when the app is brought to the foreground
        self.load_clips()
        print("App: Resumed, reloading clips.")

    def load_clips(self):
        c = self.conn.cursor()
        c.execute("SELECT content FROM clips ORDER BY timestamp DESC")
        # The data for RecycleView needs to be a list of dicts
        self.layout.ids.rv.data = [{'text': row[0]} for row in c.fetchall()]

    def add_clip(self, text):
        if not text.strip():
            return # Do not add empty strings
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM clips WHERE content = ?", (text,))
        if c.fetchone() is None:
            c.execute("INSERT INTO clips (content) VALUES (?)", (text,))
            self.conn.commit()
            self.load_clips() # Reload to show the new clip

    def on_stop(self):
        self.conn.close()

if __name__ == '__main__':
    ClipboardManagerApp().run()