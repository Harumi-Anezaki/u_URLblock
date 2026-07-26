"""
main.pyw

Main application entry point for the Time Keeper GUI and background watchdog.
Initializes DPI scaling, secures runtime directories, launches monitoring threads, and runs the CustomTkinter UI.
"""

import time
import os
import sys
import ctypes
import threading
import customtkinter as ctk
from typing import List, Tuple

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Embeddable Python environment setup for Tkinter
tcl_lib = os.path.join(os.path.dirname(sys.executable), "tcl", "tcl8.6")
tk_lib = os.path.join(os.path.dirname(sys.executable), "tcl", "tk8.6")
if os.path.exists(tcl_lib):
    os.environ["TCL_LIBRARY"] = tcl_lib
if os.path.exists(tk_lib):
    os.environ["TK_LIBRARY"] = tk_lib

lib_tcl_dir = os.path.join(os.path.dirname(sys.executable), "Lib", "tcl8.6")
if getattr(sys.flags, "ignore_environment", 0) and not os.path.exists(lib_tcl_dir):
    import shutil
    try:
        shutil.copytree(
            os.path.join(os.path.dirname(sys.executable), "tcl"),
            os.path.join(os.path.dirname(sys.executable), "Lib"),
            dirs_exist_ok=True
        )
    except Exception:
        pass

if sys.stdout is None:
    class DummyStream:
        def write(self, text: str) -> None: pass
        def flush(self) -> None: pass
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()

from win_utils import ensure_processes_running
from data_manager import load_config, FolderLocker, UsageManager, WRITABLE_DIR, ROOT_DIR
from ui import OverlayApp

PYTHON_BIN: str = os.path.join(ROOT_DIR, "bin")
TARGETS: List[Tuple[str, str]] = [
    ("main.pyw", os.path.join(PYTHON_BIN, "AudioDG_helper.exe")),
    ("watcher.pyw", os.path.join(PYTHON_BIN, "FontHost_worker.exe")),
    ("monitor.pyw", os.path.join(PYTHON_BIN, "SpoolerSub_helper.exe")),
    ("system_guard.pyw", os.path.join(PYTHON_BIN, "WinLogonAssist.exe")),
]
MY_FILENAME: str = "main.pyw"


def watchdog_loop() -> None:
    """
    Background daemon loop that periodically verifies all system security processes are actively running.
    """
    while True:
        try:
            ensure_processes_running(BASE_DIR, MY_FILENAME, TARGETS)
        except BaseException:
            pass
        time.sleep(0.5)


def main() -> None:
    """
    Main application controller. Sets up mutexes, DPI awareness, data managers, and GUI event loop.
    """
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Exe_Mutex_07")  # noqa: F841
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    # High-DPI scaling awareness for crisp text rendering on modern displays
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    locker = FolderLocker()  # noqa: F841
    config = load_config()
    manager = UsageManager(config)

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()

    app = OverlayApp(root, manager, config)  # noqa: F841

    t_watch = threading.Thread(target=watchdog_loop, daemon=True)
    t_watch.start()

    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        with open(os.path.join(WRITABLE_DIR, "error_log.txt"), "w", encoding='utf-8') as f:
            f.write(traceback.format_exc())
