from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter import ttk, messagebox, colorchooser
import tkinter.font as tkFont
import ctypes
from ctypes import wintypes
import struct
import os
# ---------- PART 1: MAIN WINDOW ----------
window = Tk()
window.title("YANTRA Bhasha")
window.geometry("1920x1080")
window.rowconfigure(0, minsize=500, weight=1)
window.columnconfigure(1, minsize=500, weight=1)
# ---------- PART 2: DOCUMENT STORAGE ----------
documents = {}
document_counter = 0
current_document = None

image_references = []

# ---------- APPLICATION THEMES ----------
APP_THEMES = {
    "light": {
        "bg": "#F2F4F8",
        "panel": "#E5E7EB",
        "editor": "#FFFFFF",
        "fg": "#1F2937",
        "button": "#D1D5DB",
        "button_fg": "#111827",
        "select": "#BFDBFE",
        "insert": "#111827"
    },
    "dark": {
        "bg": "#171923",
        "panel": "#222633",
        "editor": "#111827",
        "fg": "#E5E7EB",
        "button": "#374151",
        "button_fg": "#FFFFFF",
        "select": "#334F75",
        "insert": "#FFFFFF"
    }
}
app_theme = APP_THEMES["light"].copy()


def apply_theme_to_widget(widget):
    """Apply the current application colours to supported Tk widgets."""
    try:
        widget_class = widget.winfo_class()

        if widget_class in ("Text",):
            widget.configure(
                background=app_theme["editor"],
                foreground=app_theme["fg"],
                insertbackground=app_theme["insert"],
                selectbackground=app_theme["select"]
            )
        elif widget_class == "Listbox":
            widget.configure(
                background=app_theme["editor"],
                foreground=app_theme["fg"],
                selectbackground=app_theme["select"],
                selectforeground=app_theme["fg"]
            )
        elif widget_class == "Button":
            widget.configure(
                background=app_theme["button"],
                foreground=app_theme["button_fg"],
                activebackground=app_theme["select"],
                activeforeground=app_theme["fg"]
            )
        elif widget_class in ("Frame", "TFrame"):
            widget.configure(background=app_theme["panel"])
        elif widget_class in ("Label",):
            widget.configure(
                background=app_theme["panel"],
                foreground=app_theme["fg"]
            )
        elif widget_class == "Scrollbar":
            widget.configure(
                background=app_theme["panel"],
                troughcolor=app_theme["bg"],
                activebackground=app_theme["select"]
            )
    except TclError:
        pass

    for child in widget.winfo_children():
        apply_theme_to_widget(child)


def apply_app_theme(theme):
    global app_theme

    app_theme = theme.copy()
    window.configure(background=app_theme["bg"])

    for child in window.winfo_children():
        apply_theme_to_widget(child)


def change_background():
    """Let the user select light mode, dark mode, or a custom app colour."""
    theme_window = Toplevel(window)
    theme_window.title("Application Appearance")
    theme_window.geometry("340x260")
    theme_window.resizable(False, False)
    theme_window.transient(window)
    theme_window.configure(background=app_theme["bg"])

    Label(
        theme_window,
        text="Choose application appearance",
        font=("Arial", 12, "bold"),
        background=app_theme["bg"],
        foreground=app_theme["fg"]
    ).pack(pady=(18, 12))

    Button(
        theme_window,
        text="Light Mode",
        width=25,
        command=lambda: (
            apply_app_theme(APP_THEMES["light"]),
            theme_window.destroy()
        )
    ).pack(pady=6)

    Button(
        theme_window,
        text="Dark Mode",
        width=25,
        command=lambda: (
            apply_app_theme(APP_THEMES["dark"]),
            theme_window.destroy()
        )
    ).pack(pady=6)

    def choose_custom_colour():
        selected = colorchooser.askcolor(
            parent=theme_window,
            title="Choose Application Background Colour",
            color=app_theme["bg"]
        )

        if selected[1]:
            custom = {
                "bg": selected[1],
                "panel": selected[1],
                "editor": selected[1],
                "fg": "#FFFFFF" if sum(selected[0]) < 384 else "#202020",
                "button": "#333333" if sum(selected[0]) < 384 else "#DDDDDD",
                "button_fg": "#FFFFFF" if sum(selected[0]) < 384 else "#202020",
                "select": "#64748B",
                "insert": "#FFFFFF" if sum(selected[0]) < 384 else "#202020"
            }
            apply_app_theme(custom)
            theme_window.destroy()

    Button(
        theme_window,
        text="Custom Background Colour",
        width=25,
        command=choose_custom_colour
    ).pack(pady=6)
