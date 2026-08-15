# 沐晴 (MuQing) — Kivy AI 聊天应用（含文件选择器）

中度病娇 AI 聊天应用，Kivy 图形界面，可经 GitHub Actions 打包为独立 APK。
应用名：**沐晴**，应用图标为提供的动漫角色图。

## 功能
- 学习库：从用户对话中学习字/词/词组，≥30 条后开始自主组句（<30 条只回「嗯」）
- 记忆系统：上限 50 天，过期自动删除；数量上限 500 条（FIFO 删最老）
- 性格学习：从用户身上学习，90 天窗口，超 90 天仅产生细微影响（权重 20%），不删除记忆
- 基础性格：中度病娇 0.6 锁死，学习仅做 0~0.12 细微加成（上限 0.72）
- 24 小时主动消息（Clock 驱动）
- 设置页：修改 AI 名字、**「选择头像 / 选择背景」文件选择按钮**（弹出 FileChooser，选定后写回 settings.json 并立即刷新聊天页，无需重打包）

## 本地运行
```
pip install kivy pillow
python main.py
```

## 头像 / 背景 使用说明（文件选择器）
1. 进入设置页 → 点「选择头像」或「选择背景」
2. 弹出系统文件选择窗口（仅显示 png/jpg/jpeg/webp/bmp）
3. 选中图片后点「确定」→ 路径自动写入 settings.json，聊天页头像/背景立即刷新
4. 以上操作**无需重打包 APK**；图片路径默认从 `/sdcard/` 或 App 私有目录读取

> 提示：独立 APK 读取 `/sdcard/` 图片需在 `buildozer.spec` 保留 `READ_EXTERNAL_STORAGE` 权限；
> Android 13+ 建议把图片放入 App 私有目录 `App.get_running_app().user_data_dir` 再选择。

## 桌面应用图标（需重打包）
桌面 launcher 图标编译进 APK，运行时不可替换。要换图标：替换项目根目录 `ai_chat_icon.png`(512×512)，
修改 `buildozer.spec` 的 `icon.filename`，重新运行 GitHub Actions 编译即可。

## 打包 APK（GitHub Actions，免谷歌）
1. 注册 GitHub（邮箱即可），新建公开仓库（如 `muqing-apk`）
2. 将本目录全部文件（含 `.github/workflows/build_apk.yml`）推送上去
3. 仓库 → Actions → 选 `Build 沐晴 APK` → Run workflow
4. 等待 15~40 分钟 → 进入绿色记录 → Artifacts 下载 `muqing-apk.zip` → 解压得 APK → 手机允许未知来源安装

## 文件结构
```
muqing-apk/
├── core.py                         # AI 内核（学习库+记忆50天+性格学习90天）
├── main.py                         # Kivy 聊天界面+设置页(FileChooser)+Clock 24h
├── ai_chat_icon.png                # 应用图标（沐晴）
├── buildozer.spec                  # title=沐晴，icon 已指向图标
├── README.md
└── .github/workflows/build_apk.yml # 一键云端编译独立 APK
```
