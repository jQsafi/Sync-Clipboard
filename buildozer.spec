[app]
title = Clipboard Manager
package.name = clipboardmanager
package.domain = org.gemini
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,pyjnius
orientation = portrait
fullscreen = 0
services = service:service.py
android.permissions = READ_CLIPBOARD,FOREGROUND_SERVICE,RECEIVE_BOOT_COMPLETED
android.before_build = python3 patch_build.py