# ---------- PART 3: GET CURRENT EDITOR ----------
def get_editor():
    if current_document is None:
        return None
    return documents[current_document]["editor"]
def get_state():
    if current_document is None:
        return None
    return documents[current_document]
# ---------- PART 4: CREATE NEW TAB ----------
def new_tab(content="", filepath=None):
    global document_counter
    global current_document
    document_counter += 1
    document_id = document_counter
    if filepath:
        tab_name = os.path.basename(filepath)
    else:
        tab_name = f"Document {document_id}"
    # Create editor
    editor = Text(
        editor_frame,
        font=("Arial", 12),
        wrap="word",
        undo=True
    )
    editor.grid(
        row=0,
        column=0,
        sticky="nsew"
    )
    apply_theme_to_widget(editor)

    # Keep the selected Bold / Italic / Underline formatting active while typing.
    # This binding must be installed for every new document tab.
    editor.bind(
        "<KeyPress>",
        lambda event, current_editor=editor:
            remember_typing_position(event, current_editor),
        add="+"
    )

    if content:
        editor.insert(END, content)
    font = tkFont.Font(
        family="Arial",
        size=12
    )
    editor.configure(font=font)

    documents[document_id] = {
        "editor": editor,
        "filepath": filepath,
        "name": tab_name,
        "font": font,
        "images": [],
        "fonts": {},
        "color": "#000000",
        "family": "Arial",
        "size": 12,
        "bold": False,
        "italic": False,
        "underline": False,
        "active_tag": None,
        "tag_counter": 0
    }
    # Hide previous editor
    for doc in documents.values():
        doc["editor"].grid_remove()
    editor.grid()
    current_document = document_id
    # Add vertical tab to list
    tab_list.insert(END, tab_name)
    tab_list.selection_clear(0, END)
    tab_list.selection_set(END)
    tab_list.see(END)
    editor.focus_set()
    update_title()
# ---------- PART 5: SWITCH DOCUMENT ----------
def switch_tab(event=None):
    global current_document
    selection = tab_list.curselection()
    if not selection:
        return
    selected_index = selection[0]
    document_ids = list(documents.keys())
    if selected_index >= len(document_ids):
        return
    selected_id = document_ids[selected_index]
    # Hide all editors
    for doc in documents.values():
        doc["editor"].grid_remove()
    # Show selected editor
    documents[selected_id]["editor"].grid()
    current_document = selected_id
    get_editor().focus_set()
    update_title()
# ---------- PART 6: UPDATE WINDOW TITLE ----------
def update_title():
    if current_document is None:
        window.title("YANTRA Bhasha")
        return
    state = get_state()
    if state["filepath"]:
        window.title(
            "YANTRA Bhasha - " +
            os.path.basename(state["filepath"])
        )
    else:
        window.title(
            "YANTRA Bhasha - " + state["name"]
        )
# ---------- PART 7: OPEN FILE ----------
def open_letter():
    filepath = askopenfilename(
        filetypes=[
            ("Text Files", "*.txt"),
            ("All Files", "*.*")
        ]
    )
    if not filepath:
        return
    try:
        with open(filepath, "r", encoding="utf-8") as input_file:
            content = input_file.read()
        new_tab(
            content=content,
            filepath=filepath
        )
    except Exception as error:
        messagebox.showerror(
            "Open Error",
            str(error)
        )


