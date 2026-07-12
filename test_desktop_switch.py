import time
import os
import ctypes
from win_utils import is_window_cloaked
import uiautomation as auto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "desktop_test.log")

def _extract_url(window):
    edit = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
    if edit.Exists(0, 0):
        try:
            return edit.GetValuePattern().Value
        except:
            pass

    edit = window.Control(ControlType=auto.ControlType.EditControl, Name="アドレスと検索バー", searchDepth=6)
    if not edit.Exists(0, 0):
        edit = window.Control(ControlType=auto.ControlType.EditControl, Name="Address and search bar", searchDepth=6)
    if not edit.Exists(0, 0):
        edit = window.EditControl()
    
    if edit.Exists(0, 0):
        try:
            return edit.GetValuePattern().Value
        except:
            pass
    return None

def main():
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("Started Desktop Switch Test\n")
        
    while True:
        try:
            root = auto.GetRootControl()
            children = root.GetChildren()
            
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n--- Check at {time.strftime('%H:%M:%S')} ---\n")
                found_chrome = False
                for window in children:
                    if "Chrome_WidgetWin_1" in window.ClassName:
                        found_chrome = True
                        hwnd = window.NativeWindowHandle
                        is_cloaked = is_window_cloaked(hwnd)
                        is_iconic = ctypes.windll.user32.IsIconic(hwnd)
                        
                        f.write(f"Chrome HWND: {hwnd}, Cloaked: {is_cloaked}, Minimized: {is_iconic}\n")
                        
                        if not is_cloaked and not is_iconic:
                            url = _extract_url(window)
                            f.write(f"  -> Extracted URL: '{url}', Title: '{window.Name}'\n")
                        else:
                            f.write(f"  -> Skipped URL extraction because cloaked or iconic.\n")
                
                if not found_chrome:
                    f.write("No Chrome windows found.\n")
        except Exception as e:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"Error: {e}\n")
                
        time.sleep(2.0)

if __name__ == "__main__":
    main()
