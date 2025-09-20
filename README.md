# Clipboard Manager

Clipboard Manager is an Android application built with Kivy that allows users to manage their clipboard history. It provides a service that runs in the background to capture clipboard changes and a user interface to view and interact with the clipboard history.

## Build Instructions (for Termux on Android)

Follow these steps to build the application on your Android device using Termux:

1.  **Install Termux and necessary packages:**
    Open Termux and run the following commands to update packages and install required tools:
    ```bash
    pkg update && pkg upgrade
    pkg install git python buildozer openjdk-17 proot
    pip install --upgrade pip setuptools wheel
    pip install cython kivy==2.2.1
    ```

2.  **Clone the repository:**
    ```bash
    git clone https://github.com/jQsafi/Sync-Clipboard.git
    cd Sync-Clipboard
    ```

3.  **Initialize Git (if not already done):**
    If you are building from a fresh clone, you might need to initialize Git and configure it:
    ```bash
    git init
    git config --global --add safe.directory /storage/emulated/0/dev/clipboard_manager # Adjust path if your project is in a different directory
    git add .
    git commit -m "Initial commit"
    ```

4.  **Build the application:**
    Run the build process within a `termux-chroot` environment to ensure all dependencies are found correctly:
    ```bash
    termux-chroot buildozer android debug
    ```
    The generated APK will be located in the `bin/` directory.
