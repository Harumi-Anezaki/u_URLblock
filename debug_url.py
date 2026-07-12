import uiautomation as auto
import time

def debug_chrome():
    print("--- Debugging Chrome Windows ---")
    root = auto.GetRootControl()
    for window in root.GetChildren():
        if "Chrome_WidgetWin_1" in window.ClassName:
            print(f"Found Chrome Window: HWND={window.NativeWindowHandle}, Name={window.Name}")
            
            # Try getting URL via AccessKey
            edit1 = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
            if edit1.Exists(0, 0):
                try:
                    url = edit1.GetValuePattern().Value
                    print(f"  [AccessKey Ctrl+L] URL: {url}")
                except Exception as e:
                    print(f"  [AccessKey Ctrl+L] Error: {e}")
            else:
                print("  [AccessKey Ctrl+L] Not Found")
                
            # Try getting URL via Name
            edit2 = window.Control(ControlType=auto.ControlType.EditControl, Name="アドレスと検索バー", searchDepth=4)
            if edit2.Exists(0, 0):
                try:
                    url = edit2.GetValuePattern().Value
                    print(f"  [Name アドレスと検索バー] URL: {url}")
                except Exception as e:
                    print(f"  [Name アドレスと検索バー] Error: {e}")
            else:
                print("  [Name アドレスと検索バー] Not Found")

            # Try getting URL via EditControl
            edit3 = window.EditControl()
            if edit3.Exists(0, 0):
                try:
                    url = edit3.GetValuePattern().Value
                    print(f"  [EditControl] URL: {url}")
                except Exception as e:
                    print(f"  [EditControl] Error: {e}")
            else:
                print("  [EditControl] Not Found")
                
            # Try DocumentControl
            doc = window.DocumentControl()
            if doc.Exists(0, 0):
                try:
                    url = doc.GetValuePattern().Value
                    print(f"  [DocumentControl] URL: {url}")
                except Exception as e:
                    print(f"  [DocumentControl] Error: {e}")
            else:
                print("  [DocumentControl] Not Found")
                
if __name__ == '__main__':
    debug_chrome()
