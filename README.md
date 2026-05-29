# 📝 SnipText Pro Workspace

A modern, fast, and feature-rich tabbed text editor and IDE helper built with Python and Tkinter. Designed for developers and writers who need a clean, distraction-free environment with workspace-level file explorer support, Python syntax highlighting, automatic saving, and theme customization.

---

## 🌟 Key Features

*   **🗂️ Tabbed Workspace Canvas**: Open and edit multiple files concurrently in a clean, tabbed panel layout.
*   **📁 Workspace Explorer Sidebar**: Easily browse and double-click to open files within your designated active folder. Runtime editor applications and binary dependencies are filtered out automatically.
*   **🌓 Dual Themes (Light & Dark)**: Toggle seamlessly between two beautiful, hand-curated themes (Notepad Pro Palette):
    *   *Light Theme*: Crisp pristine white canvas with professional blue accents.
    *   *Dark Theme*: Deep Obsidian black canvas with modern emerald-green accents.
*   **💾 Auto-Save Engine**: Runs quietly in the background, auto-saving your active file edits every 300 seconds (5 minutes) so you never lose your progress.
*   **🐍 Python Syntax Highlighting**: Real-time keyword parsing that colorizes Python keywords utilizing Python's built-in `keyword` library.
*   **🔍 Interactive Find Tool**: Scan and highlight every matching query occurrence within the active file using the accent color of the theme.
*   **🕒 Time & Date Stamp**: Instantly insert a timestamp (`YYYY-MM-DD HH:MM:SS`) at your cursor position with a single click.
*   **📍 Precision Status Bar**: Real-time caret position tracking (`Line X, Column Y`) at the bottom of the editor.
*   **🖱️ Custom Context Menu**: Quick right-click access to standard actions like Cut, Copy, Paste, and Find.

---

## 🛠️ How It Works (Technical Architecture)

`SnipText Pro` is engineered with clean, modular blocks using Python's native GUI framework, **Tkinter**, requiring zero third-party dependencies.

1.  **GUI Core (`tkinter` & `ttk`)**:
    *   The layout is structured using a top `Frame` for the toolbar controls, a left `Frame` for the directory list, and a central `ttk.Notebook` container for multi-tab management.
    *   Dynamic styles are applied via `ttk.Style` to customize notebook tabs and borders to match the selected theme.
2.  **State Management**:
    *   `current_file_paths`: A dictionary linking individual notebook tab instances to their absolute local file paths on disk.
    *   `current_workspace_dir`: Remembers the current active directory path to keep the Workspace Explorer populated.
3.  **Background Auto-Save**:
    *   Implements an asynchronous non-blocking loop utilizing Tkinter's `.after()` handler to regularly inspect modified states and save changes to disk safely without interrupting typing.
4.  **Modified Flags & Warnings**:
    *   Uses Tkinter's native `edit_modified()` property to detect changes in text widgets. When you attempt to close a modified tab (by double-clicking), the app prompts you to save changes.

---

## ⚙️ Theme Palette Specifications

| Token | Light Mode Color | Dark Mode Color | Description |
| :--- | :--- | :--- | :--- |
| **Workspace Base** | `#f0f0f0` | `#202020` | Frame structure background |
| **Widget Canvas** | `#ffffff` | `#111111` | Text editing area background |
| **Separators/Borders**| `#dcdcdc` | `#333333` | Panel outline borders |
| **Main Text** | `#000000` | `#e0e0e0` | Editor content text color |
| **Muted Text** | `#555555` | `#888888` | Status bar and descriptive text |
| **Theme Accent** | `#007acc` | `#107c41` | Caret highlighting & search focus |
| **Caret Insertion** | `#000000` | `#ffffff` | Blinking cursor point |
| **Syntax Keyword** | `#0000ff` | `#569cd6` | Highlighted syntax color |

---

## 🚀 Getting Started

### Prerequisites

Since SnipText Pro relies entirely on the Python Standard Library, there are **no external packages** to install. You only need Python 3.x.

#### Windows
Python installations on Windows include Tkinter by default.

#### macOS
If not already installed, you can install Python and Tkinter via Homebrew:
```bash
brew install python
```

#### Linux (Debian/Ubuntu)
Install Tkinter alongside Python:
```bash
sudo apt-get install python3-tk
```

---

### How to Run

Clone or download the project directory, open your terminal/command prompt inside the folder, and execute:

```bash
python SnipText_Pro.py
```

---

### 📦 Compiling to a Standalone Executable (.exe)

This project is configured with a PyInstaller `.spec` configuration file (`SnipTextPro.spec`), allowing you to compile it into a single, standalone executable for Windows.

1.  First, install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Build the project using the preconfigured spec file:
    ```bash
    pyinstaller SnipTextPro.spec
    ```
3.  Once the build is complete, you will find the standalone executable in the `dist` directory. (Note: PyInstaller will build intermediates in the `build` directory, and output the compiled bundle to `dist`).

---

## 🎹 Navigation & Controls

*   **Open Workspace Folder**: Click `📁 Open Workspace Folder` at the top of the sidebar.
*   **Open a File**: Double-click any file in the Sidebar Explorer, or click `📂 Open File` on the toolbar.
*   **Close a Tab**: Double-click the tab's header in the tab bar.
*   **Right-Click Menu**: Access Cut, Copy, Paste, and Find tools directly within the editor.
*   **Highlight Search Word**: Click `🔍 Find` on the toolbar (or in the context menu), type your word, and click **Find All**. Click anywhere inside the document to clear highlighting.
