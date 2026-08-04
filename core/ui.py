"""
ui.py

Provides the floating, topmost GUI overlay (Time Keeper) using CustomTkinter.
Displays real-time usage progress bars, countdowns, and security status.
"""

import os
import sys
import json
import datetime
import customtkinter as ctk
import ctypes
from ctypes import wintypes
from typing import Dict, Any, List, Optional
from data_manager import UsageManager, WRITABLE_DIR, save_config, load_config


class OverlayApp:
    """
    Floating topmost dashboard displaying live site usage countdowns, block list status, and security alerts.
    """

    def __init__(self, root: ctk.CTk, manager: UsageManager, config: Dict[str, Any]) -> None:
        """
        Initializes the overlay application window and UI widgets.

        Args:
            root (ctk.CTk): The main CustomTkinter root window.
            manager (UsageManager): The data manager instance for usage tracking.
            config (Dict[str, Any]): Application configuration dictionary.
        """
        self.root: ctk.CTk = root
        self.manager: UsageManager = manager
        self.config: Dict[str, Any] = config
        self.time_limits: Dict[str, int] = config.get("TIME_LIMITS", {})
        self.block_list: List[str] = config.get("BLOCK_LIST", [])
        self.white_list: List[str] = config.get("WHITE_LIST", [])

        self.root.title("Time Keeper")
        self.root.geometry("280x450+50+50")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.root.resizable(True, True)
        self.root.minsize(250, 400)

        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        self.last_config_mtime = os.path.getmtime(self.config_path) if os.path.exists(self.config_path) else 0

        self.main_scroll: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(root, fg_color="transparent")
        self.main_scroll.pack(side='top', fill='both', expand=True, padx=10, pady=5)

        header = ctk.CTkLabel(
            self.main_scroll,
            text="⏳ 本日の使用状況",
            font=ctk.CTkFont(family="Meiryo UI", size=16, weight="bold")
        )
        header.pack(anchor='w', pady=(5, 10))

        self.progress_bars: Dict[str, ctk.CTkProgressBar] = {}
        self.time_labels: Dict[str, ctk.CTkLabel] = {}

        for domain in self.time_limits:
            self.create_domain_card(self.main_scroll, domain)

        separator = ctk.CTkFrame(self.main_scroll, height=2, fg_color=("gray70", "gray30"))
        separator.pack(fill='x', pady=15)

        self.is_blocklist_open: bool = False
        block_toggle_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        block_toggle_frame.pack(fill='x', pady=2)

        self.toggle_btn: ctk.CTkButton = ctk.CTkButton(
            block_toggle_frame,
            text="▶ 表示",
            width=50,
            height=24,
            fg_color="#333333",
            hover_color="#555555",
            font=ctk.CTkFont(size=11),
            command=self.toggle_block_list
        )
        self.toggle_btn.pack(side='left')
        ctk.CTkLabel(
            block_toggle_frame,
            text=f" 完全ブロックリスト ({len(self.block_list)}件)",
            font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold")
        ).pack(side='left', padx=5)

        self.block_list_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            self.main_scroll, height=100, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8
        )
        for item in self.block_list:
            ctk.CTkLabel(
                self.block_list_frame,
                text=f"• {item}",
                font=ctk.CTkFont(family="Consolas", size=11)
            ).pack(anchor='w', padx=5, pady=1)

        self.is_whitelist_open: bool = False
        wl_toggle_frame = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        wl_toggle_frame.pack(fill='x', pady=(10, 2))

        self.wl_toggle_btn: ctk.CTkButton = ctk.CTkButton(
            wl_toggle_frame,
            text="▶ 表示",
            width=50,
            height=24,
            fg_color="#333333",
            hover_color="#555555",
            font=ctk.CTkFont(size=11),
            command=self.toggle_white_list
        )
        self.wl_toggle_btn.pack(side='left')
        ctk.CTkLabel(
            wl_toggle_frame,
            text=f" 許可リスト ({len(self.white_list)}件)",
            font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold")
        ).pack(side='left', padx=5)

        self.white_list_frame: ctk.CTkScrollableFrame = ctk.CTkScrollableFrame(
            self.main_scroll, height=100, fg_color=("#e9ecef", "#2b2b2b"), corner_radius=8
        )
        for item in self.white_list:
            ctk.CTkLabel(
                self.white_list_frame,
                text=f"✓ {item}",
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color="#198754"
            ).pack(anchor='w', padx=5, pady=1)

        self.status_var: ctk.StringVar = ctk.StringVar(value="システム稼働中...")
        self.status_frame: ctk.CTkFrame = ctk.CTkFrame(root, height=35, fg_color="#1f538d", corner_radius=0)
        self.status_frame.pack(side='bottom', fill='x')
        self.status_frame.pack_propagate(False)

        self.settings_btn = ctk.CTkButton(
            self.status_frame,
            text="⚙️ 設定",
            width=50,
            height=24,
            fg_color="transparent",
            hover_color="#3b73b5",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.open_settings_editor
        )
        self.settings_btn.pack(side='right', padx=5, pady=5)

        self.status_label: ctk.CTkLabel = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_var,
            font=ctk.CTkFont(family="Meiryo UI", size=11, weight="bold"),
            text_color="white"
        )
        self.status_label.pack(side='left', expand=True, padx=(50, 0))

        self.update_gui()

    def open_settings_editor(self):
        try:
            editor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_editor.pyw")
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "open", 
                sys.executable, 
                f'"{editor_path}"', 
                None, 
                1
            )
        except Exception:
            pass

    def create_domain_card(self, parent: Any, domain: str) -> None:
        """
        Creates a visual card with domain label, countdown timer, and progress bar.

        Args:
            parent (Any): The parent widget frame.
            domain (str): The domain name to display.
        """
        card = ctk.CTkFrame(
            parent,
            corner_radius=8,
            fg_color=("white", "#2b2b2b"),
            border_width=1,
            border_color=("gray85", "gray25")
        )
        card.pack(fill='x', pady=5, padx=2)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill='x', padx=10, pady=(8, 0))

        info_row = ctk.CTkFrame(card, fg_color="transparent", height=18)
        info_row.pack(fill='x', padx=10, pady=(0, 5))
        info_row.pack_propagate(False)

        domain_lbl = ctk.CTkLabel(
            top_row,
            text=domain,
            font=ctk.CTkFont(family="Meiryo UI", size=12, weight="bold"),
            anchor="w"
        )
        domain_lbl.pack(side='left', fill='x', expand=True)

        time_lbl = ctk.CTkLabel(
            top_row,
            text="--:--",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="gray",
            width=55,
            anchor="e"
        )
        time_lbl.pack(side='right')
        self.time_labels[domain] = time_lbl

        domain_config = self.time_limits.get(domain, {})
        max_sec = domain_config.get("max_seconds", 0) if isinstance(domain_config, dict) else 0
        allow_windows = domain_config.get("allow_windows", []) if isinstance(domain_config, dict) else []
        
        info_texts = []
        if max_sec > 0:
            info_texts.append(f"{max_sec//60}分")
        if allow_windows:
            win_str = ",".join([f"{w.get('start', '')}~{w.get('end', '')}" for w in allow_windows])
            if win_str:
                info_texts.append(win_str)
        
        info_str = " | ".join(info_texts)

        if info_str:
            info_lbl = ctk.CTkLabel(
                info_row,
                text=info_str,
                font=ctk.CTkFont(family="Meiryo UI", size=10),
                text_color="#aaaaaa",
                anchor="w"
            )
            info_lbl.pack(side='left', fill='x', expand=True)

        pb = ctk.CTkProgressBar(card, height=6, corner_radius=3, progress_color="#1f538d")
        pb.pack(fill='x', padx=10, pady=(0, 8))
        pb.set(0)
        self.progress_bars[domain] = pb

    def toggle_block_list(self) -> None:
        """Toggles visibility of the complete block list panel."""
        if self.is_blocklist_open:
            self.block_list_frame.pack_forget()
            self.toggle_btn.configure(text="▶ 表示")
        else:
            self.block_list_frame.pack(fill='x', pady=10, padx=5)
            self.toggle_btn.configure(text="▼ 隠す")
        self.is_blocklist_open = not self.is_blocklist_open

    def toggle_white_list(self) -> None:
        """Toggles visibility of the whitelist panel."""
        if self.is_whitelist_open:
            self.white_list_frame.pack_forget()
            self.wl_toggle_btn.configure(text="▶ 表示")
        else:
            self.white_list_frame.pack(fill='x', pady=10, padx=5)
            self.wl_toggle_btn.configure(text="▼ 隠す")
        self.is_whitelist_open = not self.is_whitelist_open

    def disable_event(self) -> None:
        """Disables window closing via the close button to ensure persistent monitoring."""
        pass

    def update_gui(self) -> None:
        """
        Periodic GUI update loop. Reloads tracking data from disk and refreshes countdown timers and status.
        """
        if os.path.exists(self.config_path):
            current_mtime = os.path.getmtime(self.config_path)
            if current_mtime > self.last_config_mtime:
                self.last_config_mtime = current_mtime
                self.config = load_config()
                self.time_limits = self.config.get("TIME_LIMITS", {})
                self.block_list = self.config.get("BLOCK_LIST", [])
                self.white_list = self.config.get("WHITE_LIST", [])
                
                for pb in self.progress_bars.values(): pb.master.destroy()
                self.progress_bars.clear()
                self.time_labels.clear()
                for domain in self.time_limits:
                    self.create_domain_card(self.main_scroll, domain)

        today_str = datetime.date.today().isoformat()
        if self.manager.data["date"] != today_str:
            self.manager.data = {"date": today_str, "usage": {k: 0 for k in self.time_limits}}
            self.manager.save_data()

        self.manager.data = self.manager.load_data()

        for domain, domain_config in self.time_limits.items():
            used = self.manager.get_usage(domain)
            limit = domain_config.get("max_seconds", 0)
            remaining = max(0, limit - used)
            rem_min = remaining // 60
            rem_sec = remaining % 60

            if domain not in self.progress_bars: continue
            pb = self.progress_bars[domain]
            fraction = min(1.0, used / limit) if limit > 0 else 1.0
            pb.set(fraction)

            lbl = self.time_labels[domain]
            if used >= limit:
                lbl.configure(text="Time Up", text_color="#ff4a4a")
                pb.configure(progress_color="#ff4a4a")
            else:
                lbl.configure(text=f"{rem_min:02d}:{rem_sec:02d}", text_color="#ffffff")
                if fraction > 0.8:
                    pb.configure(progress_color="#e6a23c")
                else:
                    pb.configure(progress_color="#1f538d")

        try:
            status_path = os.path.join(WRITABLE_DIR, "status.txt")
            if os.path.exists(status_path):
                with open(status_path, "r", encoding="utf-8") as f:
                    status_text = f.read().strip()
                self.set_status(status_text)
        except BaseException:
            pass

        self.root.after(200, self.update_gui)

    def set_status(self, text: str) -> None:
        """
        Updates the bottom status label and panel color based on the current monitoring state.

        Args:
            text (str): Status text string from the background monitor.
        """
        self.status_var.set(text)
        if "BLOCKED" in text or "TIME UP" in text:
            self.status_frame.configure(fg_color="#ff4a4a")
        elif "Counting" in text:
            self.status_frame.configure(fg_color="#e6a23c")
        elif "Allowed" in text:
            self.status_frame.configure(fg_color="#4caf50")
        else:
            self.status_frame.configure(fg_color="#1f538d")
