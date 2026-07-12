import ctypes
from ctypes import wintypes
import uiautomation as auto

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
    except Exception as e:
        print(f"Error checking cloaked for {hwnd}: {e}")
    return False

def debug_windows():
    print("--- Debugging Windows ---")
    root = auto.GetRootControl()
    for window in root.GetChildren():
        if "Chrome_WidgetWin_1" in window.ClassName:
            hwnd = window.NativeWindowHandle
            cloaked = is_window_cloaked(hwnd)
            visible = ctypes.windll.user32.IsWindowVisible(hwnd)
            iconic = ctypes.windll.user32.IsIconic(hwnd)
            print(f"HWND={hwnd}, Name='{window.Name}', Cloaked={cloaked}, Visible={visible}, Minimized={iconic}")

if __name__ == '__main__':
    debug_windows()
