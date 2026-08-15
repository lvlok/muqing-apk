# -*- coding: utf-8 -*-
import os, json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from core import AIBrain, DATA_DIR

SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
IMG_EXTS = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp"]


def get_data_dir():
    d = App.get_running_app().user_data_dir
    os.makedirs(d, exist_ok=True)
    return d


class ChatScreen(Screen):
    def __init__(self, brain, **kw):
        super().__init__(**kw)
        self.brain = brain
        self.name = "chat"
        self.layout = BoxLayout(orientation="vertical")

        # 背景（放最底层，allow_stretch 铺满）
        self.bg_img = KivyImage(source="", allow_stretch=True, keep_ratio=False,
                                size_hint=(1, 1), pos_hint={"x": 0, "y": 0})
        self.add_widget(self.bg_img)

        # 头部
        self.header = BoxLayout(orientation="horizontal", size_hint=(1, None), height=50)
        self.avatar_img = KivyImage(source="", size_hint=(None, 1), width=50)
        self.title_lbl = Label(text=brain.settings.get("ai_name", "沐晴"),
                               size_hint=(1, None), height=50, font_size=20)
        self.set_btn = Button(text="设置", size_hint=(None, None), size=(70, 50))
        self.set_btn.bind(on_release=lambda x: set_screen("settings"))
        self.header.add_widget(self.avatar_img)
        self.header.add_widget(self.title_lbl)
        self.header.add_widget(self.set_btn)

        # 聊天区
        self.chat_box = BoxLayout(orientation="vertical", size_hint_y=None, padding=8, spacing=6)
        self.chat_box.bind(minimum_height=self.chat_box.setter("height"))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.chat_box)

        # 输入区
        self.input_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=48)
        self.text_in = TextInput(hint_text="说点什么…", multiline=False, size_hint=(0.8, 1))
        self.send_btn = Button(text="发送", size_hint=(0.2, 1))
        self.send_btn.bind(on_release=self._on_send)
        self.text_in.bind(on_text_validate=self._on_send)
        self.input_row.add_widget(self.text_in)
        self.input_row.add_widget(self.send_btn)

        self.layout.add_widget(self.header)
        self.layout.add_widget(self.scroll)
        self.layout.add_widget(self.input_row)
        self.add_widget(self.layout)
        self._refresh_assets()

    # ---------- 资源刷新 ----------
    def _refresh_assets(self):
        s = self.brain.settings
        av = s.get("avatar_path", "")
        bg = s.get("bg_path", "")
        if av and os.path.exists(av):
            self.avatar_img.source = av
            self.avatar_img.reload()
        if bg and os.path.exists(bg):
            self.bg_img.source = bg
            self.bg_img.reload()
        self.title_lbl.text = s.get("ai_name", "沐晴")

    def on_pre_enter(self, *a):
        self._refresh_assets()

    def reload_avatar(self):
        path = self.brain.settings.get("avatar_path", "")
        if path and os.path.exists(path):
            self.avatar_img.source = path
            self.avatar_img.reload()

    def reload_bg(self):
        path = self.brain.settings.get("bg_path", "")
        if path and os.path.exists(path):
            self.bg_img.source = path
            self.bg_img.reload()

    # ---------- 聊天逻辑 ----------
    def _on_send(self, *a):
        txt = self.text_in.text.strip()
        if not txt:
            return
        self._add_bubble(txt, "user")
        self.text_in.text = ""
        reply = self.brain.reply(txt)
        self._add_bubble(reply, "ai")

    def _add_bubble(self, text, who):
        lbl = Label(text=text, size_hint_y=None, halign="left", valign="top",
                    text_size=(self.width - 40, None), padding=(10, 8))
        lbl.bind(texture_size=lambda *a: setattr(lbl, "height", lbl.texture_size[1] + 16))
        color = (0.95, 0.85, 0.9, 1) if who == "ai" else (0.85, 0.9, 0.95, 1)
        lbl.color = (0.1, 0.1, 0.1, 1)

        def _draw(*a):
            lbl.canvas.before.clear()
            with lbl.canvas.before:
                Color(*color)
                RoundedRectangle(pos=lbl.pos, size=lbl.size, radius=[10])
        lbl.bind(pos=_draw, size=_draw)
        self.chat_box.add_widget(lbl)
        Clock.schedule_once(lambda dt: setattr(self.scroll, "scroll_y", 0), 0.05)


