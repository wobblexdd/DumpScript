import os
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


EXCLUDED_DIRS = {
    ".git", ".idea", ".vscode", "node_modules", "target", "build",
    "__pycache__", ".mvn", ".gradle", ".venv", "venv", "dist", "out"
}

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".ico",
    ".jar", ".class", ".exe", ".dll", ".so", ".dylib",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".mp3", ".wav", ".ogg", ".mp4", ".mov", ".avi", ".mkv",
    ".ttf", ".otf", ".woff", ".woff2"
}

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


def is_binary_file(path: Path) -> bool:
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True

    try:
        with path.open("rb") as f:
            chunk = f.read(4096)
        if b"\x00" in chunk:
            return True
    except Exception:
        return True

    return False


def should_skip_dir(dirname: str) -> bool:
    return dirname in EXCLUDED_DIRS


def build_tree(root_dir: Path) -> str:
    lines = [f"[{root_dir.name}/]"]

    def walk(current: Path, prefix: str = "    "):
        try:
            entries = sorted(
                current.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower())
            )
        except PermissionError:
            lines.append(f"{prefix}[ACCESS DENIED]")
            return
        except Exception as e:
            lines.append(f"{prefix}[ERROR: {e}]")
            return

        filtered = []
        for entry in entries:
            if entry.is_dir() and should_skip_dir(entry.name):
                continue
            filtered.append(entry)

        for entry in filtered:
            if entry.is_dir():
                lines.append(f"{prefix}[{entry.name}/]")
                walk(entry, prefix + "    ")
            else:
                relative = entry.relative_to(root_dir)
                lines.append(f"{prefix}{entry.name}    ->    {relative}")

    walk(root_dir)
    return "\n".join(lines)


def read_text_file(path: Path) -> str:
    try:
        size = path.stat().st_size
    except Exception as e:
        return f"[ERROR GETTING FILE SIZE: {e}]"

    if size > MAX_FILE_SIZE_BYTES:
        return f"[SKIPPED: file too large ({size} bytes)]"

    encodings_to_try = ["utf-8", "utf-8-sig", "cp1251", "latin-1"]

    for encoding in encodings_to_try:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except Exception as e:
            return f"[ERROR READING FILE: {e}]"

    return "[SKIPPED: could not decode file as text]"


def collect_all_files(root_dir: Path):
    result = []

    for current_root, dirs, files in os.walk(root_dir):
        dirs[:] = sorted([d for d in dirs if not should_skip_dir(d)], key=str.lower)
        files.sort(key=str.lower)

        current_path = Path(current_root)

        for filename in files:
            file_path = current_path / filename
            result.append(file_path)

    return result


def generate_dump(root_dir: Path) -> str:
    files = collect_all_files(root_dir)

    header = []
    header.append("=== FULL PROJECT PACK ===")
    header.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    header.append(f"Source directory: {root_dir}")
    header.append(f"Total files: {len(files)}")
    header.append("=" * 90)
    header.append("")
    header.append("--- DIRECTORY TREE ---")
    header.append(build_tree(root_dir))
    header.append("")
    header.append("=" * 90)
    header.append("")

    sections = []

    for file_path in files:
        relative = file_path.relative_to(root_dir)

        sections.append("#" * 90)
        sections.append(f"FILE: {relative}")
        sections.append(f"ABSOLUTE PATH: {file_path}")
        sections.append("#" * 90)
        sections.append("")

        if is_binary_file(file_path):
            sections.append("[BINARY FILE SKIPPED]")
        else:
            sections.append(read_text_file(file_path))

        sections.append("")
        sections.append("")

    return "\n".join(header + sections)


def choose_source_folder(root: tk.Tk):
    folder = filedialog.askdirectory(title="Select source folder to dump")
    return Path(folder) if folder else None


def choose_save_folder(root: tk.Tk):
    folder = filedialog.askdirectory(title="Select folder where dump .txt will be saved")
    return Path(folder) if folder else None


def ask_output_filename(root: tk.Tk):
    name = simpledialog.askstring(
        "Output file name",
        "Enter TXT file name (without .txt):",
        parent=root
    )

    if not name:
        return None

    invalid_chars = '<>:"/\\|?*'
    cleaned = "".join("_" if ch in invalid_chars else ch for ch in name).strip()

    if not cleaned:
        return None

    return cleaned + ".txt"


def main():
    root = tk.Tk()
    root.withdraw()
    root.update()

    try:
        source_folder = choose_source_folder(root)
        if not source_folder:
            messagebox.showinfo("Cancelled", "Source folder was not selected.")
            return

        save_folder = choose_save_folder(root)
        if not save_folder:
            messagebox.showinfo("Cancelled", "Save folder was not selected.")
            return

        output_filename = ask_output_filename(root)
        if not output_filename:
            messagebox.showinfo("Cancelled", "Output file name was not provided.")
            return

        output_path = save_folder / output_filename

        dump_text = generate_dump(source_folder)
        output_path.write_text(dump_text, encoding="utf-8")

        messagebox.showinfo(
            "Done",
            f"Dump created successfully.\n\nSaved to:\n{output_path}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Failed to create dump:\n\n{e}")
    finally:
        root.destroy()


if __name__ == "__main__":
    main()