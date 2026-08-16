[app]

title = 沐晴AI
package.name = muqingai
package.domain = com.muqing
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,json
version = 0.1
python_version = 3.10
android.api = 31
android.minapi = 21
android.arch = armeabi-v7a,arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
requirements = python3,kivy
icon.filename = ai_chat_icon.png

[buildozer]
log_level = 2
warn_on_root = 0