class SettingsScreen(Screen):
    def __init__(self, brain, **kw):
        super().__init__(**kw)
        self.brain = brain
        self.name = "settings"
        self.layout = BoxLayout(orientation="vertical", padding=16, spacing=10)

        self.layout.add_widget(Label(text="设置", size_hint=(1, None), height=40, font_size=22))

        self.ai_name_in = TextInput(text=brain.settings.get("ai_name", "沐晴"),
                                    hint_text="AI 名字", size_hint=(1, None), height=40)
        self.avatar_in = TextInput(text=brain.settings.get("avatar_path", ""),
                                   hint_text="头像路径(/sdcard/...)", size_hint=(1, None), height=40)
        self.bg_in = TextInput(text=brain.settings.get("bg_path", ""),
                               hint_text="聊天背景路径", size_hint=(1, None), height=40)

        # 文件选择按钮
        self.btn_row = BoxLayout(orientation="horizontal", size_hint=(1, None), height=44, spacing=8)
        self.btn_avatar = Button(text="选择头像")
        self.btn_bg = Button(text="选择背景")
        self.btn_avatar.bind(on_release=lambda x: self.pick_file("avatar"))
        self.btn_bg.bind(on_release=lambda x: self.pick_file("bg"))
        self.btn_row.add_widget(self.btn_avatar)
        self.btn_row.add_widget(self.btn_bg)

        self.save_btn = Button(text="保存并返回聊天", size_hint=(1, None), height=44)
        self.save_btn.bind(on_release=self._save)

        for w in [self.ai_name_in, self.avatar_in, self.bg_in, self.btn_row, self.save_btn]:
            self.layout.add_widget(w)
        self.add_widget(self.layout)

    # ---------- 文件选择弹窗 ----------
    def pick_file(self, mode):
        """弹出 FileChooser，选定后写回 settings.json 并刷新聊天页。"""
        fc = FileChooserListView(filters=IMG_EXTS)
        box = BoxLayout(orientation="vertical")
        box.add_widget(fc)

        def on_ok(*a):
            if fc.selection:
                path = fc.selection[0]
                key = "avatar_path" if mode == "avatar" else "bg_path"
                self.brain.update_settings(key, path)
                # 同步到输入框显示
                if mode == "avatar":
                    self.avatar_in.text = path
                else:
                    self.bg_in.text = path
                # 立即刷新聊天页
                try:
                    chat = self.manager.get_screen("chat")
                    if mode == "avatar":
                        chat.reload_avatar()
                    else:
                        chat.reload_bg()
                except Exception:
                    pass
            popup.dismiss()

        btn = BoxLayout(size_hint_y=None, height=44)
        btn.add_widget(Button(text="取消", on_release=lambda *a: popup.dismiss()))
        btn.add_widget(Button(text="确定", on_release=on_ok))
        box.add_widget(btn)

        popup = Popup(title="选择图片（%s）" % ("头像" if mode == "avatar" else "背景"),
                      content=box, size_hint=(0.95, 0.85))
        popup.open()

    # ---------- 保存 ----------
    def _save(self, *a):
        self.brain.update_settings("ai_name", self.ai_name_in.text.strip() or "沐晴")
        self.brain.update_settings("avatar_path", self.avatar_in.text.strip())
        self.brain.update_settings("bg_path", self.bg_in.text.strip())
        set_screen("chat")


sm = None


def set_screen(name):
    if sm:
        sm.current = name


class MuQingApp(App):
    def build(self):
        global sm
        os.makedirs(DATA_DIR, exist_ok=True)
        self.brain = AIBrain()
        sm = ScreenManager()
        sm.add_widget(ChatScreen(self.brain))
        sm.add_widget(SettingsScreen(self.brain))
        # 24h 主动消息
        Clock.schedule_interval(self._cycle_check, 60)
        return sm

    def _cycle_check(self, dt):
        hours = self.brain.settings.get("cycle_hours", 24)
        if not hasattr(self, "_last"):
            self._last = __import__("datetime", fromlist=["datetime"]).datetime.now()
        now = __import__("datetime", fromlist=["datetime"]).datetime.now()
        if (now - self._last).total_seconds() >= hours * 3600:
            msg = self.brain.主动_message()
            if msg and sm and sm.current_screen.name == "chat":
                chat = sm.get_screen("chat")
                chat._add_bubble(msg, "ai")
            self._last = now


if __name__ == "__main__":
    MuQingApp().run()
