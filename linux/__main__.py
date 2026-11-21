"""Linux desktop build of Its Everyday Bro."""

import base64
import math
import re
import tkinter as tk
import tkinter.font as tkfont
from importlib.resources import files

BACKGROUND = "#efefef"
INK = "#191919"
EDITOR_BACKGROUND = "#1e1e1e"
COLORS = {
    "comment": "#7cae70",
    "string": "#e1a184",
    "keyword": "#82afee",
    "number": "#bbd09a",
}
KEYWORDS = frozenset(
    "and break do else elseif end false for function goto if in local nil not "
    "or repeat return then true until while".split()
)
TOKENS = re.compile(
    r"(?P<long_comment>--\[(?P<comment_level>=*)\[)"
    r"|(?P<long_string>\[(?P<string_level>=*)\[)"
    r"|(?P<comment>--[^\n]*)"
    r"""|(?P<string>"(?:\\[\s\S]|[^"\\\r\n])*"?|'(?:\\[\s\S]|[^'\\\r\n])*'?)"""
    r"|(?P<number>0[xX](?:[0-9a-fA-F]+(?:\.(?!\.)[0-9a-fA-F]*)?|\.[0-9a-fA-F]+)"
    r"(?:[pP][+-]?[0-9]+)?|(?:[0-9]+(?:\.(?!\.)[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?)"
    r"|(?P<word>[A-Za-z_][A-Za-z_0-9]*)"
)


def lua_tokens(source):
    offset = 0
    while match := TOKENS.search(source, offset):
        category = match.lastgroup
        offset = match.end()
        if category in ("long_comment", "long_string"):
            category = category.removeprefix("long_")
            closing = "]" + match[category + "_level"] + "]"
            end = source.find(closing, offset)
            offset = len(source) if end == -1 else end + len(closing)
        elif category == "word":
            if match[0] not in KEYWORDS:
                continue
            category = "keyword"
        yield category, match.start(), offset


class LuaEditor(tk.Text):
    def __init__(self, parent, family):
        super().__init__(
            parent, bg=EDITOR_BACKGROUND, fg="#dcdcdc", insertbackground="#dcdcdc",
            selectbackground="#4a6685", selectforeground="#ffffff", borderwidth=0,
            highlightthickness=0, padx=7, pady=6, wrap="none", undo=True,
            font=(family, -16),
        )
        self.highlight_job = None
        for category, color in COLORS.items():
            self.tag_configure(category, foreground=color)
        self.bind("<<Modified>>", self.schedule_highlight)
        self.bind("<Control-y>", self.redo)
        self.tag_raise("sel")

    def redo(self, _event):
        self.event_generate("<<Redo>>")
        return "break"

    def schedule_highlight(self, _event):
        if self.edit_modified():
            self.edit_modified(False)
        if self.highlight_job is not None:
            self.after_cancel(self.highlight_job)
        self.highlight_job = self.after(110, self.highlight)

    def highlight(self):
        self.highlight_job = None
        for category in COLORS:
            self.tag_remove(category, "1.0", "end")
        for category, start, end in lua_tokens(self.get("1.0", "end-1c")):
            self.tag_add(category, f"1.0 + {start} chars", f"1.0 + {end} chars")


def checkbox_image(parent, checked):
    image = tk.PhotoImage(master=parent, width=21, height=21)
    image.put("#6f8f98" if checked else "#7b7b7b", to=(0, 0, 21, 21))
    image.put("#d7e9ed" if checked else "#f5f5f5", to=(1, 1, 20, 20))
    if checked:
        for x, y in ((4, 10), (5, 11), (6, 12), (7, 13), (8, 12), (9, 11),
                     (10, 10), (11, 9), (12, 8), (13, 7), (14, 6), (15, 5)):
            image.put("#4e707b", to=(x, y, x + 2, y + 2))
    return image


class BroWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Its Everyday Bro Executor")
        self.geometry("1152x648")
        self.minsize(780, 480)
        self.configure(bg=BACKGROUND)
        families = set(tkfont.families(self))
        ui_font = next(
            (name for name in ("Segoe UI", "Liberation Sans", "Arial", "DejaVu Sans") if name in families),
            tkfont.nametofont("TkDefaultFont").actual("family"),
        )
        self.ui_scale = 0.86 if ui_font == "DejaVu Sans" else 1.0
        mono_font = next(
            (name for name in ("Consolas", "Liberation Mono", "DejaVu Sans Mono") if name in families),
            tkfont.nametofont("TkFixedFont").actual("family"),
        )

        self.heading(self, "Its Everyday Bro", ui_font, 34).place(x=8, y=16)
        editor_frame = tk.Frame(self, bg=EDITOR_BACKGROUND, highlightbackground="#414141", highlightthickness=1)
        editor_frame.place(x=8, y=64, relwidth=1, width=-297, relheight=1, height=-136)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)
        self.editor = LuaEditor(editor_frame, mono_font)
        self.editor.grid(row=0, column=0, sticky="nsew")
        for orient, view, row, column, sticky, scrollcommand in (
            ("horizontal", self.editor.xview, 1, 0, "ew", "xscrollcommand"),
            ("vertical", self.editor.yview, 0, 1, "ns", "yscrollcommand"),
        ):
            scrollbar = tk.Scrollbar(editor_frame, orient=orient, command=view)
            scrollbar.grid(row=row, column=column, sticky=sticky)
            scrollbar.grid_remove()
            self.editor.configure(**{
                scrollcommand: lambda first, last, bar=scrollbar: self.show_scrollbar(bar, first, last)
            })

        settings = tk.Frame(self, bg=BACKGROUND)
        settings.place(relx=1, x=-271, y=65, width=256, relheight=1, height=-135)
        self.heading(settings, "Settings", ui_font, 32).place(x=0, y=3)
        self.check_images = (checkbox_image(self, False), checkbox_image(self, True))
        self.bypass = tk.BooleanVar(self, False)
        self.serverside = tk.BooleanVar(self, True)
        self.add_checkbox(settings, "fe bypass mode", self.bypass, 47, ui_font)
        self.add_checkbox(settings, "serverside mode", self.serverside, 80, ui_font)

        image_bytes = files("bro_assets").joinpath("thumbnail.png").read_bytes()
        self.original_thumbnail = tk.PhotoImage(data=base64.b64encode(image_bytes))
        self.thumbnail = self.original_thumbnail
        self.resize_job = None
        self.picture = tk.Label(settings, image=self.thumbnail, borderwidth=0, bg=BACKGROUND)
        self.picture.place(x=1, y=134, width=255, relheight=1, height=-135)
        self.picture.bind("<Configure>", self.schedule_thumbnail_resize)

        self.buttons = (
            self.add_button("Execute", ui_font, 8),
            self.add_button("Clear", ui_font, 174),
            self.add_button("Inject", ui_font, -443, relx=1),
        )

    def heading(self, parent, text, family, size):
        return tk.Label(parent, text=text, font=(family, -round(size * self.ui_scale), "bold"),
                        bg=BACKGROUND, fg=INK, padx=0, pady=0, borderwidth=0)

    @staticmethod
    def show_scrollbar(bar, first, last):
        if float(first) <= 0 and float(last) >= 1:
            bar.grid_remove()
        else:
            bar.grid()
        bar.set(first, last)

    def add_checkbox(self, parent, text, variable, y, family):
        checkbox = tk.Checkbutton(
            parent, text=" " + text, variable=variable, image=self.check_images[0],
            selectimage=self.check_images[1], compound="left", indicatoron=False,
            font=(family, -round(16 * self.ui_scale)), fg=INK, activeforeground=INK,
            bg=BACKGROUND, activebackground=BACKGROUND, selectcolor=BACKGROUND,
            anchor="w", relief="flat", offrelief="flat", overrelief="flat",
            borderwidth=0, highlightthickness=1, highlightbackground=BACKGROUND,
            highlightcolor="#737373", padx=0, pady=0,
        )
        checkbox.place(x=0, y=y, width=245, height=25)

    def add_button(self, text, family, x, relx=0):
        button = tk.Button(
            self, text=text, font=(family, -round(23 * self.ui_scale), "bold"), fg=INK, activeforeground=INK,
            bg="#e1e1e1", activebackground="#dddddd", relief="flat",
            overrelief="flat", bd=0, highlightthickness=2,
            highlightbackground="#c1c1c1", highlightcolor="#777777",
        )
        button.place(x=x, relx=relx, rely=1, y=-60, width=154, height=45)
        return button

    def schedule_thumbnail_resize(self, event):
        if self.resize_job is not None:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(100, self.resize_thumbnail, event.height)

    def resize_thumbnail(self, height):
        self.resize_job = None
        original_height = self.original_thumbnail.height()
        if height == original_height:
            self.thumbnail = self.original_thumbnail
        else:
            img = tk.PhotoImage(master=self)
            factor = math.gcd(height, original_height)
            img.tk.call(img, "copy", self.original_thumbnail,
                        "-zoom", 1, height // factor, "-subsample", 1, original_height // factor)
            self.thumbnail = img
        self.picture.configure(image=self.thumbnail)


def main():
    try:
        window = BroWindow()
    except tk.TclError as error:
        raise SystemExit(f"Could not open the desktop window: {error}") from error
    window.mainloop()


if __name__ == "__main__":
    main()
