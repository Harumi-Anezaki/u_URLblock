import time
import os
import ctypes
import sys
import threading
from urllib.parse import urlparse

if sys.stdout is None:
    class DummyStream:
        def write(self, text): pass
        def flush(self): pass
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()

# from win_utils import is_window_cloaked
import uiautomation as auto

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
WRITABLE_DIR = os.path.join(ROOT_DIR, "authenticated_users_kakikomi_true")
os.makedirs(WRITABLE_DIR, exist_ok=True)
CONFIG_FILE = "config.json"
STATUS_FILE = "status.txt"

# --- 共通のUsageManagerをインポートするためにmain.pywからロード ---
import sys  # noqa: E402
import importlib.util
sys.path.append(BASE_DIR)
try:
    spec = importlib.util.spec_from_file_location("main", os.path.join(BASE_DIR, "main.pyw"))
    main_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_mod)
    UsageManager = main_mod.UsageManager
    load_config = main_mod.load_config
except Exception as e:
    with open(os.path.join(WRITABLE_DIR, "import_error.txt"), "w") as f:
        f.write(str(e))


class URLMonitor:
    def __init__(self, manager, config):
        self.manager = manager
        self.config = config
        self.white_list = config.get("WHITE_LIST", [])
        self.time_limits = config.get("TIME_LIMITS", {})
        self.block_list = config.get("BLOCK_LIST", [])
        self.url_cache = {}

    def _perform_block(self, hwnd):
        try:
            fg_hwnd = ctypes.windll.user32.GetForegroundWindow()
            if fg_hwnd == hwnd:
                import uiautomation as auto
                auto.SetGlobalSearchTimeout(1.0)
                win_ctrl = auto.WindowControl(searchDepth=1, Handle=hwnd)
                win_ctrl.SetFocus()
                win_ctrl.SendKeys('{Ctrl}w')
            else:
                ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
        except BaseException:
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

        # 動的マッチング：設定されたブロックリスト・制限リストから推測する
        all_domains = list(self.block_list) + list(self.time_limits.keys())
        title_no_spaces = title.replace(' ', '')
        
        for domain in all_domains:
            if 'notion' in domain.lower():
                continue
            clean_domain = domain.split('/')[0]
            parts = clean_domain.split('.')
            main_part = parts[0] if parts[0] != 'www' else parts[1]
            if len(main_part) > 2 and main_part in title_no_spaces:
                return domain
                
        return None

    def _extract_url(self, hwnd, title):
        import uiautomation as auto
        auto.SetGlobalSearchTimeout(0.2)
        try:
            window = auto.WindowControl(searchDepth=1, Handle=hwnd)
            edit = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
            if edit.Exists(0, 0):
                try:
                    val = edit.GetValuePattern().Value
                    if val:
                        return val
                except BaseException:
                    pass

            edit = window.Control(
                ControlType=auto.ControlType.EditControl,
                Name="アドレスと検索バー",
                searchDepth=6)
            if not edit.Exists(0, 0):
                edit = window.Control(
                    ControlType=auto.ControlType.EditControl,
                    Name="Address and search bar",
                    searchDepth=6)
            if not edit.Exists(0, 0):
                edit = window.EditControl()

            if edit.Exists(0, 0):
                try:
                    val = edit.GetValuePattern().Value
                    if val:
                        return val
                except BaseException:
                    pass
        except BaseException:
            pass

        return self._extract_url_from_title(title)

    def start(self):
        last_check_time = time.time()
        while True:
            try:
                now = time.time()
                elapsed_seconds = now - last_check_time
                last_check_time = now

                hwnds = []
                def get_hwnd(hwnd, lParam):
                    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    title_clean = title.replace('\u200b', '')
                    if ('Google Chrome' in title_clean or 'Microsoft Edge' in title_clean) and ctypes.windll.user32.IsWindowVisible(hwnd):
                        class_buff = ctypes.create_unicode_buffer(256)
                        ctypes.windll.user32.GetClassNameW(hwnd, class_buff, 256)
                        if 'Chrome_WidgetWin_1' in class_buff.value:
                            hwnds.append((hwnd, title))
                    return True

                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
                ctypes.windll.user32.EnumWindows(EnumWindowsProc(get_hwnd), 0)

                status_priority = 0
                status_text = "💤  Idle"
                counted_domains = set()

                for hwnd, title in hwnds:
                    current_url = self._extract_url(hwnd, title)

                    if not current_url:
                        continue

                    url_base = current_url.split('?')[0]

                    whitelisted_word = next(
                        (w for w in self.white_list if w in url_base), None)
                    if whitelisted_word:
                        if status_priority < 1:
                            status_text = f"🛡️  Allowed: {whitelisted_word}"
                            status_priority = 1
                        continue

                    blocked_word = next(
                        (w for w in self.block_list if w in url_base), None)
                    if blocked_word:
                        status_text = f"🚫  BLOCKED: {blocked_word}"
                        status_priority = 4
                        self._perform_block(hwnd)
                        continue

                    limited_domain = next(
                        (d for d in self.time_limits if d in current_url), None)
                    if limited_domain:
                        if limited_domain not in counted_domains:
                            self.manager.add_usage(
                                limited_domain, elapsed_seconds)
                            counted_domains.add(limited_domain)

                        used = self.manager.get_usage(limited_domain)
                        limit = self.time_limits[limited_domain]

                        if used >= limit:
                            status_text = f"⌛  TIME UP: {limited_domain}"
                            status_priority = 3
                            self._perform_block(hwnd)
                        else:
                            if status_priority < 2:
                                status_text = f"⏱  Counting: {limited_domain}"
                                status_priority = 2
                    else:
                        if status_priority < 1:
                            status_text = "✅  Safe Browsing"
                            status_priority = 1

                # ステータスをファイルに書き出してGUI側に伝える
                with open(os.path.join(WRITABLE_DIR, STATUS_FILE), "w", encoding='utf-8') as f:
                    f.write(status_text)

            except Exception as e:
                import traceback
                with open(os.path.join(WRITABLE_DIR, "loop_error.txt"), "a", encoding="utf-8") as err_f:
                    err_f.write(traceback.format_exc() + "\n")

            time.sleep(1.0)


def main():
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(
        None, False, "URLBlocker_Monitor_Mutex_07")  # noqa: F841
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    config = load_config()
    manager = UsageManager(config)

    monitor = URLMonitor(manager, config)
    monitor.start()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        with open(os.path.join(WRITABLE_DIR, "monitor_error.log"), "w", encoding='utf-8') as f:
            f.write(traceback.format_exc())
