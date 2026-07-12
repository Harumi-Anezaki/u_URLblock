import uiautomation as auto
import ctypes
from ctypes import wintypes
import time

DWMWA_CLOAKED = 14

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

def test():
    root = auto.GetRootControl()
    children = root.GetChildren()
    for window in children:
        if "Chrome_WidgetWin_1" in window.ClassName:
            hwnd = window.NativeWindowHandle
            cloaked = is_window_cloaked(hwnd)
            print(f"Window: {window.Name}, Cloaked: {cloaked}")
            if cloaked:
                print("Attempting to read URL of cloaked window...")
                try:
                    edit = window.Control(ControlType=auto.ControlType.EditControl, Name="アドレスと検索バー", searchDepth=4)
                    if not edit.Exists(0, 0):
                        edit = window.Control(ControlType=auto.ControlType.EditControl, Name="Address and search bar", searchDepth=4)
                    if edit.Exists(0, 0):
                        val = edit.GetValuePattern().Value
                        print(f"URL: {val}")
                    else:
                        print("Edit control not found.")
                except Exception as e:
                    print(f"Failed: {e}")

if __name__ == '__main__':
    test()
