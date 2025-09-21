import os
import shutil
import psutil
import re

# Forbidden system folders for safety
FORBIDDEN_FOLDERS = [
    "/", "/root", "/etc", "/bin", "/usr", "/lib", "/lib64", "/boot", "/dev", "/proc", "/sys", "/tmp"
]

CURRENT_DIR = os.getcwd()  # start at actual working directory

def ensure_base():
    # No sandbox creation needed; optional base folder for safety
    base = os.path.join(os.getcwd(), "workspace")
    os.makedirs(base, exist_ok=True)
    global CURRENT_DIR
    CURRENT_DIR = base

def safe_path(path=""):
    path = path.strip()
    target = os.path.abspath(os.path.join(CURRENT_DIR, path or ""))
    for forbidden in FORBIDDEN_FOLDERS:
        if target == forbidden or target.startswith(forbidden + os.sep):
            raise ValueError(f"Access to system folder blocked: {forbidden}")
    return target

def list_files(arg=""):
    p = safe_path(arg or ".")
    try:
        items = os.listdir(p)
        return "\n".join(sorted(items)) if items else "(empty directory)"
    except FileNotFoundError:
        return f"No such directory: {arg}"

def print_working_dir(_=None):
    return CURRENT_DIR

def change_dir(arg):
    arg = arg.strip()
    if not arg:
        return "Error: No directory specified."
    try:
        p = safe_path(arg)
        if not os.path.isdir(p):
            return f"No such directory: {arg}"
        global CURRENT_DIR
        CURRENT_DIR = p
        return f"Changed directory to {CURRENT_DIR}"
    except ValueError as e:
        return str(e)

def make_dir(arg):
    arg = arg.strip()
    if not arg:
        return "Error: No directory name specified."
    names = [a.strip() for a in re.split(r"[ ,]+", arg) if a.strip()]
    results = []
    for name in names:
        try:
            p = safe_path(name)
            if os.path.exists(p):
                results.append(f"Directory already exists: {name}")
            else:
                os.makedirs(p)
                results.append(f"Directory '{name}' created.")
        except ValueError as e:
            results.append(str(e))
    return "\n".join(results)

def touch_file(arg):
    arg = arg.strip()
    if not arg:
        return "Error: No filename specified."
    names = [a.strip() for a in re.split(r"[ ,]+", arg) if a.strip()]
    results = []
    for name in names:
        try:
            p = safe_path(name)
            if os.path.exists(p):
                results.append(f"File already exists: {name}")
            else:
                with open(p, "w", encoding="utf-8") as f:
                    f.write("")
                results.append(f"File '{name}' created.")
        except ValueError as e:
            results.append(str(e))
    return "\n".join(results)

def remove_file(arg):
    arg = arg.strip()
    if not arg:
        return "Error: No target specified for remove."
    targets = [a.strip() for a in re.split(r"[ ,]+", arg) if a.strip()]
    results = []
    for t in targets:
        try:
            p = safe_path(t)
            name = os.path.basename(p)
            if not os.path.exists(p):
                results.append(f"No such file or directory: {name}")
                continue
            if os.path.isdir(p):
                shutil.rmtree(p)
                results.append(f"Directory '{name}' removed.")
            else:
                os.remove(p)
                results.append(f"File '{name}' removed.")
        except ValueError as e:
            results.append(str(e))
    return "\n".join(results)

def read_file(arg):
    arg = arg.strip()
    if not arg:
        return "Error: No file specified."
    try:
        p = safe_path(arg)
        if not os.path.exists(p):
            return f"No such file: {arg}"
        if os.path.isdir(p):
            return f"'{arg}' is a directory, not a file."
        with open(p, "r", encoding="utf-8") as f:
            return f.read()
    except ValueError as e:
        return str(e)

def move_file(src, dest):
    src_list = [a.strip() for a in re.split(r"[ ,]+", src) if a.strip()]
    results = []
    try:
        dest_path = safe_path(dest)
        if not os.path.isdir(dest_path):
            return f"Destination folder does not exist: {dest}"
        for s in src_list:
            try:
                src_path = safe_path(s)
                if not os.path.exists(src_path):
                    results.append(f"No such file: {s}")
                    continue
                shutil.move(src_path, os.path.join(dest_path, os.path.basename(s)))
                results.append(f"Moved '{s}' to '{dest}'")
            except ValueError as e:
                results.append(str(e))
        return "\n".join(results)
    except ValueError as e:
        return str(e)

def cpu_usage(_=None):
    return f"CPU Usage: {psutil.cpu_percent(interval=0.5)}%"

def mem_usage(_=None):
    return f"Memory Usage: {psutil.virtual_memory().percent}%"

def list_processes(_=None):
    procs = []
    for proc in psutil.process_iter(['pid', 'name']):
        info = proc.info
        procs.append(f"{info.get('pid')}\t{info.get('name')}")
    return "\n".join(procs) if procs else "(no running processes)"
