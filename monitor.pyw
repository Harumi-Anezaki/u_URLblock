import time
import os
import ctypes
from win_utils import is_window_cloaked
import uiautomation as auto
import json
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = "config.json"
STATUS_FILE = "status.txt"

# --- 共通のUsageManagerをインポートするためにmain.pywからロード ---
import sys
sys.path.append(BASE_DIR)
try:
    from main import UsageManager, load_config
except ImportError:
    pass

class URLMonitor:
    def __init__(self, manager, config):
        self.manager = manager
        self.config = config
        self.white_list = config.get("WHITE_LIST", [])
        self.time_limits = config.get("TIME_LIMITS", {})
        self.block_list = config.get("BLOCK_LIST", [])
        self.url_cache = {}

    def _perform_block(self, window):
        try:
            if "Chrome_WidgetWin_1" in window.ClassName:
                window.SetFocus()
                window.SendKeys('{Ctrl}w')
        except:
            pass

    def _extract_url_from_title(self, title):
        if not title:
            return None
        title = title.lower()
        if "youtube" in title:
            if "shorts" in title:
                return "youtube.com/shorts"
            return "youtube.com"
        if " / x" in title or " - x" in title or "x" == title.strip():
            return "x.com"
        if "tiktok" in title:
            return "tiktok.com"
        if "instagram" in title:
            return "instagram.com"
        if "pornhub" in title:
            return "pornhub.com"
        if "xvideos" in title:
            return "xvideos.com"
        if "missav" in title:
            return "missav.ai"
        if "duckduckgo" in title:
            return "duckduckgo.com"
        if "yahoo!知恵袋" in title or "yahoo! chiebukuro" in title:
            return "chiebukuro.yahoo.co.jp"
        if "yahoo" in title:
            return "yahoo.co.jp"
        return None

    def _extract_url(self, window):
        edit = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
        if edit.Exists(0, 0):
            try:
                val = edit.GetValuePattern().Value
                if val: return val
            except:
                pass

        edit = window.Control(ControlType=auto.ControlType.EditControl, Name="アドレスと検索バー", searchDepth=6)
        if not edit.Exists(0, 0):
            edit = window.Control(ControlType=auto.ControlType.EditControl, Name="Address and search bar", searchDepth=6)
        if not edit.Exists(0, 0):
            edit = window.EditControl()
        
        if edit.Exists(0, 0):
            try:
                val = edit.GetValuePattern().Value
                if val: return val
            except:
                pass
                
        # UIAutomationによるURL抽出が仮想デスクトップ切り替え等で失敗した場合のフォールバック
        return self._extract_url_from_title(window.Name)

    def start(self):
        last_check_time = time.time()
        while True:
            try:
                now = time.time()
                elapsed_seconds = now - last_check_time
                last_check_time = now

                root = auto.GetRootControl()
                children = root.GetChildren()

                status_priority = 0
                status_text = "💤  Idle"
                counted_domains = set()

                for window in children:
                    if "Chrome_WidgetWin_1" not in window.ClassName:
                        continue

                    hwnd = window.NativeWindowHandle
                    current_url = ""
                    
                    if ctypes.windll.user32.IsIconic(hwnd) or is_window_cloaked(hwnd):
                        continue
                    
                    current_url = self._extract_url(window)

                    if not current_url:
                        continue

                    url_base = current_url.split('?')[0]

                    whitelisted_word = next((w for w in self.white_list if w in url_base), None)
                    if whitelisted_word:
                        if status_priority < 1:
                            status_text = f"🛡️  Allowed: {whitelisted_word}"
                            status_priority = 1
                        continue

                    blocked_word = next((w for w in self.block_list if w in url_base), None)
                    if blocked_word:
                        status_text = f"🚫  BLOCKED: {blocked_word}"
                        status_priority = 4
                        self._perform_block(window)
                        continue

                    limited_domain = next((d for d in self.time_limits if d in current_url), None)
                    if limited_domain:
                        if limited_domain not in counted_domains:
                            self.manager.add_usage(limited_domain, elapsed_seconds)
                            counted_domains.add(limited_domain)

                        used = self.manager.get_usage(limited_domain)
                        limit = self.time_limits[limited_domain]

                        if used >= limit:
                            status_text = f"⌛  TIME UP: {limited_domain}"
                            status_priority = 3
                            self._perform_block(window)
                        else:
                            if status_priority < 2:
                                status_text = f"⏱  Counting: {limited_domain}"
                                status_priority = 2
                    else:
                        if status_priority < 1:
                            status_text = "✅  Safe Browsing"
                            status_priority = 1

                # ステータスをファイルに書き出してGUI側に伝える
                with open(os.path.join(BASE_DIR, STATUS_FILE), "w", encoding='utf-8') as f:
                    f.write(status_text)

            except Exception:
                pass

            time.sleep(1.0)

def main():
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Monitor_Mutex_07")
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    from main import load_config, UsageManager
    config = load_config()
    manager = UsageManager(config)
    
    monitor = URLMonitor(manager, config)
    monitor.start()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        with open(os.path.join(BASE_DIR, "monitor_error.log"), "w", encoding='utf-8') as f:
            f.write(traceback.format_exc())
