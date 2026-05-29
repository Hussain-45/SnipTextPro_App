import tkinter as tk
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from datetime import datetime
import keyword

# -------------------------- Notepad Pro Palette -------------------------- #
THEMES = {
    "light": {
        "bg_base": "#f0f0f0",       # Main frame layout color
        "bg_widget": "#ffffff",     # Notepad pristine white canvas
        "border": "#dcdcdc",        # Clean thin separator borders
        "fg_main": "#000000",       # Sharp black system text
        "fg_muted": "#555555",      # Gray status/sidebar details
        "accent": "#007acc",        # Classic focus blue
        "insert": "#000000",        # Black caret insertion point
        "kw_color": "#0000ff"       # Traditional IDE Royal Blue keywords
    },
    "dark": {
        "bg_base": "#202020",       # Frame layout background
        "bg_widget": "#111111",     # Deep Obsidian Black canvas
        "border": "#333333",        # Stealth dark borders
        "fg_main": "#e0e0e0",       # Off-white readability text
        "fg_muted": "#888888",      # Charcoal commentary text
        "accent": "#107c41",        # Dark accent highlight 
        "insert": "#ffffff",        # High visibility white caret
        "kw_color": "#569cd6"       # Modern crisp ice-blue keywords
    }
}

current_theme = "light"
current_file_paths = {}
current_workspace_dir = os.path.abspath(".")  # Tracks active workspace absolute path
auto_save_interval = 300  # seconds

# ---------------------------- Root Window ---------------------------- #
root = tk.Tk()
root.title("SnipText Pro Workspace")
root.geometry("1150x750")
root.configure(bg=THEMES[current_theme]["bg_base"])

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=THEMES[current_theme]["bg_base"], borderwidth=0)
style.configure("TNotebook.Tab", 
                background=THEMES[current_theme]["bg_base"], 
                foreground=THEMES[current_theme]["fg_main"], 
                padding=[12, 4], 
                font=("Segoe UI", 9),
                borderwidth=1,
                lightcolor=THEMES[current_theme]["border"],
                darkcolor=THEMES[current_theme]["border"])
style.map("TNotebook.Tab", 
          background=[("selected", THEMES[current_theme]["bg_widget"])], 
          foreground=[("selected", THEMES[current_theme]["fg_main"])])

# ---------------------------- Core System Helpers ---------------------------- #
def get_current_text():
    try:
        current_tab = tab_control.select()
        if current_tab:
            return tab_control.nametowidget(current_tab).text_area
        return None
    except Exception:
        return None

# ---------------------------- Close Tab Logic ---------------------------- #
def close_tab(event):
    try:
        clicked_tab = tab_control.tk.call(tab_control._w, "identify", "tab", event.x, event.y)
        if clicked_tab == "": 
            return 
            
        tab_id = tab_control.tabs()[clicked_tab]
        frame = tab_control.nametowidget(tab_id)
        text_area = frame.text_area
        
        if text_area.edit_modified():
            path = current_file_paths.get(str(tab_id))
            file_name = os.path.basename(path) if path else "Untitled"
            
            choice = messagebox.askyesnocancel(
                "Save Changes?", 
                f"Do you want to save changes to {file_name} before closing?"
            )
            
            if choice is True: 
                save_file(specific_tab=tab_id)
            elif choice is False: 
                pass 
            else: 
                return 

        if str(tab_id) in current_file_paths:
            del current_file_paths[str(tab_id)]
        tab_control.forget(tab_id)
        
        if not tab_control.tabs():
            new_tab()
    except Exception:
        pass

# ---------------------------- Auto-Save Feature ---------------------------- #
def auto_save():
    for tab_id in tab_control.tabs():
        path = current_file_paths.get(str(tab_id))
        if path:
            try:
                text_widget = tab_control.nametowidget(tab_id).text_area
                content = text_widget.get("1.0", END)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                text_widget.edit_modified(False) 
            except Exception:
                pass
    root.after(auto_save_interval * 1000, auto_save)

