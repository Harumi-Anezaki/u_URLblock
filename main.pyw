import uiautomation as auto
import time
import sys
import subprocess
import os
import json
import datetime
import threading
import random
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import hashlib
import base64
import ctypes
from ctypes import wintypes
import zlib

from win_utils import ensure_processes_running, is_window_cloaked

# ==========================================
# 設定と定数
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_BIN = r"C:\Users\aneha\AppData\Local\Python\pythoncore-3.14-64"
TARGETS = [
    ("main.pyw", os.path.join(PYTHON_BIN, "AudioDG_helper.exe")),
    ("watcher.pyw", os.path.join(PYTHON_BIN, "FontHost_worker.exe")),
    ("WinLogonAssist.exe", os.path.join(BASE_DIR, "WinLogonAssist", "WinLogonAssist.exe")),
]
MY_FILENAME = "main.pyw"
JSON_FILE = "usage_log.json"
CONFIG_FILE = "config.json"

def load_config():
    config_path = os.path.join(BASE_DIR, CONFIG_FILE)
    if not os.path.exists(config_path):
        return {"WHITE_LIST": [], "TIME_LIMITS": {}, "BLOCK_LIST": []}
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==========================================
# フォルダロック用クラス
# ==========================================
class FolderLocker:
    def __init__(self):
        self.lock_path = os.path.join(BASE_DIR, "system.lock")
        self.file_handle = None
        self.lock()

    def lock(self):
        try:
            self.file_handle = open(self.lock_path, "w")
            self.file_handle.write("LOCKED")
            self.file_handle.flush()
            subprocess.run(["attrib", "+h", self.lock_path], creationflags=0x08000000)
        except:
            pass

# ==========================================
# データ管理クラス (冗長・高セキュア版)
# ==========================================
class UsageManager:
    def __init__(self, config):
        self.filepath = os.path.join(BASE_DIR, JSON_FILE)
        self.time_limits = config.get("TIME_LIMITS", {})
        self.secret_key1 = "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
        self.secret_key2 = "Z9Y8X7W6-V5U4-T3S2-R1Q0-P9O8N7M6L5K4"
        self.data = self.load_data()

    def _xor_crypt(self, text, key):
        return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

    def _calculate_checksums(self, encoded_data_str):
        sha_hash = hashlib.sha256((encoded_data_str + self.secret_key1).encode('utf-8')).hexdigest()
        md5_hash = hashlib.md5((encoded_data_str + self.secret_key2).encode('utf-8')).hexdigest()
        return sha_hash, md5_hash

    def load_data(self):
        today_str = datetime.date.today().isoformat()
        default_data = {"date": today_str, "usage": {k: 0 for k in self.time_limits}}
        penalty_data = {"date": today_str, "usage": {k: 999999 for k in self.time_limits}}

        def reset_and_save(is_penalty=False):
            self.data = penalty_data if is_penalty else default_data
            self.save_data()
            return self.data

        if not os.path.exists(self.filepath):
            return reset_and_save()

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                saved_content = json.load(f)

            if "payload" not in saved_content or "signature1" not in saved_content or "signature2" not in saved_content:
                return reset_and_save(is_penalty=True)

            encoded_data = saved_content["payload"]
            sig1 = saved_content["signature1"]
            sig2 = saved_content["signature2"]

            calc_sig1, calc_sig2 = self._calculate_checksums(encoded_data)
            if calc_sig1 != sig1 or calc_sig2 != sig2:
                return reset_and_save(is_penalty=True)

            decoded_b64 = base64.b64decode(encoded_data.encode('utf-8')).decode('utf-8')
            decrypted_xor = self._xor_crypt(decoded_b64, self.secret_key1)
            decompressed = zlib.decompress(bytes.fromhex(decrypted_xor)).decode('utf-8')
            
            data = json.loads(decompressed)

            if data.get("date") != today_str:
                return reset_and_save()

            return data
        except:
            return reset_and_save(is_penalty=True)

    def save_data(self):
        try:
            json_str = json.dumps(self.data)
            compressed = zlib.compress(json_str.encode('utf-8')).hex()
            crypted_xor = self._xor_crypt(compressed, self.secret_key1)
            encoded_data = base64.b64encode(crypted_xor.encode('utf-8')).decode('utf-8')
            sig1, sig2 = self._calculate_checksums(encoded_data)

            content_to_save = {
                "metadata": {"version": 2, "id": random.randint(1000, 9999)},
                "payload": encoded_data,
                "signature1": sig1,
                "dummy_hash": hashlib.sha1(str(random.random()).encode()).hexdigest(),
                "signature2": sig2
            }

            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(content_to_save, f)
                f.flush()
                os.fsync(f.fileno())
        except:
            pass

    def add_usage(self, domain, seconds):
        today_str = datetime.date.today().isoformat()
        if self.data["date"] != today_str:
            self.data = {"date": today_str, "usage": {k: 0 for k in self.time_limits}}

        if domain not in self.data["usage"]:
            self.data["usage"][domain] = 0

        self.data["usage"][domain] += seconds
        self.save_data()

    def get_usage(self, domain):
        return int(self.data["usage"].get(domain, 0))

