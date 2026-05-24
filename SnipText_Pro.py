from ttkthemes import ThemedTk
import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext, font
import os
from datetime import datetime
import keyword
import json

# ---------------------------- Global Variables ---------------------------- #
current_file_paths = {}
dark_mode = False
custom_font = ("Consolas", 12)
auto_save_interval = 300  # seconds

# ---------------------------- Root Window ---------------------------- #
root = ThemedTk(theme="arc")
root.title("SnipText Pro")
root.geometry("1000x700")
root.configure(bg="#f0f0f0")

# ---------------------------- Auto-Save Feature ---------------------------- #
def auto_save():
    content = get_current_text().get(1.0, END)
    path = current_file_paths.get(str(tab_control.select()))
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    root.after(auto_save_interval * 1000, auto_save)

# ---------------------------- Top Toolbar ---------------------------- #
toolbar = Frame(root, bg="#e0e0e0")
toolbar.pack(side=TOP, fill=X)

def toolbar_button(icon_text, command):
    return Button(toolbar, text=icon_text, command=command, relief=FLAT, bg="#d0d0d0", font=("Segoe UI", 9))

toolbar_button("New", lambda: new_tab()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Open", lambda: open_file()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Save", lambda: save_file()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Cut", lambda: cut()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Copy", lambda: copy()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Paste", lambda: paste()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Find", lambda: find_text()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Date/Time", lambda: insert_datetime()).pack(side=LEFT, padx=2, pady=2)
toolbar_button("Dark Mode", lambda: toggle_dark_mode()).pack(side=LEFT, padx=2, pady=2)

# ---------------------------- Sidebar ---------------------------- #
sidebar = Frame(root, width=200, bg="#f7f7f7")
sidebar.pack(side=LEFT, fill=Y)
file_listbox = Listbox(sidebar, bg="#ffffff")
file_listbox.pack(fill=BOTH, expand=1, padx=5, pady=5)

def populate_file_list():
    file_listbox.delete(0, END)
    for file in os.listdir("."):
        if file.endswith(".txt") or file.endswith(".py"):
            file_listbox.insert(END, file)

file_listbox.bind("<Double-Button-1>", lambda e: open_selected_file())
populate_file_list()

# ---------------------------- File Open/Save Helpers ---------------------------- #
def open_selected_file():
    selection = file_listbox.curselection()
    if selection:
        filename = file_listbox.get(selection[0])
        open_path(filename)

def open_path(path):
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        add_tab_with_close(path)
        get_current_text().insert(1.0, content)

# ---------------------------- Tab Area ---------------------------- #
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both")

def add_tab_with_close(title):
    frame = Frame(tab_control)
    text_area = scrolledtext.ScrolledText(frame, wrap=WORD, undo=True, font=custom_font, bg="white", fg="black", insertbackground="black")
    text_area.pack(expand=1, fill=BOTH)
    frame.text_area = text_area
    tab_control.add(frame, text=title)
    tab_control.select(frame)
    current_file_paths[str(frame)] = None
    text_area.bind("<KeyRelease>", lambda e: [highlight_syntax(text_area), update_status()])
    text_area.bind("<Button-3>", lambda e: show_context_menu(e, text_area))

def new_tab():
    add_tab_with_close("Untitled")

# ---------------------------- Status Bar ---------------------------- #
status_bar = Label(root, text="Line 1, Column 1", anchor=W, bg="#e0e0e0")
status_bar.pack(side=BOTTOM, fill=X)

def update_status(event=None):
    try:
        text = get_current_text()
        line, col = text.index(INSERT).split('.')
        status_bar.config(text=f"Line {line}, Column {int(col)+1}")
    except:
        pass

# ---------------------------- Syntax Highlight ---------------------------- #
def highlight_syntax(text):
    text.tag_remove("keyword", "1.0", END)
    text.tag_config("keyword", foreground="blue")
    for kw in keyword.kwlist:
        start = "1.0"
        while True:
            start = text.search(rf'\m{kw}\M', start, stopindex=END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(kw)}c"
            text.tag_add("keyword", start, end)
            start = end

# ---------------------------- Context Menu ---------------------------- #
def show_context_menu(event, widget):
    context_menu = Menu(root, tearoff=0)
    context_menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    context_menu.add_command(label="Find", command=find_text)
    context_menu.tk_popup(event.x_root, event.y_root)

# ---------------------------- Utility Functions ---------------------------- #
def get_current_text():
    current_tab = tab_control.select()
    return tab_control.nametowidget(current_tab).text_area

def open_file():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
    if path:
        open_path(path)

def save_file():
    content = get_current_text().get(1.0, END)
    path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Saved", f"File saved to {path}")

def cut(): get_current_text().event_generate("<<Cut>>")
def copy(): get_current_text().event_generate("<<Copy>>")
def paste(): get_current_text().event_generate("<<Paste>>")

def insert_datetime():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    get_current_text().insert(INSERT, now)

def find_text():
    popup = Toplevel()
    popup.title("Find")
    popup.geometry("300x100")
    Label(popup, text="Find:").pack()
    input_entry = Entry(popup)
    input_entry.pack(pady=5)
    def do_find():
        word = input_entry.get()
        text = get_current_text()
        text.tag_remove('found', '1.0', END)
        if word:
            idx = '1.0'
            while True:
                idx = text.search(word, idx, stopindex=END)
                if not idx: break
                lastidx = f"{idx}+{len(word)}c"
                text.tag_add('found', idx, lastidx)
                idx = lastidx
            text.tag_config('found', foreground='white', background='orange')
    Button(popup, text="Find", command=do_find).pack()

# ---------------------------- Dark Mode ---------------------------- #
def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    bg = "#1e1e1e" if dark_mode else "#f0f0f0"
    fg = "white" if dark_mode else "black"
    tb_bg = "#2b2b2b" if dark_mode else "#e0e0e0"
    sb_bg = "#2b2b2b" if dark_mode else "#e0e0e0"
    sb_fg = "white" if dark_mode else "black"
    root.tk_setPalette(background=bg, foreground=fg)
    root.configure(bg=bg)
    toolbar.configure(bg=tb_bg)
    status_bar.configure(bg=sb_bg, fg=sb_fg)
    file_listbox.configure(bg=tb_bg, fg=fg)
    for widget in tab_control.winfo_children():
        widget.text_area.configure(bg=tb_bg, fg=fg, insertbackground=fg)

# ---------------------------- Menu Bar ---------------------------- #
menu_bar = Menu(root)

file_menu = Menu(menu_bar, tearoff=0)
file_menu.add_command(label="New", command=new_tab)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

edit_menu = Menu(menu_bar, tearoff=0)
edit_menu.add_command(label="Cut", command=cut)
edit_menu.add_command(label="Copy", command=copy)
edit_menu.add_command(label="Paste", command=paste)
edit_menu.add_command(label="Find", command=find_text)
edit_menu.add_command(label="Insert Date/Time", command=insert_datetime)
menu_bar.add_cascade(label="Edit", menu=edit_menu)

view_menu = Menu(menu_bar, tearoff=0)
view_menu.add_command(label="Toggle Dark Mode", command=toggle_dark_mode)
menu_bar.add_cascade(label="View", menu=view_menu)

help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "SnipText Pro\nVersion 2.0\nBy Team TechnoCreds"))
menu_bar.add_cascade(label="Help", menu=help_menu)

root.config(menu=menu_bar)

# ---------------------------- Init ---------------------------- #
new_tab()
auto_save()
root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()
# ---------------------------- End of SnipText-Pro.py ---------------------------- #
# This code is a complete text editor application with features like syntax highlighting, dark mode, auto-save, and a user-friendly interface.
# It supports multiple file types and provides a context menu for easy access to common actions.