# ---------------------------- Top Toolbar ---------------------------- #
toolbar = Frame(root, bg=THEMES[current_theme]["bg_base"], padx=5, pady=4)
toolbar.pack(side=TOP, fill=X)

def toolbar_button(icon_text, command):
    t = THEMES[current_theme]
    btn = Button(
        toolbar, text=icon_text, command=command, relief=FLAT,
        bg=t["bg_base"], fg=t["fg_main"], 
        activebackground=t["border"], activeforeground=t["fg_main"],
        font=("Segoe UI", 9), bd=1, highlightthickness=0,
        padx=8, pady=3
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=THEMES[current_theme]["border"]))
    btn.bind("<Leave>", lambda e: btn.config(bg=THEMES[current_theme]["bg_base"]))
    return btn

toolbar_button("📄 New", lambda: new_tab()).pack(side=LEFT, padx=2)
toolbar_button("📂 Open File", lambda: open_file()).pack(side=LEFT, padx=2)
toolbar_button("💾 Save", lambda: save_file()).pack(side=LEFT, padx=2)
toolbar_button("✂️ Cut", lambda: cut()).pack(side=LEFT, padx=2)
toolbar_button("📋 Copy", lambda: copy()).pack(side=LEFT, padx=2)
toolbar_button("📝 Paste", lambda: paste()).pack(side=LEFT, padx=2)
toolbar_button("🔍 Find", lambda: find_text()).pack(side=LEFT, padx=2)
toolbar_button("🕒 Time", lambda: insert_datetime()).pack(side=LEFT, padx=2)

theme_btn = toolbar_button("🌓 Theme", lambda: toggle_theme())
theme_btn.pack(side=RIGHT, padx=5)

# ------------------------- Workspace Explorer Sidebar ------------------------- #
sidebar = Frame(root, width=220, bg=THEMES[current_theme]["bg_base"], bd=0)
sidebar.pack(side=LEFT, fill=Y, padx=5, pady=5)

open_dir_btn = Button(
    sidebar, text="📁 Open Workspace Folder", command=lambda: change_workspace(),
    relief=GROOVE, bg=THEMES[current_theme]["bg_widget"], fg=THEMES[current_theme]["fg_main"],
    font=("Segoe UI", 9), bd=1, padx=5, pady=4
)
open_dir_btn.pack(fill=X, padx=2, pady=(2, 5))

file_listbox = Listbox(
    sidebar, bg=THEMES[current_theme]["bg_widget"], fg=THEMES[current_theme]["fg_main"],
    selectbackground=THEMES[current_theme]["border"], selectforeground=THEMES[current_theme]["fg_main"],
    relief=SOLID, bd=1, highlightthickness=0, font=("Segoe UI", 10), activestyle="none"
)
file_listbox.pack(fill=BOTH, expand=1, padx=2, pady=2)

def populate_file_list():
    file_listbox.delete(0, END)
    try:
        abs_path = os.path.abspath(current_workspace_dir)
        if not os.path.exists(abs_path):
            file_listbox.insert(END, " (Folder does not exist) ")
            return

        files = os.listdir(abs_path)
        
        valid_files = []
        for f in files:
            full_item_path = os.path.join(abs_path, f)
            # Skip directories to focus on opening core target text sheets
            if os.path.isdir(full_item_path):
                continue
            # Hide runtime editor application background binaries/scripts
            if f in ["SnipText-Pro.py", "SnipText_Pro.py", "main.py"]:
                continue
            valid_files.append(f)
        
        if not valid_files:
            file_listbox.insert(END, " (No files in this folder) ")
        else:
            for file in valid_files:
                file_listbox.insert(END, f" 📄 {file}")
    except Exception as e:
        file_listbox.insert(END, " (Failed to read folder) ")

def change_workspace():
    global current_workspace_dir
    chosen_dir = filedialog.askdirectory()
    if chosen_dir:
        current_workspace_dir = chosen_dir
        populate_file_list()