def open_folder():
    """Open every file in the selected folder, regardless of its extension."""
    folderpath = askdirectory(
        title="Select Folder to Open",
        parent=window
    )
    if not folderpath:
        return

    # Do not filter by extension: include .py, .html, .jpg, .pdf, and all
    # other files directly inside the selected folder. Subfolders are skipped.
    folder_files = sorted(
        filename for filename in os.listdir(folderpath)
        if os.path.isfile(os.path.join(folderpath, filename))
    )

    if not folder_files:
        messagebox.showinfo(
            "Open Folder",
            "This folder does not contain any files.",
            parent=window
        )
        return

    opened_count = 0
    errors = []
    for filename in folder_files:
        filepath = os.path.join(folderpath, filename)
        try:
            # Replacement characters allow files with non-UTF-8 encodings or
            # binary data to be loaded instead of being skipped due to decoding.
            with open(filepath, "r", encoding="utf-8", errors="replace") as input_file:
                content = input_file.read()
            new_tab(content=content, filepath=filepath)
            opened_count += 1
        except Exception as error:
            errors.append(f"{filename}: {error}")

    if errors:
        messagebox.showwarning(
            "Some Files Could Not Be Opened",
            f"Opened {opened_count} file(s).\n\n" + "\n".join(errors),
            parent=window
        )
# ---------- PART 8: SAVE FILE ----------
def save_letter():
    """Save the active document. Return True only when saving succeeds."""
    if current_document is None:
        return False

    state = get_state()
    editor = get_editor()
    filepath = state["filepath"]

    if not filepath:
        filepath = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )
        # The user cancelled the Save As dialog.
        if not filepath:
            return False

        state["filepath"] = filepath
        state["name"] = os.path.basename(filepath)
        update_tab_name()

    try:
        with open(filepath, "w", encoding="utf-8") as output_file:
            output_file.write(editor.get("1.0", "end-1c"))

        update_title()
        messagebox.showinfo(
            "Saved",
            "File saved successfully!",
            parent=window
        )
        return True

    except Exception as error:
        messagebox.showerror(
            "Save Error",
            str(error),
            parent=window
        )
        return False


# ---------- PART 8B: CONFIRM BEFORE EXITING ----------
def confirm_application_close():
    """Ask what to do with the currently selected document before exiting."""
    if current_document is None:
        window.destroy()
        return

    close_dialog = Toplevel(window)
    close_dialog.title("Close YANTRA Bhasha")
    close_dialog.resizable(False, False)
    close_dialog.transient(window)
    close_dialog.configure(background=app_theme["bg"])

    # Keep the dialog centered over the main application window.
    close_dialog.update_idletasks()
    dialog_width = 390
    dialog_height = 165
    x = window.winfo_rootx() + (window.winfo_width() - dialog_width) // 2
    y = window.winfo_rooty() + (window.winfo_height() - dialog_height) // 2
    close_dialog.geometry(f"{dialog_width}x{dialog_height}+{max(x, 0)}+{max(y, 0)}")

    Label(
        close_dialog,
        text="Do you want to save file before closing?",
        font=("Arial", 11, "bold"),
        background=app_theme["bg"],
        foreground=app_theme["fg"]
    ).pack(padx=18, pady=(24, 22))

    button_frame = Frame(close_dialog, background=app_theme["bg"])
    button_frame.pack(pady=(0, 18))

    def save_and_close():
        # If Save As is cancelled or saving fails, leave the application open.
        if save_letter():
            close_dialog.destroy()
            window.destroy()

    def discard_and_close():
        close_dialog.destroy()
        window.destroy()

    def keep_application_open():
        close_dialog.destroy()

    Button(
        button_frame,
        text="Save",
        width=12,
        command=save_and_close
    ).pack(side=LEFT, padx=5)

    Button(
        button_frame,
        text="Do Not Save",
        width=12,
        command=discard_and_close
    ).pack(side=LEFT, padx=5)

    Button(
        button_frame,
        text="Keep Open",
        width=12,
        command=keep_application_open
    ).pack(side=LEFT, padx=5)

    # Clicking the dialog's X is the same as choosing Keep Open.
    close_dialog.protocol("WM_DELETE_WINDOW", keep_application_open)
    close_dialog.grab_set()
    close_dialog.focus_set()
