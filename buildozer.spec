[app]

# 应用名称
title = 沐晴AI

# 包名
package.name = muqingai
package.domain = com.muqing

# 入口文件
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt,json,mp3,wav
version = 0.1

# Python 版本
python_version = 3.10

# Android 配置
android.api = 31
android.minapi = 21
android.arch = armeabi-v7a,arm64-v8a
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 依赖库
requirements = python3,kivy,kivymd,requests,pillow,pygame,numpy

# 图标（确保仓库根目录有这个文件）
icon.filename = ai_chat_icon.png

[buildozer]
log_level = 2
