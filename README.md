[English](README.md) | [日本語](docs/README_ja.md) | [简体中文](docs/README_zh.md)

# u_URLblock - Commercial Portable Edition

**u_URLblock** is a high-security, lightweight parental control and self-discipline web monitoring application for Windows. It provides real-time URL inspection, daily usage time tracking, and instant tab blocking across **Google Chrome**, **Microsoft Edge**, and **Mozilla Firefox**.

Designed for commercial deployment, `u_URLblock` runs inside a self-contained, isolated embedded Python runtime. It requires no administrative privileges, modifies no Windows registry settings, and leaves zero footprint on your system global environment variables.

---

## 🌟 Key Features

1. **Multi-Browser Real-Time Inspection**:
   - Accurately inspects active URLs across **Chrome**, **Edge**, and **Firefox** in real-time (sub-50ms response time) using Windows UI Automation.
2. **Dual-Layer Protection**:
   - **Daily Time Limits**: Automatically tracks cumulative usage per domain (e.g., YouTube, Instagram, TikTok). When the time limit expires, active browser tabs are immediately closed.
   - **Absolute Blocklist**: Instantaneously closes tabs attempting to access restricted web domains or keywords.
3. **Smart Silent Launcher**:
   - Launches via a native VBScript wrapper (`run.vbs`), completely eliminating command prompt console flashes.
4. **Self-Healing Multi-Process Architecture**:
   - Employs disguised background watchdog workers (`WinLogonAssist`, `AudioDG_helper`, `FontHost_worker`, `SpoolerSub_helper`) with mutex locks and automatic process resurrection to prevent accidental termination.
5. **Modern High-DPI Dashboard**:
   - Features a sleek, dark-themed floating widget built with CustomTkinter, fully DPI-aware for crisp rendering on high-resolution displays.
6. **Encrypted Anti-Tamper Tracking**:
   - Usage data is compressed (zlib), cyclic XOR encrypted, base64 encoded, and verified via dual SHA-256 and MD5 cryptographic signatures.

---

## 🚀 Quick Start Guide

### 1. Initial Setup (Run Once)
Before running the application for the first time, initialize the portable environment:
1. Double-click **`setup.bat`** in the root directory.
2. The installer will automatically download the Windows Embeddable Python package, configure site libraries, extract required GUI dependencies, and install all packages into an isolated `bin/` directory.

### 2. Daily Launching
To start the application for daily use:
1. Double-click **`run.vbs`** in the root directory.
2. The application will start silently in the background without opening any command prompt windows. The floating **Time Keeper** dashboard will appear on your screen.

---

## ⚙️ Configuration (`config.json`)

You can customize your filtering rules by editing **`config.json`** located in the root directory:

```json
{
  "WHITE_LIST": [
    "chiebukuro.yahoo.co.jp"
  ],
  "TIME_LIMITS": {
    "instagram.com": 180,
    "x.com": 180,
    "youtube.com/shorts": 180,
    "tiktok.com": 600,
    "youtube.com": 1800
  },
  "BLOCK_LIST": [
    "crazygames.com",
    "streamtape.com",
    "duckduckgo.com"
  ]
}
```

- **`TIME_LIMITS`**: Specify domain names and their maximum allowed daily browsing time in **seconds** (e.g., `1800` = 30 minutes).
- **`BLOCK_LIST`**: Specify domains or keywords that should be blocked instantly upon access.
- **`WHITE_LIST`**: Specify trusted domains that bypass time tracking and blocklist checks.

---

## 🗑️ Uninstallation

Because `u_URLblock` operates entirely within its self-contained portable directory, uninstallation is clean and simple:
1. Terminate running background processes via Task Manager or reboot your system.
2. Delete the `u_URLblock` project folder.
3. Your PC remains 100% clean—no registry entries, services, or environment variables are left behind.

---

## 📁 Commercial Directory Structure

```text
u_URLblock/
 ├─ setup.bat          # One-time automated installer script
 ├─ run.vbs            # Daily silent background launcher
 ├─ config.json        # User-accessible configuration rules
 ├─ README.md          # English manual (This document)
 ├─ docs/              # Additional localized manuals (Japanese, Chinese)
 ├─ bin/               # Isolated embeddable Python runtime (Auto-generated)
 └─ core/              # Hidden application source code and core logic
     ├─ main.pyw       # Application controller & watchdog initiator
     ├─ data_manager.py # Encrypted storage & config management
     ├─ ui.py          # CustomTkinter DPI-aware overlay GUI
     ├─ monitor.pyw    # Multi-browser real-time URL inspection engine
     ├─ watcher.pyw    # Background process resurrection monitor
     ├─ system_guard.pyw # WMI/Mutex system guard
     └─ win_utils.py   # Windows API helper utilities
```