# ---------- PART 9: UPDATE TAB NAME ----------
def update_tab_name():
    if current_document is None:
        return
    state = get_state()
    index = list(documents.keys()).index(current_document)
    tab_list.delete(index)
    tab_list.insert(index, state["name"])
    tab_list.selection_clear(0, END)
    tab_list.selection_set(index)
# ---------- PART 10: CLOSE TAB ----------
def close_tab():
    global current_document
    if current_document is None:
        return
    index = list(documents.keys()).index(current_document)
    editor = get_editor()
    editor.destroy()
    del documents[current_document]
    tab_list.delete(index)
    if documents:
        new_index = min(index, len(documents) - 1)
        tab_list.selection_set(new_index)
        switch_tab()
    else:
        current_document = None
        update_title()
# ---------- PART 11: CHANGE FONT ----------
def change_font():
    if current_document is None:
        return
    state = get_state()
    editor = get_editor()
    font_window = Toplevel(window)
    font_window.title("Change Font")
    font_window.geometry("400x470")
    font_window.resizable(False, False)
    installed_fonts = sorted(set(tkFont.families(window)))
    family_var = StringVar(value=state["family"])
    size_var = StringVar(value=str(state["size"]))
    color_var = StringVar(value=state["color"])
    bold_var = BooleanVar(value=state["bold"])
    italic_var = BooleanVar(value=state["italic"])
    underline_var = BooleanVar(value=state["underline"])
    Label(font_window, text="Font Family:").pack(pady=5)
    ttk.Combobox(
        font_window,
        textvariable=family_var,
        values=installed_fonts,
        state="readonly",
        width=35
    ).pack()
    Label(font_window, text="Font Size:").pack(pady=5)
    Spinbox(
        font_window,
        from_=6,
        to=96,
        textvariable=size_var
    ).pack()
    Label(font_window, text="Font Colour:").pack(pady=8)
    color_frame = Frame(font_window)
    color_frame.pack()
    preview = Label(
        color_frame,
        text="       ",
        bg=state["color"],
        relief=SOLID
    )
    preview.pack(side=LEFT, padx=5)
    def choose_color():
        selected = colorchooser.askcolor(
            color=color_var.get(),
            parent=font_window,
            title="Choose Font Colour"
        )
        if selected[1]:
            color_var.set(selected[1])
            preview.config(bg=selected[1])
    Button(
        color_frame,
        text="Choose Colour",
        command=choose_color
    ).pack(side=LEFT)
    Label(font_window, text="Text Style:").pack(pady=10)
    Checkbutton(
        font_window,
        text="Bold",
        variable=bold_var
    ).pack()
    Checkbutton(
        font_window,
        text="Italic",
        variable=italic_var
    ).pack()
    Checkbutton(
        font_window,
        text="Underline",
        variable=underline_var
    ).pack()
    def apply_font():
        try:
            size = int(size_var.get())
            if not 6 <= size <= 96:
                raise ValueError
            state["family"] = family_var.get()
            state["size"] = size
            state["color"] = color_var.get()
            state["bold"] = bold_var.get()
            state["italic"] = italic_var.get()
            state["underline"] = underline_var.get()
            selected_font = tkFont.Font(
                family=state["family"],
                size=state["size"],
                weight="bold" if state["bold"] else "normal",
                slant="italic" if state["italic"] else "roman",
                underline=state["underline"]
            )
            tag_name = "format_" + str(state["tag_counter"])
            state["tag_counter"] += 1
            state["fonts"][tag_name] = selected_font
            state["font"].configure(
                family=state["family"],
                size=state["size"]
            )
            editor.tag_configure(
                tag_name,
                font=selected_font,
                foreground=state["color"]
            )
            # Keep the latest formatting tag above older formatting tags.
            editor.tag_raise(tag_name)

            # Apply to selected text
            try:
                start = editor.index(SEL_FIRST)
                end = editor.index(SEL_LAST)
                editor.tag_add(tag_name, start, end)
            except TclError:
                pass
            # Apply to newly typed text
            state["active_tag"] = tag_name
            editor.focus_set()
            font_window.destroy()
        except ValueError:
            messagebox.showerror(
                "Invalid Size",
                "Enter a font size between 6 and 96.",
                parent=font_window
            )
    Button(
        font_window,
        text="Apply Formatting",
        command=apply_font,
        bg="#2563EB",
        fg="white",
        font=("Arial", 11, "bold")
    ).pack(pady=20)
