"""Musicality Android prototype. Case-sensitive musical syntax parser."""
import re
import json
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

NOTE_VALUES = {
    "D": "Đô", "R": "Rê", "M": "Mi", "F": "Pha",
    "S": "Sol", "L": "La", "S'": "Si", "D¹": "Đô quãng cao"
}
SOL_COORD_RE = re.compile(r"^Sol\(\s*(?P<row>\d+)\s*,\s*x(?P<x>\d+)\s*:\s*y(?P<y>\d+)\s*\)?$")


def parse_line(source):
    text = source.strip()
    if not text:
        return {"kind": "empty", "source": source, "message": "Hãy nhập một biểu thức Musicality."}
    match = SOL_COORD_RE.fullmatch(text)
    if match:
        return {
            "kind": "coordinate_note", "source": text, "note": "Sol",
            "row": int(match.group("row")), "x": int(match.group("x")),
            "y": int(match.group("y")),
            "message": "Đã nhận diện hàm Sol và tọa độ theo ví dụ của bạn."
        }
    if text in NOTE_VALUES:
        return {"kind": "note_value", "source": text, "note": NOTE_VALUES[text],
                "message": f"Giá trị nốt: {text} = {NOTE_VALUES[text]}"}
    if text == "sol":
        return {"kind": "symbol", "source": text,
                "message": "sol viết thường là ký hiệu riêng, khác Sol(. Ý nghĩa sẽ do bạn định nghĩa."}
    if "#" in text or "~" in text:
        return {"kind": "unresolved_operator", "source": text,
                "message": "Biểu thức có # hoặc ~. Chưa tự gán ý nghĩa khi quy tắc chưa được xác định."}
    if text.startswith("Sol("):
        return {"kind": "syntax_error", "source": text,
                "message": "Chưa đọc được cú pháp. Ví dụ hiện hỗ trợ: Sol(5,x5:y4"}
    return {"kind": "unknown", "source": text,
            "message": "Ký hiệu này chưa được định nghĩa trong bản thử nghiệm."}


class MusicalityApp(App):
    def build(self):
        Window.clearcolor = (0.055, 0.065, 0.09, 1)
        root = BoxLayout(orientation="vertical", padding=dp(18), spacing=dp(12))
        title = Label(text="[b]Musicality[/b]", markup=True, font_size="30sp",
                      size_hint_y=None, height=dp(48), color=(0.42, 0.91, 0.76, 1))
        subtitle = Label(text="Ngôn ngữ tính toán âm nhạc", font_size="15sp",
                         size_hint_y=None, height=dp(28), color=(0.75, 0.79, 0.86, 1))
        root.add_widget(title)
        root.add_widget(subtitle)
        self.editor = TextInput(
            hint_text="Nhập biểu thức, ví dụ: Sol(5,x5:y4",
            multiline=False, size_hint_y=None, height=dp(54), font_size="18sp",
            background_color=(0.12, 0.14, 0.19, 1), foreground_color=(1, 1, 1, 1),
            hint_text_color=(0.58, 0.62, 0.70, 1), cursor_color=(0.42, 0.91, 0.76, 1),
            padding=[dp(12), dp(14), dp(12), dp(10)])
        self.editor.bind(on_text_validate=lambda *_: self.analyze())
        root.add_widget(self.editor)
        button = Button(text="Phân tích biểu thức", size_hint_y=None, height=dp(50),
                        font_size="17sp", background_normal="", background_color=(0.13, 0.57, 0.46, 1))
        button.bind(on_release=lambda *_: self.analyze())
        root.add_widget(button)
        examples = Label(text="Ví dụ:  Sol(5,x5:y4    •    D    •    S'    •    sol",
                         size_hint_y=None, height=dp(34), font_size="13sp",
                         color=(0.67, 0.72, 0.80, 1))
        root.add_widget(examples)
        scroll = ScrollView()
        self.result = Label(text="Kết quả sẽ hiện ở đây.", markup=True, font_size="16sp",
                            color=(0.92, 0.94, 0.98, 1), size_hint_y=None,
                            halign="left", valign="top", padding=(dp(14), dp(14)))
        self.result.bind(texture_size=self._resize_result)
        scroll.add_widget(self.result)
        root.add_widget(scroll)
        footer = Label(text="Bản thử nghiệm • Chưa phát âm thanh", size_hint_y=None,
                       height=dp(24), font_size="12sp", color=(0.53, 0.58, 0.66, 1))
        root.add_widget(footer)
        return root

    def _resize_result(self, widget, size):
        widget.height = max(size[1] + dp(30), dp(180))

    def analyze(self):
        data = parse_line(self.editor.text)
        lines = [f"[b]Loại:[/b] {data['kind']}", f"[b]Biểu thức:[/b] {data['source']}", "", data.get("message", "")]
        if data.get("kind") == "coordinate_note":
            lines += ["", f"[b]Nốt:[/b] {data['note']}", f"[b]Hàng ngang:[/b] {data['row']}",
                      f"[b]Tọa độ X:[/b] {data['x']}", f"[b]Tọa độ Y:[/b] {data['y']}"]
        elif data.get("kind") == "note_value":
            lines += ["", f"[b]Giá trị nốt:[/b] {data['note']}"]
        self.result.text = "\n".join(lines)


if __name__ == "__main__":
    MusicalityApp().run()
