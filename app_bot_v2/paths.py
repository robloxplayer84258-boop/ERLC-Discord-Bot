import os
import sys
import shutil

APP_DIR = os.path.expanduser("~/Library/Application Support/ERLCBot")
os.makedirs(APP_DIR, exist_ok=True)

def get_bundled_path(filename):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)

def get_data_path(filename):
    target = os.path.join(APP_DIR, filename)
    if not os.path.exists(target):
        bundled = get_bundled_path(filename)
        if os.path.exists(bundled):
            shutil.copy2(bundled, target)
        elif filename == ".env":
            open(target, "a").close()
    return target
