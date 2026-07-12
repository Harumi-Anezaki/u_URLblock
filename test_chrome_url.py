import uiautomation as auto

def test_chrome_url():
    root = auto.GetRootControl()
    for window in root.GetChildren():
        if "Chrome_WidgetWin_1" in window.ClassName and "Google Chrome" in window.Name:
            print(f"Testing {window.Name}")
            try:
                doc = window.DocumentControl()
                if doc.Exists(0, 0):
                    val = doc.GetValuePattern().Value
                    print(f"  [DocumentControl] URL: {val}")
                else:
                    print("  [DocumentControl] Not Found")
            except Exception as e:
                print(f"  [DocumentControl] Error: {e}")
                
            try:
                edit = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
                if edit.Exists(0, 0):
                    print(f"  [Ctrl+L] URL: {edit.GetValuePattern().Value}")
            except Exception as e:
                print(f"  [Ctrl+L] Error: {e}")

if __name__ == '__main__':
    test_chrome_url()
