# -*- coding: utf-8 -*-
import time
import subprocess
import os
import ctypes
from ctypes import wintypes

# ==========================================
# 設定
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MY_FILENAME = os.path.basename(__file__)

PYTHON_BIN = r"C:\Users\aneha\AppData\Local\Python\pythoncore-3.14-64"
TARGETS = [
    ("実行.pyw", os.path.join(PYTHON_BIN, "AudioDG_helper.exe")),
    ("監視.pyw", os.path.join(PYTHON_BIN, "FontHost_worker.exe")),
    ("WinLogonAssist.exe", os.path.join(BASE_DIR, "WinLogonAssist", "WinLogonAssist.exe")),
]
# ==========================================

TH32CS_SNAPPROCESS = 2

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
            except:
                pass
            if not Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
    CloseHandle(hProcessSnap)
    return exes

def ensure_processes_running():
    try:
        exes = get_running_exes()
        
        for script_name, exe_name in TARGETS:
            if script_name == MY_FILENAME:
                continue # 自分自身は監視対象から外す
            
            exe_basename = os.path.basename(exe_name)
            if exe_basename.lower() not in exes:
                # 死んでいるプロセスを見つけたら再起動
                script_path = os.path.join(BASE_DIR, script_name)
                if script_name.endswith('.exe'):
                    subprocess.Popen([exe_name], creationflags=0x08000000, cwd=BASE_DIR)
                else:
                    subprocess.Popen([exe_name, script_path], creationflags=0x08000000, cwd=BASE_DIR)
    except:
        pass

def main():
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Watcher_Mutex_07")
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    while True:
        try:
            ensure_processes_running()
        except:
            pass
        time.sleep(0.2) # 0.2秒間隔で監視

if __name__ == "__main__":
    main()
