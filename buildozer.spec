[app]

# 应用基本信息
title = 沐晴AI
package.name = muqingai
package.domain = com.muqing
version = 0.1

# 源码配置（确保包含 py 和其他资源）
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,mp3,wav

# 入口文件（非常重要！如果你的主程序叫 main.py 就写 main.py）
# 如果是其他名字（比如 muqing.py），请修改这里
entrypoint = main.py

# Python 和 Android 版本
python_version = 3.10
android.api = 31
android.minapi = 21
android.arch = armeabi-v7a,arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 依赖库
requirements = python3,kivy,kivymd,requests,pillow,pygame,numpy

# 图标
icon.filename = ai_chat_icon.png

[buildozer]
log_level = 2
