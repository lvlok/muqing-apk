# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
import os

Window.clearcolor = get_color_from_hex("#1a1a2e")


class ChatScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = 8
        self.padding = [10, 10, 10, 10]

        title = Label(
            text="沐晴",
            color=get_color_from_hex("#ff99cc"),
            font_size="22sp",
            size_hint_y=None,
            height="50dp",
            bold=True
        )
        self.add_widget(title)

        self.scroll = ScrollView()
        self.chat_log = BoxLayout(orientation="vertical", size_hint_y=None, spacing=6)
        self.chat_log.bind(minimum_height=self.chat_log.setter("height"))
        self.scroll.add_widget(self.chat_log)
        self.add_widget(self.scroll)

        input_row = BoxLayout(size_hint_y=None, height="48dp", spacing=6)
        self.text_input = TextInput(
            hint_text="说点什么…",
            multiline=False,
            background_color=get_color_from_hex("#2a2a4a"),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(1, 1, 1, 1)
        )
        self.text_input.bind(on_text_validate=self.send_message)
        send_btn = Button(
            text="发送",
            size_hint_x=None,
            width="70dp",
            background_color=get_color_from_hex("#ff6699")
        )
        send_btn.bind(on_release=self.send_message)
        input_row.add_widget(self.text_input)
        input_row.add_widget(send_btn)
        self.add_widget(input_row)

        self._add_bubble("沐晴初始化完成~ 你好呀！", "ai")

    def send_message(self, *args):
        text = self.text_input.text.strip()
        if not text:
            return
        self._add_bubble(text, "user")
        self.text_input.text = ""
        reply = f"嗯…你说的是「{text}」对吧~"
        Clock.schedule_once(lambda dt: self._add_bubble(reply, "ai"), 0.5)

    def _add_bubble(self, text, sender):
        bubble = Label(
            text=text,
            size_hint_y=None,
            color=(1, 1, 1, 1) if sender == "user" else get_color_from_hex("#ffccf0"),
            text_size=(Window.width * 0.7, None),
            halign="right" if sender == "user" else "left"
        )
        bubble.bind(texture_size=lambda *_: setattr(
            bubble, "height", bubble.texture_size[1] + 16))
        self.chat_log.add_widget(bubble)
        self.scroll.scroll_to(bubble)


class MuQingApp(App):
    def build(self):
        self.title = "沐晴"
        sm = ScreenManager()
        chat_screen = Screen(name="chat")
        chat_screen.add_widget(ChatScreen())
        sm.add_widget(chat_screen)
        return sm


if __name__ == "__main__":
    MuQingApp().run()
