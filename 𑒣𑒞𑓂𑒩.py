
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import ttk, messagebox
import tkinter.font as tkFont
import ctypes
from ctypes import wintypes
import io
import struct
import zlib
import binascii


# ---------- PART 1: MAIN WINDOW ----------
window = Tk()
window.title("YANTRA Bhasha")
window.geometry("1920x1080")

window.rowconfigure(0, minsize=500, weight=1)
window.columnconfigure(1, minsize=500, weight=1)


# ---------- PART 2: EDITOR FONT ----------
editor_font = tkFont.Font(
    family="Arial",
    size=12
)

image_references = []


# ---------- PART 3: OPEN FILE ----------
def open_letter():
    filepath = askopenfilename(
        filetypes=[
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
    )

    if not filepath:
        return

    txt_edit.delete(1.0, END)
    image_references.clear()

    with open(filepath, "r", encoding="utf-8") as input_file:
        txt_edit.insert(END, input_file.read())

    window.title(f"YANTRA Bhasha - {filepath}")


# ---------- PART 4: SAVE FILE ----------
def save_letter():
    filepath = asksaveasfilename(
        defaultextension=".txt",
        filetypes=[
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
    )

    if not filepath:
        return

    with open(filepath, "w", encoding="utf-8") as output_file:
        output_file.write(txt_edit.get(1.0, END))

    window.title(f"YANTRA Bhasha - {filepath}")


# ---------- PART 5: CHANGE FONT ----------
def change_font():
    font_window = Toplevel(window)
    font_window.title("Change Font")
    font_window.geometry("350x220")
    font_window.resizable(False, False)

    installed_fonts = sorted(set(tkFont.families(window)))

    family_var = StringVar(value=editor_font.cget("family"))
    size_var = StringVar(value=str(editor_font.cget("size")))

    Label(font_window, text="Select Font:").pack(pady=5)

    font_box = ttk.Combobox(
        font_window,
        textvariable=family_var,
        values=installed_fonts,
        state="readonly",
        width=35
    )
    font_box.pack(pady=5)

    Label(font_window, text="Font Size:").pack(pady=5)

    size_box = Spinbox(
        font_window,
        from_=6,
        to=96,
        textvariable=size_var,
        width=10
    )
    size_box.pack(pady=5)

    def apply_font():
        try:
            size = int(size_var.get())

            if not 6 <= size <= 96:
                raise ValueError

            editor_font.configure(
                family=family_var.get(),
                size=size
            )

            font_window.destroy()

        except ValueError:
            messagebox.showerror(
                "Invalid Size",
                "Enter a font size between 6 and 96."
            )

    Button(
        font_window,
        text="Apply Font",
        command=apply_font
    ).pack(pady=15)


# ---------- PART 6: WINDOWS CLIPBOARD IMAGE SUPPORT ----------

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

CF_DIB = 8
CF_BITMAP = 2
GMEM_MOVEABLE = 2
BI_RGB = 0


def clipboard_image():

    if not user32.OpenClipboard(window.winfo_id()):
        return None

    try:
        handle = user32.GetClipboardData(CF_DIB)

        if not handle:
            return None

        kernel32.GlobalLock.restype = ctypes.c_void_p
        kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]

        kernel32.GlobalSize.restype = ctypes.c_size_t
        kernel32.GlobalSize.argtypes = [wintypes.HGLOBAL]

        kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

        ptr = kernel32.GlobalLock(handle)

        if not ptr:
            return None

        try:
            size = kernel32.GlobalSize(handle)

            if size <= 0:
                return None

            dib = ctypes.string_at(ptr, size)

        finally:
            kernel32.GlobalUnlock(handle)

        return dib

    finally:
        user32.CloseClipboard()


# ---------- PART 7: CONVERT DIB TO PPM ----------

def dib_to_ppm(dib):

    if len(dib) < 40:
        raise ValueError("Invalid image data")

    header_size = struct.unpack_from("<I", dib, 0)[0]

    if header_size < 40:
        raise ValueError("Unsupported image format")

    width, height, planes, bits, compression = struct.unpack_from(
        "<iiHHI", dib, 4
    )

    if width <= 0 or height == 0:
        raise ValueError("Invalid image dimensions")

    if bits not in (24, 32) or compression != BI_RGB:
        raise ValueError("Unsupported clipboard image format")

    height_abs = abs(height)
    stride = ((width * bits + 31) // 32) * 4

    offset = header_size

    if len(dib) < offset + stride * height_abs:
        raise ValueError("Incomplete image data")

    pixels = []

    for y in range(height_abs):
        source_y = y if height < 0 else height_abs - 1 - y
        row = dib[offset + source_y * stride:
                  offset + (source_y + 1) * stride]

        for x in range(width):
            index = x * (bits // 8)
            b, g, r = row[index:index + 3]
            pixels.extend((r, g, b))

    return (
        f"P6\n{width} {height_abs}\n255\n".encode() + bytes(pixels)
    )


# ---------- PART 8: PASTE IMAGE ----------

def paste_image(event=None):

    try:
        dib = clipboard_image()

        if not dib:
            return None

        ppm_data = dib_to_ppm(dib)

        photo = PhotoImage(data=ppm_data, format="PPM")

        # Limit huge images
        max_width = 700
        max_height = 700

        scale = max(
            1,
            (photo.width() + max_width - 1) // max_width,
            (photo.height() + max_height - 1) // max_height
        )

        if scale > 1:
            photo = photo.subsample(scale, scale)

        image_references.append(photo)

        txt_edit.image_create(
            INSERT,
            image=photo
        )

        txt_edit.insert(INSERT, "\n")

        return "break"

    except Exception as error:
        messagebox.showerror(
            "Image Error",
            str(error)
        )
        return "break"


# ---------- PART 9: WIDGETS ----------

txt_edit = Text(
    window,
    font=editor_font,
    wrap="word",
    undo=True
)

fr_buttons = Frame(
    window,
    relief=RAISED,
    bd=2
)

btn_open = Button(
    fr_buttons,
    text="Open file",
    command=open_letter
)

btn_save = Button(
    fr_buttons,
    text="Save file As...",
    command=save_letter
)

btn_font = Button(
    fr_buttons,
    text="Change Font",
    command=change_font
)

btn_paste = Button(
    fr_buttons,
    text="Paste Image",
    command=paste_image
)


# ---------- PART 10: KEYBOARD SHORTCUTS ----------

txt_edit.bind("<Control-v>", paste_image)
txt_edit.bind("<Control-V>", paste_image)


# ---------- PART 11: LAYOUT ----------

btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_font.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_paste.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")


# ---------- PART 12: START APPLICATION ----------

window.mainloop()