def open_selected_file():
    selection = file_listbox.curselection()
    if selection:
        item_text = file_listbox.get(selection[0])
        # Defensive catch if clicking helper messaging placeholders
        if item_text.startswith(" ("):
            return
        filename = item_text.replace(" 📄 ", "").strip()
        full_path = os.path.join(current_workspace_dir, filename)
        open_path(os.path.abspath(full_path))

file_listbox.bind("<Double-Button-1>", lambda e: open_selected_file())
populate_file_list()

# ---------------------------- File Handlers ---------------------------- #
def open_path(path):
    if os.path.isfile(path):
        for id_check in tab_control.tabs():
            if current_file_paths.get(str(id_check)) == path:
                tab_control.select(id_check)
                return

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        add_tab_with_close(os.path.basename(path), path)
        txt = get_current_text()
        if txt:
            txt.insert(1.0, content)
            highlight_syntax(txt)
            txt.edit_modified(False)

# ---------------------------- Notebook Workspace Canvas ---------------------------- #
tab_control = ttk.Notebook(root)
tab_control.pack(expand=1, fill="both", padx=5, pady=5)
tab_control.bind("<Double-Button-1>", close_tab)

def add_tab_with_close(title, path=None):
    t = THEMES[current_theme]
    frame = Frame(tab_control, bg=t["bg_base"])
    
    text_area = scrolledtext.ScrolledText(
        frame, wrap=WORD, undo=True, font=("Consolas", 12),
        bg=t["bg_widget"], fg=t["fg_main"], 
        insertbackground=t["insert"], relief=SOLID, bd=1,
        highlightthickness=0, padx=8, pady=8
    )
    text_area.pack(expand=1, fill=BOTH)
    frame.text_area = text_area
    
    tab_control.add(frame, text=f" {title} ")
    tab_control.select(frame)
    current_file_paths[str(frame)] = path
    
    text_area.bind("<KeyRelease>", lambda e: [highlight_syntax(text_area), update_status()])
    text_area.bind("<Button-3>", lambda e: show_context_menu(e, text_area))

def new_tab():
    add_tab_with_close("Untitled")

# ---------------------------- Bottom Status Bar ---------------------------- #
status_bar = Frame(root, bg=THEMES[current_theme]["bg_base"], bd=1, relief=FLAT)
status_bar.pack(side=BOTTOM, fill=X, padx=5, pady=2)

status_label = Label(status_bar, text="Line 1, Column 1", anchor=W, bg=THEMES[current_theme]["bg_base"], fg=THEMES[current_theme]["fg_muted"], font=("Segoe UI", 9))
status_label.pack(side=LEFT)

def update_status(event=None):
    text = get_current_text()
    if text:
        line, col = text.index(INSERT).split('.')
        status_label.config(text=f"Line {line}, Column {int(col)+1}")

# ---------------------------- Engine Logic ---------------------------- #
def highlight_syntax(text):
    text.tag_remove("keyword", "1.0", END)
    text.tag_config("keyword", foreground=THEMES[current_theme]["kw_color"])
    for kw in keyword.kwlist:
        start = "1.0"
        while True:
            start = text.search(rf'\b{kw}\b', start, stopindex=END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(kw)}c"
            text.tag_add("keyword", start, end)
            start = end

def show_context_menu(event, widget):
    context_menu = Menu(root, tearoff=0, bg=THEMES[current_theme]["bg_widget"], fg=THEMES[current_theme]["fg_main"], activebackground=THEMES[current_theme]["border"])
    context_menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
    context_menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
    context_menu.add_command(label="Paste", command=lambda: widget.event_generate("<<Paste>>"))
    context_menu.add_separator()
    context_menu.add_command(label="Find", command=find_text)
    context_menu.tk_popup(event.x_root, event.y_root)

