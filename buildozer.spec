[app]
title = 沐晴
package.name = muqing
package.domain = com.yourname
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 0.1
requirements = python3==3.10,kivy==2.3.0,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
icon.filename = %(source.dir)s/ai_chat_icon.png

[buildozer]
log_level = 2
warn_on_root = 1