# ==========================================
# GUIクラス
# ==========================================
class OverlayApp:
    def __init__(self, root, manager, config):
        self.root = root
        self.manager = manager
        self.config = config
        self.time_limits = config.get("TIME_LIMITS", {})
        self.block_list = config.get("BLOCK_LIST", [])
        self.white_list = config.get("WHITE_LIST", [])

        self.root.title("Time Keeper")
        self.root.geometry("280x450+50+50")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.root.resizable(True, True)
        self.root.minsize(250, 400)

        self.main_scroll = ctk.CTkScrollableFrame(root, fg_color="transparent")
        self.main_scroll.pack(side='top', fill='both', expand=True, padx=10, pady=5)

        header = ctk.CTkLabel(self.main_scroll, text="⏳ 本日の使用状況", font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold"))
        header.pack(anchor='w', pady=(5, 10))

        self.progress_bars = {}
        self.time_labels = {}
        
        for domain in self.time_limits:
            self.create_domain_card(self.main_scroll, domain)

        separator = ctk.CTkFrame(self.main_scroll, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', pady=15)

        self.is_blocklist_open = False
        block_toggle_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        block_toggle_frame.pack(fill='x', pady=2)
        
        self.toggle_btn = ctk.CTkButton(block_toggle_frame, text="▶ 表示", width=50, height=24, fg_color="#333333", hover_color="#555555", font=ctk.CTkFont(size=11), command=self.toggle_block_list)
        self.toggle_btn.pack(side='left')
        ctk.CTkLabel(block_toggle_frame, text=f" 完全ブロックリスト ({len(self.block_list)}件)", font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold")).pack(side='left', padx=5)

        self.block_list_frame = ctk.CTkScrollableFrame(self.main_scroll, height=100, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8)
        for item in self.block_list:
            ctk.CTkLabel(self.block_list_frame, text=f"• {item}", font=ctk.CTkFont(family="Consolas", size=11)).pack(anchor='w', padx=5, pady=1)

        self.is_whitelist_open = False
        wl_toggle_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        wl_toggle_frame.pack(fill='x', pady=(10, 2))

        self.wl_toggle_btn = ctk.CTkButton(wl_toggle_frame, text="▶ 表示", width=50, height=24, fg_color="#333333", hover_color="#555555", font=ctk.CTkFont(size=11), command=self.toggle_white_list)
        self.wl_toggle_btn.pack(side='left')
        ctk.CTkLabel(wl_toggle_frame, text=f" 許可リスト ({len(self.white_list)}件)", font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold")).pack(side='left', padx=5)

        self.white_list_frame = ctk.CTkScrollableFrame(self.main_scroll, height=100, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8)
        for item in self.white_list:
            ctk.CTkLabel(self.white_list_frame, text=f"✓ {item}", font=ctk.CTkFont(family="Consolas", size=11), text_color="#198754").pack(anchor='w', padx=5, pady=1)

        self.status_var = ctk.StringVar(value="システム稼働中...")
        self.status_frame = ctk.CTkFrame(root, height=35, fg_color="#1f538d", corner_radius=0)
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)
        self.status_label = ctk.CTkLabel(self.status_frame, textvariable=self.status_var, font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold"), text_color="white")
        self.status_label.pack(expand=True)

        self.update_gui()

    def create_domain_card(self, parent, domain):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color=("white", "#2b2b2b"), border_width=1, border_color=("gray85", "gray25"))
        card.pack(fill='x', pady=5, padx=2)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill='x', padx=10, pady=(8, 5))

        domain_lbl = ctk.CTkLabel(top_row, text=domain, font=ctk.CTkFont(family="Meiryo UI", size=12, weight="bold"))
        domain_lbl.pack(side='left')

        time_lbl = ctk.CTkLabel(top_row, text="--:--", font=ctk.CTkFont(family="Consolas", size=13, weight="bold"), text_color="gray")
        time_lbl.pack(side='right')
        self.time_labels[domain] = time_lbl

        pb = ctk.CTkProgressBar(card, height=6, corner_radius=3, progress_color="#1f538d")
        pb.pack(fill='x', padx=10, pady=(0, 8))
        pb.set(0)
        self.progress_bars[domain] = pb

    def toggle_block_list(self):
        if self.is_blocklist_open:
            self.block_list_frame.pack_forget()
            self.toggle_btn.configure(text="▶ 表示")
        else:
            self.block_list_frame.pack(fill='x', pady=10, padx=5)
            self.toggle_btn.configure(text="▼ 隠す")
        self.is_blocklist_open = not self.is_blocklist_open

    def toggle_white_list(self):
        if self.is_whitelist_open:
            self.white_list_frame.pack_forget()
            self.wl_toggle_btn.configure(text="▶ 表示")
        else:
            self.white_list_frame.pack(fill='x', pady=10, padx=5)
            self.wl_toggle_btn.configure(text="▼ 隠す")
        self.is_whitelist_open = not self.is_whitelist_open

    def disable_event(self):
        pass

    def update_gui(self):
        today_str = datetime.date.today().isoformat()
        if self.manager.data["date"] != today_str:
            self.manager.data = {"date": today_str, "usage": {k: 0 for k in self.time_limits}}
            self.manager.save_data()

        for domain, limit in self.time_limits.items():
            used = self.manager.get_usage(domain)
            remaining = max(0, limit - used)
            rem_min = remaining // 60
            rem_sec = remaining % 60

            pb = self.progress_bars[domain]
            fraction = min(1.0, used / limit) if limit > 0 else 1.0
            pb.set(fraction)
            
            lbl = self.time_labels[domain]
            if used >= limit:
                lbl.configure(text="Time Up", text_color="#ff4a4a")
                pb.configure(progress_color="#ff4a4a")
            else:
                lbl.configure(text=f"{rem_min:02}:{rem_sec:02}", text_color=("#1f538d", "#5da2ed"))
                if fraction > 0.8:
                    pb.configure(progress_color="#e6a23c")
                else:
                    pb.configure(progress_color="#1f538d")

        self.root.after(1000, self.update_gui)

    def set_status(self, text):
        self.status_var.set(text)
        if "BLOCKED" in text or "TIME UP" in text:
            self.status_frame.configure(fg_color="#ff4a4a")
        elif "Counting" in text:
            self.status_frame.configure(fg_color="#e6a23c")
        elif "Allowed" in text:
            self.status_frame.configure(fg_color="#4caf50")
        else:
            self.status_frame.configure(fg_color="#1f538d")

# ==========================================
# 監視ロジッククラス化
# ==========================================
class URLMonitor:
    def __init__(self, app, manager, config):
        self.app = app
        self.manager = manager
        self.config = config
        self.white_list = config.get("WHITE_LIST", [])
        self.time_limits = config.get("TIME_LIMITS", {})
        self.block_list = config.get("BLOCK_LIST", [])
        self.url_cache = {}

    def start(self):
        t = threading.Thread(target=self._monitor_loop, daemon=True)
        t.start()
        
        t_watch = threading.Thread(target=self._watchdog_loop, daemon=True)
        t_watch.start()

    def _watchdog_loop(self):
        while True:
            try:
                ensure_processes_running(BASE_DIR, MY_FILENAME, TARGETS)
            except:
                pass
            time.sleep(0.2)

    def _perform_block(self, window):
        try:
            if "Chrome_WidgetWin_1" in window.ClassName:
                window.SetFocus()
                window.SendKeys('{Ctrl}w')
        except:
            pass

    def _extract_url(self, window):
        edit = auto.EditControl(searchFromControl=window, AccessKey="Ctrl+L")
        if edit.Exists(0, 0):
            try:
                return edit.GetValuePattern().Value
            except:
                pass

        edit = window.Control(ControlType=auto.ControlType.EditControl, Name="アドレスと検索バー", searchDepth=4)
        if not edit.Exists(0, 0):
            edit = window.Control(ControlType=auto.ControlType.EditControl, Name="Address and search bar", searchDepth=4)
        if not edit.Exists(0, 0):
            edit = window.EditControl()
        
        if edit.Exists(0, 0):
            try:
                return edit.GetValuePattern().Value
            except:
                pass
        return None

    def _monitor_loop(self):
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
                        current_url = self.url_cache.get(hwnd, "")
                    else:
                        val = self._extract_url(window)
                        if val:
                            current_url = val
                            self.url_cache[hwnd] = current_url
                        
                        if not current_url:
                            current_url = self.url_cache.get(hwnd, "")

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

                self.app.set_status(status_text)

            except Exception:
                pass

            time.sleep(1.0)

# ==========================================
# メイン (エラーログ機能付き)
# ==========================================
def main():
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Exe_Mutex_07")
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    locker = FolderLocker()
    config = load_config()
    manager = UsageManager(config)
    
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    
    app = OverlayApp(root, manager, config)
    monitor = URLMonitor(app, manager, config)
    monitor.start()

    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        with open(os.path.join(BASE_DIR, "error_log.txt"), "w", encoding='utf-8') as f:
            f.write(traceback.format_exc())
