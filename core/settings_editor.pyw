import os
import sys
import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from data_manager import load_config, save_config

class SettingsEditor(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("設定エディタ")
        self.geometry("700x750")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        self.config = load_config()
        self.time_limits = self.config.get("TIME_LIMITS", {})
        self.block_list = self.config.get("BLOCK_LIST", [])
        self.white_list = self.config.get("WHITE_LIST", [])
        
        self.domain_frames = []
        self.block_entries = []
        self.white_entries = []
        
        self.build_ui()
        
    def build_ui(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=10, pady=10, fill="both", expand=True)
        
        self.tab_time = self.tabview.add("時間制限")
        self.tab_block = self.tabview.add("ブロックリスト")
        self.tab_white = self.tabview.add("許可リスト")
        
        self.build_time_limits_tab()
        self.build_simple_list_tab(self.tab_block, self.block_list, self.block_entries, "ブロックするドメイン/キーワードを追加")
        self.build_simple_list_tab(self.tab_white, self.white_list, self.white_entries, "許可するドメイン/キーワードを追加")
        
        self.error_lbl = ctk.CTkLabel(self, text="", text_color="#ff4a4a")
        self.error_lbl.pack(pady=5)
        
        save_btn = ctk.CTkButton(self, text="保存して終了", fg_color="#1f538d", font=ctk.CTkFont(weight="bold"), command=self.save_and_exit)
        save_btn.pack(pady=(0, 15))
        
    def build_time_limits_tab(self):
        self.time_scroll = ctk.CTkScrollableFrame(self.tab_time, fg_color="transparent")
        self.time_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        for domain, data in self.time_limits.items():
            self.add_domain_card(domain, data.get("max_seconds", 0), data.get("allow_windows", []))
            
        add_btn = ctk.CTkButton(self.tab_time, text="＋ ドメインを追加", command=lambda: self.add_domain_card("", 1800, []))
        add_btn.pack(pady=10)
        
    def add_domain_card(self, domain_name, max_seconds, allow_windows):
        card = ctk.CTkFrame(self.time_scroll, corner_radius=8, fg_color="#2b2b2b", border_width=1, border_color="#444444")
        card.pack(fill="x", pady=5, padx=5)
        
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(top_row, text="ドメイン:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        domain_var = ctk.StringVar(value=domain_name)
        domain_entry = ctk.CTkEntry(top_row, textvariable=domain_var, width=150)
        domain_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(top_row, text="1日の上限時間:").pack(side="left", padx=(20,0))
        mins = max_seconds // 60
        secs = max_seconds % 60
        min_var = ctk.StringVar(value=str(mins))
        sec_var = ctk.StringVar(value=str(secs))
        
        min_entry = ctk.CTkEntry(top_row, textvariable=min_var, width=50)
        min_entry.pack(side="left", padx=5)
        ctk.CTkLabel(top_row, text="分").pack(side="left")
        
        sec_entry = ctk.CTkEntry(top_row, textvariable=sec_var, width=50)
        sec_entry.pack(side="left", padx=5)
        ctk.CTkLabel(top_row, text="秒").pack(side="left")
        
        del_btn = ctk.CTkButton(top_row, text="🗑️ 削除", width=50, fg_color="#a83232", hover_color="#802626", command=lambda: self.delete_card(card, self.domain_frames))
        del_btn.pack(side="right")
        
        windows_frame = ctk.CTkFrame(card, fg_color="transparent")
        windows_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        windows_list = []
        for w in allow_windows:
            self.add_window_row(windows_frame, windows_list, w.get("start", ""), w.get("end", ""))
            
        add_win_btn = ctk.CTkButton(windows_frame, text="＋ 許可時間帯を追加", width=120, height=24, fg_color="#3b3b3b", hover_color="#555555", font=ctk.CTkFont(size=11), command=lambda: self.add_window_row(windows_frame, windows_list, "09:00", "17:00"))
        add_win_btn.pack(anchor="w", pady=(5,0))
        
        card_data = {
            "card": card,
            "domain_var": domain_var,
            "min_var": min_var,
            "sec_var": sec_var,
            "windows_list": windows_list
        }
        self.domain_frames.append(card_data)
        
    def add_window_row(self, parent, windows_list, start_time, end_time):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=2)
        
        ctk.CTkLabel(row, text="許可時間帯:").pack(side="left")
        start_var = ctk.StringVar(value=start_time)
        end_var = ctk.StringVar(value=end_time)
        
        ctk.CTkEntry(row, textvariable=start_var, width=60).pack(side="left", padx=5)
        ctk.CTkLabel(row, text="〜").pack(side="left")
        ctk.CTkEntry(row, textvariable=end_var, width=60).pack(side="left", padx=5)
        
        def del_row():
            row.destroy()
            windows_list.remove((start_var, end_var, row))
            
        ctk.CTkButton(row, text="×", width=30, height=24, fg_color="#666666", hover_color="#888888", command=del_row).pack(side="left", padx=10)
        windows_list.append((start_var, end_var, row))
        
    def delete_card(self, card, card_list):
        card.destroy()
        for i, c in enumerate(card_list):
            if c["card"] == card:
                card_list.pop(i)
                break
                
    def build_simple_list_tab(self, parent, data_list, entries_list, add_text):
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        for item in data_list:
            self.add_simple_list_row(scroll, entries_list, item)
            
        add_btn = ctk.CTkButton(parent, text=f"＋ {add_text}", command=lambda: self.add_simple_list_row(scroll, entries_list, ""))
        add_btn.pack(pady=10)
        
    def add_simple_list_row(self, parent, entries_list, text):
        row = ctk.CTkFrame(parent, fg_color="#2b2b2b", corner_radius=6, border_width=1, border_color="#444444")
        row.pack(fill="x", pady=2, padx=5)
        
        var = ctk.StringVar(value=text)
        entry = ctk.CTkEntry(row, textvariable=var)
        entry.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        def del_row():
            row.destroy()
            entries_list.remove((var, row))
            
        ctk.CTkButton(row, text="🗑️", width=35, fg_color="#a83232", hover_color="#802626", command=del_row).pack(side="right", padx=10)
        entries_list.append((var, row))
        
    def save_and_exit(self):
        new_time_limits = {}
        for c in self.domain_frames:
            domain = c["domain_var"].get().strip()
            if not domain:
                continue
                
            try:
                mins = int(c["min_var"].get().strip() or 0)
                secs = int(c["sec_var"].get().strip() or 0)
                max_seconds = (mins * 60) + secs
            except ValueError:
                self.error_lbl.configure(text=f"エラー: ドメイン '{domain}' の上限時間に数値以外が含まれています。")
                return
                
            allow_windows = []
            for svar, evar, _ in c["windows_list"]:
                st = svar.get().strip()
                et = evar.get().strip()
                if st and et:
                    import re
                    if not re.match(r'^\d{1,2}:\d{2}$', st) or not re.match(r'^\d{1,2}:\d{2}$', et):
                        self.error_lbl.configure(text=f"エラー: ドメイン '{domain}' の時間帯フォーマットが不正です (例: 09:00)。")
                        return
                    allow_windows.append({"start": st, "end": et})
                    
            new_time_limits[domain] = {
                "max_seconds": max_seconds,
                "allow_windows": allow_windows
            }
            
        new_block_list = [v.get().strip() for v, _ in self.block_entries if v.get().strip()]
        new_white_list = [v.get().strip() for v, _ in self.white_entries if v.get().strip()]
        
        new_config = {
            "WHITE_LIST": new_white_list,
            "TIME_LIMITS": new_time_limits,
            "BLOCK_LIST": new_block_list
        }
        
        try:
            save_config(new_config)
            
            # 保存後、即座にメインGUIと監視プロセスに設定を反映させるため、run.vbs経由でプロセスを再起動
            import subprocess
            vbs_path = os.path.join(os.path.dirname(BASE_DIR), "run.vbs")
            if os.path.exists(vbs_path):
                subprocess.Popen(
                    ["wscript.exe", vbs_path], 
                    creationflags=0x08000000, 
                    cwd=os.path.dirname(BASE_DIR)
                )
                
            self.destroy()
        except Exception as e:
            self.error_lbl.configure(text=f"保存に失敗しました: {e}")

if __name__ == "__main__":
    app = SettingsEditor()
    app.mainloop()