# ---------------------------- Theme Engine Switcher ---------------------------- #
def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    t = THEMES[current_theme]
    
    root.configure(bg=t["bg_base"])
    toolbar.configure(bg=t["bg_base"])
    sidebar.configure(bg=t["bg_base"])
    file_listbox.configure(bg=t["bg_widget"], fg=t["fg_main"], selectbackground=t["border"], selectforeground=t["fg_main"])
    open_dir_btn.configure(bg=t["bg_widget"], fg=t["fg_main"], activebackground=t["border"])
    status_bar.configure(bg=t["bg_base"])
    status_label.configure(bg=t["bg_base"], fg=t["fg_muted"])
    
    for btn in toolbar.winfo_children():
        if isinstance(btn, Button):
            btn.configure(bg=t["bg_base"], fg=t["fg_main"], activebackground=t["border"], activeforeground=t["fg_main"])
            
    style.configure("TNotebook", background=t["bg_base"])
    style.configure("TNotebook.Tab", background=t["bg_base"], foreground=t["fg_main"], lightcolor=t["border"], darkcolor=t["border"])
    style.map("TNotebook.Tab", background=[("selected", t["bg_widget"])], foreground=[("selected", t["fg_main"])])
    
    for tab_id in tab_control.tabs():
        pane = tab_control.nametowidget(tab_id)
        pane.configure(bg=t["bg_base"])
        pane.text_area.configure(bg=t["bg_widget"], fg=t["fg_main"], insertbackground=t["insert"])
        highlight_syntax(pane.text_area)

# ---------------------------- Core Tool Functions ---------------------------- #
def open_file():
    path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("Python Files", "*.py"), ("All Files", "*.*")])
    if path:
        open_path(path)

def save_file(specific_tab=None):
    target_tab = specific_tab if specific_tab else tab_control.select()
    if not target_tab: return
    
    text_widget = tab_control.nametowidget(target_tab).text_area
    path = current_file_paths.get(str(target_tab))
    
    if not path:
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    
    if path:
        try:
            content = text_widget.get(1.0, END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            current_file_paths[str(target_tab)] = path
            tab_control.tab(target_tab, text=f" {os.path.basename(path)} ")
            text_widget.edit_modified(False) 
            populate_file_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

def cut(): 
    txt = get_current_text()
    if txt: txt.event_generate("<<Cut>>")

def copy(): 
    txt = get_current_text()
    if txt: txt.event_generate("<<Copy>>")

def paste(): 
    txt = get_current_text()
    if txt: txt.event_generate("<<Paste>>")

def insert_datetime():
    txt = get_current_text()
    if txt:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        txt.insert(INSERT, now)

def find_text():
    text_widget = get_current_text()
    if not text_widget: return
    
    t = THEMES[current_theme]
    popup = Toplevel(root, bg=t["bg_base"], bd=1, relief=SOLID)
    popup.title("Find")
    popup.geometry("300x120")
    popup.resizable(False, False)
    
    Label(popup, text="Find:", bg=t["bg_base"], fg=t["fg_main"]).pack(pady=4)
    input_entry = Entry(popup, bg=t["bg_widget"], fg=t["fg_main"], insertbackground=t["insert"], bd=1, relief=SOLID)
    input_entry.pack(pady=5)
    input_entry.focus_set()
    
    def do_find():
        word = input_entry.get()
        text_widget.tag_remove('found', '1.0', END)
        if word:
            idx = '1.0'
            while True:
                idx = text_widget.search(word, idx, stopindex=END)
                if not idx: break
                lastidx = f"{idx}+{len(word)}c"
                text_widget.tag_add('found', idx, lastidx)
                idx = lastidx
            text_widget.tag_config('found', foreground='white', background=t["accent"])
            
    Button(popup, text="Find All", command=do_find, bg=t["bg_base"], fg=t["fg_main"], relief=SOLID, bd=1).pack(pady=4)

# ---------------------------- Start ---------------------------- #
new_tab()
auto_save()
root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()