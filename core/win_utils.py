import os
import ctypes
from ctypes import wintypes
import subprocess

TH32CS_SNAPPROCESS = 2
DWMWA_CLOAKED = 14


class PROCESSENTRY32(ctypes.Structure):
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


def is_window_cloaked(hwnd):
    cloaked = wintypes.DWORD()
    try:
        res = ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd,
            DWMWA_CLOAKED,
            ctypes.byref(cloaked),
            ctypes.sizeof(cloaked)
        )
        if res == 0:
            return bool(cloaked.value)
    except Exception:
        pass
    return False


def get_running_exes():
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

    exes = set()
    if Process32First(hProcessSnap, ctypes.byref(pe32)):
        while True:
            try:
                exe_name = pe32.szExeFile.decode('mbcs').lower()
                exes.add(exe_name)
            except BaseException:
                pass
            if not Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
    CloseHandle(hProcessSnap)
    return exes


def is_mutex_locked(mutex_name):
    SYNCHRONIZE = 0x00100000
    handle = ctypes.windll.kernel32.OpenMutexW(SYNCHRONIZE, False, mutex_name)
    if handle:
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    return False

MUTEX_MAP = {
    "main.pyw": "URLBlocker_Exe_Mutex_07",
    "monitor.pyw": "URLBlocker_Monitor_Mutex_07",
    "watcher.pyw": "URLBlocker_Watcher_Mutex_07",
    "system_guard.pyw": "URLBlocker_Guard_Mutex_08"
}

_start_attempts = {}
_last_backoff_time = {}

def ensure_processes_running(base_dir, my_filename, targets):
    global _start_attempts, _last_backoff_time
    import time
    now = time.time()
    try:
        exes = get_running_exes()

        for script_name, exe_name in targets:
            if script_name == my_filename:
                continue
                
            mutex_name = MUTEX_MAP.get(script_name)
            if mutex_name and is_mutex_locked(mutex_name):
                continue

            exe_basename = os.path.basename(exe_name)
            if exe_basename.lower() not in exes:
                
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
                
                script_path = os.path.join(base_dir, script_name)
                if script_name.endswith('.exe'):
                    subprocess.Popen([exe_name], creationflags=0x08000000, cwd=base_dir, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen([exe_name, script_path], creationflags=0x08000000, cwd=base_dir, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error in ensure_processes_running: {e}")