# ---------- PART 12: AUTOMATIC TEXT FORMATTING ----------
def remember_typing_position(event, editor):
    state = documents.get(
        next(
            (key for key, value in documents.items()
             if value["editor"] == editor),
            None
        )
    )
    if not state or not state["active_tag"]:
        return
    if not event.char:
        return
    if not event.char.isprintable():
        return
    try:
        start = editor.index(SEL_FIRST)
    except TclError:
        start = editor.index(INSERT)
    tag_name = state["active_tag"]
    editor.after_idle(
        lambda e=editor, s=start, t=tag_name:
        apply_typing_format(e, s, t)
    )
def apply_typing_format(editor, start, tag_name):
    try:
        end = editor.index(INSERT)
        if editor.compare(end, ">", start):
            editor.tag_add(
                tag_name,
                start,
                end
            )
            editor.tag_raise(tag_name)
    except TclError:
        pass
# ---------- PART 13: WINDOWS CLIPBOARD IMAGE SUPPORT ----------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
CF_DIB = 8
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
# ---------- PART 14: CONVERT DIB TO PPM ----------
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
        row = dib[
            offset + source_y * stride:
            offset + (source_y + 1) * stride
        ]
        for x in range(width):
            index = x * (bits // 8)
            b, g, r = row[index:index + 3]
            pixels.extend((r, g, b))
    return (
        f"P6\n{width} {height_abs}\n255\n".encode()
        + bytes(pixels)
    )
# ---------- PART 15: PASTE IMAGE ----------
def paste_image(event=None):
    editor = get_editor()
    if editor is None:
        return "break"
    state = get_state()
    try:
        dib = clipboard_image()
        if not dib:
            return None
        ppm_data = dib_to_ppm(dib)
        photo = PhotoImage(
            data=ppm_data,
            format="PPM"
        )
        max_width = 700
        max_height = 700
        scale = max(
            1,
            (photo.width() + max_width - 1) // max_width,
            (photo.height() + max_height - 1) // max_height
        )
        if scale > 1:
            photo = photo.subsample(scale, scale)
        # Each document stores its own images
        state["images"].append(photo)
        editor.image_create(
            INSERT,
            image=photo
        )
        editor.insert(INSERT, "\n")
        return "break"
    except Exception as error:
        messagebox.showerror(
            "Image Error",
            str(error)
        )
        return "break"
# ---------- PART 16: MAIN BUTTONS ----------
btn_open = Button(
    fr_buttons if False else window,
    text="Open",
    command=open_letter
)
btn_save = Button(
    window,
    text="Save file As...",
    command=save_letter
)
btn_font = Button(
    window,
    text="Change Font",
    command=change_font
)
btn_background = Button(
    window,
    text="Change Background",
    command=change_background
)
# ---------- PART 17: LEFT PANEL ----------
fr_buttons = Frame(
    window,
    relief=RAISED,
    bd=2
)
# Move the original buttons into the left panel
btn_open.master = fr_buttons
btn_save.master = fr_buttons
btn_font.master = fr_buttons
btn_background.master = fr_buttons
# Recreate buttons correctly in the panel
btn_open.destroy()
btn_save.destroy()
btn_font.destroy()
btn_background.destroy()
btn_open = Menubutton(
    fr_buttons,
    text="Open",
    relief=RAISED,
    direction="below"
)
open_menu = Menu(btn_open, tearoff=0)
open_menu.add_command(
    label="Open File...",
    command=open_letter
)
open_menu.add_command(
    label="Open Folder...",
    command=open_folder
)
btn_open.configure(menu=open_menu)
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
btn_background = Button(
    fr_buttons,
    text="Change Background",
    command=change_background
)
# ---------- PART 18: VERTICAL DOCUMENT TABS ----------
Label(
    fr_buttons,
    text="Documents",
    font=("Arial", 10, "bold")
).grid(
    row=4,
    column=0,
    sticky="w",
    padx=5,
    pady=(15, 5)
)
tab_frame = Frame(fr_buttons)
tab_frame.grid(
    row=5,
    column=0,
    sticky="nsew",
    padx=5,
    pady=5
)
fr_buttons.rowconfigure(5, weight=1)
fr_buttons.columnconfigure(0, weight=1)
tab_scrollbar = Scrollbar(
    tab_frame,
    orient=VERTICAL
)
tab_list = Listbox(
    tab_frame,
    width=22,
    height=15,
    exportselection=False,
    activestyle="dotbox",
    yscrollcommand=tab_scrollbar.set
)
tab_scrollbar.config(
    command=tab_list.yview
)
# Arrange the document list, close button, and scrollbar side by side.
tab_frame.rowconfigure(0, weight=1)
tab_frame.columnconfigure(0, weight=1)
tab_list.grid(
    row=0,
    column=0,
    sticky="nsew"
)
# Close the currently selected document.
btn_close_tab = Button(
    tab_frame,
    text="X",
    width=3,
    command=close_tab
)
btn_close_tab.grid(
    row=0,
    column=1,
    sticky="n",
    padx=(5, 0)
)
tab_scrollbar.grid(
    row=0,
    column=2,
    sticky="ns"
)
tab_list.bind(
    "<<ListboxSelect>>",
    switch_tab
)
# ---------- PART 19: RIGHT CLICK TAB MENU ----------
tab_menu = Menu(
    window,
    tearoff=0
)
tab_menu.add_command(
    label="New Document",
    command=lambda: new_tab()
)
tab_menu.add_command(
    label="Close Selected Document",
    command=close_tab
)
def show_tab_menu(event):
    index = tab_list.nearest(event.y)
    if index >= 0:
        tab_list.selection_clear(0, END)
        tab_list.selection_set(index)
        switch_tab()
        tab_menu.tk_popup(
            event.x_root,
            event.y_root
        )
tab_list.bind(
    "<Button-3>",
    show_tab_menu
)
# ---------- PART 20: LAYOUT ----------
btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
btn_font.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
btn_background.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
fr_buttons.grid(
    row=0,
    column=0,
    sticky="ns"
)
editor_frame = Frame(window)
editor_frame.grid(
    row=0,
    column=1,
    sticky="nsew"
)
editor_frame.rowconfigure(0, weight=1)
editor_frame.columnconfigure(0, weight=1)
# ---------- PART 21: KEYBOARD SHORTCUTS ----------
window.bind(
    "<Control-n>",
    lambda event: new_tab()
)
window.bind(
    "<Control-N>",
    lambda event: new_tab()
)
window.bind(
    "<Control-w>",
    lambda event: close_tab()
)
window.bind(
    "<Control-W>",
    lambda event: close_tab()
)
# ---------- PART 22: START APPLICATION ----------
apply_app_theme(APP_THEMES["light"])
new_tab()

# Show the Save / Do Not Save / Keep Open dialog for the title-bar X and Alt+F4.
window.protocol("WM_DELETE_WINDOW", confirm_application_close)

window.mainloop()
