"""
system_guard.pyw

WMI and Mutex-backed system guard process (disguised as WinLogonAssist.exe).
Monitors the execution state of all background helpers and respawns them if killed.
"""

import time
import subprocess
import os
import sys
import ctypes
from ctypes import wintypes
from typing import Set, Dict, List, Tuple, Any, Optional

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout is None:
    class DummyStream:
        def write(self, text: str) -> None: pass
        def flush(self) -> None: pass
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.dirname(sys.executable))
    ROOT_DIR: str = os.path.dirname(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
PYTHON_BIN: str = os.path.join(ROOT_DIR, "bin")
WRITABLE_DIR: str = os.path.join(ROOT_DIR, "authenticated_users_kakikomi_true")
os.makedirs(WRITABLE_DIR, exist_ok=True)

TARGETS: List[Tuple[str, List[str]]] = [
    ("AudioDG_helper.exe", [os.path.join(PYTHON_BIN, "AudioDG_helper.exe"), os.path.join(BASE_DIR, "main.pyw")]),
    ("FontHost_worker.exe", [os.path.join(PYTHON_BIN, "FontHost_worker.exe"), os.path.join(BASE_DIR, "watcher.pyw")]),
    ("SpoolerSub_helper.exe", [os.path.join(PYTHON_BIN, "SpoolerSub_helper.exe"), os.path.join(BASE_DIR, "monitor.pyw")]),
    ("WinLogonAssist.exe", [os.path.join(PYTHON_BIN, "WinLogonAssist.exe"), os.path.join(BASE_DIR, "system_guard.pyw")]),
]

MY_EXE_NAME: str = os.path.basename(sys.executable).lower()


def is_mutex_locked(mutex_name: str) -> bool:
    """
    Checks if a named Windows mutex is currently held by another running process.

    Args:
        mutex_name (str): The name of the mutex to check.

    Returns:
        bool: True if locked/held, False otherwise.
    """
    SYNCHRONIZE = 0x00100000
    handle = ctypes.windll.kernel32.OpenMutexW(SYNCHRONIZE, False, mutex_name)
    if handle:
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    return False


MUTEX_MAP: Dict[str, str] = {
    "AudioDG_helper.exe": "URLBlocker_Exe_Mutex_07",
    "SpoolerSub_helper.exe": "URLBlocker_Monitor_Mutex_07",
    "FontHost_worker.exe": "URLBlocker_Watcher_Mutex_07",
    "WinLogonAssist.exe": "URLBlocker_Guard_Mutex_08"
}

_start_attempts: Dict[str, List[float]] = {}
_last_backoff_time: Dict[str, float] = {}
TH32CS_SNAPPROCESS: int = 2


class PROCESSENTRY32(ctypes.Structure):
    """Windows API PROCESSENTRY32 structure for Toolhelp32 process enumeration."""
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260)
    ]


def get_running_exes() -> Set[str]:
    """
    Takes a Windows process snapshot and returns a set of lowercase executable names currently running.

    Returns:
        Set[str]: Set of active executable filenames.
    """
    kernel32 = ctypes.windll.kernel32
    CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
    Process32First = kernel32.Process32First
    Process32Next = kernel32.Process32Next
    CloseHandle = kernel32.CloseHandle

    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if hProcessSnap == -1:
        return set()

    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)

    exes: Set[str] = set()
    if Process32First(hProcessSnap, ctypes.byref(pe32)):
        while True:
            try:
                exe_name = pe32.szExeFile.decode('mbcs').lower()
                exes.add(exe_name)
            except Exception:
                pass
            if not Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
    CloseHandle(hProcessSnap)
    return exes


def ensure_processes_running() -> None:
    """
    Verifies that all targeted helper executables are alive.
    Applies backoff rate-limiting to prevent restart loops if a process continually crashes.
    """
    global _start_attempts, _last_backoff_time
    now = time.time()
    try:
        exes = get_running_exes()
        for exe_name, launch_cmd in TARGETS:
            if exe_name.lower() == MY_EXE_NAME:
                continue

            mutex_name = MUTEX_MAP.get(exe_name)
            if mutex_name and is_mutex_locked(mutex_name):
                continue

            if exe_name.lower() not in exes:
                exe_basename = exe_name
                if exe_basename in _last_backoff_time:
                    if now - _last_backoff_time[exe_basename] < 30.0:
                        continue
                    else:
                        del _last_backoff_time[exe_basename]

                attempts = _start_attempts.get(exe_basename, [])
                attempts = [t for t in attempts if now - t < 10.0]
                if len(attempts) >= 3:
                    _last_backoff_time[exe_basename] = now
                    _start_attempts[exe_basename] = []
                    continue

                attempts.append(now)
                _start_attempts[exe_basename] = attempts

                subprocess.Popen(
                    launch_cmd,
                    creationflags=0x08000000,
                    cwd=BASE_DIR,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
    except Exception:
        pass


def main() -> None:
    """
    Main system guard loop. Acquires primary guard mutex and continuously enforces process persistence.
    """
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Guard_Mutex_08")  # noqa: F841
    last_err = ctypes.get_last_error()
    if last_err == ERROR_ALREADY_EXISTS:
        return

    while True:
        try:
            ensure_processes_running()
        except Exception:
            pass
        time.sleep(0.2)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        with open(os.path.join(WRITABLE_DIR, "guard_fatal.txt"), "w") as f:
            f.write(traceback.format_exc())
