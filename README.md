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

## 🛡️ Dual-Account Isolation & Psychological Friction Architecture

`u_URLblock` is engineered not merely as a software blocklist, but as a physical and psychological intervention system. By combining **Windows Account Privilege Isolation** with **Psychological Friction (Cognitive Effort)**, it effectively cures digital addiction and impulsive browsing (SNS, Shorts, YouTube binges).

### 1. Recommended Two-Account (Profile) Deployment
To prevent an end-user (or yourself during a moment of weakness) from bypassing the daily time limits, set up two isolated Windows user profiles on the PC:

1. **Administrators Account**:
   - Set the password for this account to an **extremely long, complex 100-character random password**. Seal or hide this password somewhere difficult to access (e.g., written on paper in a locked safe, held by a trusted friend or family member, or inside a complex password manager).
   - Use this account exclusively for initial installation, configuration rule editing (`config.json`), and Windows Task Scheduler registration.
2. **Standard User Account**:
   - The end-user must log into Windows using this restricted **Standard User** profile for all daily work, studying, and browsing.
   - Without administrative privileges, standard users cannot terminate protected system-guard processes via Task Manager or alter automated scheduled tasks.

### 2. The Power of the "100-Character Password" Psychological Barrier
If an end-user exhausts their daily time limit (e.g., 5 minutes of YouTube) and feels an impulsive dopamine urge to keep watching, they are forced to confront an overwhelming psychological barrier. To bypass the restriction, they must endure the following tedious process:

1. Log out or switch user accounts from their daily Standard User profile.
2. Manually type the grueling 100-character Administrator password character-by-character into the Windows login screen without making a typo.
3. Open Task Manager with elevated privileges and forcefully destroy or kill the running `u_URLblock` watchdog processes and scheduled tasks.
4. Switch back to the Standard User profile and re-launch the browser.

This **high-friction mechanism** makes the effort required to cheat the system so exhausting and annoying that it breaks the impulsive dopamine loop, ensuring long-term self-discipline.

### 3. Administrator Task Scheduler Registration (Automated Persistence)
To guarantee that the monitoring engine launches automatically whenever the Standard User logs in—and cannot be stopped or disabled by the user—an Administrator must register `run.vbs` as an elevated job in the **Windows Task Scheduler**:

1. **Open Task Scheduler**:
   - Log into the Administrators account and press `Win + R`, type `taskschd.msc`, and press Enter.
2. **Create Task**:
   - Click **Create Task...** in the right-hand Actions panel.
   - **Name**: `u_URLblock_SystemGuard` (or any custom name).
3. **Configure Triggers**:
   - Go to the **Triggers** tab, click **New...**, and set the trigger to **At log on** (or **At startup**).
4. **Configure Actions**:
   - Go to the **Actions** tab, click **New...**, and select **Start a program**.
   - **Program/script**: `wscript.exe`
   - **Add arguments (optional)**: `//NoLogo "C:\Path\to\u_URLblock\run.vbs"` *(Replace with your absolute path to run.vbs)*.
   - **Start in (optional)**: `C:\Path\to\u_URLblock\` *(Must be the absolute path to the project root directory)*.
5. **Elevate Privileges (Critical)**:
   - On the **General** tab, check the box labeled **Run with highest privileges**.
   - This ensures the background watchdog processes run silently with full administrative elevation even when the active session belongs to a Standard User, rendering termination attempts impossible.

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

## 🔒 Runtime State & Security (`authenticated_users_kakikomi_true`)

During execution, `u_URLblock` automatically generates a runtime directory named **`authenticated_users_kakikomi_true/`** in the project root. This directory plays a vital architectural and security role:

1. **Non-Admin (Unprivileged) Write Access**:
   - In Windows environments (including multi-user or restricted corporate/school PCs), standard users ("Authenticated Users") require explicit write permissions ("kakikomi true" / 書き込み可能) to record usage logs and IPC status files without triggering User Account Control (UAC) administrative prompts.
2. **Encrypted & Anti-Tamper Storage**:
   - This directory stores live tracking data (`usage_log.json`), real-time monitoring status (`status.txt`), and bytecode cache (`__pycache__`).
   - Even though standard users have write access to the folder, the usage logs inside are compressed (zlib), cyclic XOR encrypted, base64 encoded, and protected by dual SHA-256/MD5 cryptographic checksums. Any manual tampering immediately invalidates the log and triggers a penalty timeout state.
3. **Automated Folder Locking & Hiding**:
   - The application automatically generates a hidden lock file (`system.lock`) and applies Windows attributes to secure runtime communication between background watchdog processes.

### 🔐 Administrator Guide: Setting NTFS Security Permissions
To complete the dual-account fortress architecture, an Administrator must configure Windows NTFS security permissions so that **standard users cannot modify or delete application files, but are explicitly permitted to write to `authenticated_users_kakikomi_true`**.

#### Method A: Using Command Line / `icacls` (Recommended)
Open an elevated Command Prompt or PowerShell as Administrator and execute the following commands *(replace paths with your actual installation directory)*:

```powershell
# 1. Restrict standard users (Authenticated Users) to Read & Execute (RX) across the entire app (prevents deletion/tampering)
icacls "C:\path\to\u_URLblock" /grant:r "Authenticated Users":(RX) /t

# 2. Grant explicit Modify (M) / Write (W) permissions ONLY to the runtime log directory
icacls "C:\path\to\u_URLblock\authenticated_users_kakikomi_true" /grant:r "Authenticated Users":(M)
```

#### Method B: Using Windows Explorer GUI
1. Right-click the root `u_URLblock` folder in Windows Explorer ➔ **Properties** ➔ **Security** tab. Set permissions for `Users` or `Authenticated Users` to **Read & execute, List folder contents, Read** only *(uncheck Write and Modify)*.
2. Next, right-click the **`authenticated_users_kakikomi_true`** subdirectory ➔ **Properties** ➔ **Security** tab ➔ Click **Edit...**.
3. Select **`Authenticated Users`** (or `Users`), check the **Allow** box for **Modify** and **Write**, and click Apply ➔ OK.

This establishes an unbreakable security fortress: standard users are physically blocked by Windows NTFS from deleting or tampering with the monitoring engine, while remaining fully capable of logging daily browsing hours in the designated runtime folder.

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
 ├─ authenticated_users_kakikomi_true/ # Runtime logs, IPC status, & encrypted storage (Auto-generated)
 └─ core/              # Hidden application source code and core logic
     ├─ main.pyw       # Application controller & watchdog initiator
     ├─ data_manager.py # Encrypted storage & config management
     ├─ ui.py          # CustomTkinter DPI-aware overlay GUI
     ├─ monitor.pyw    # Multi-browser real-time URL inspection engine
     ├─ watcher.pyw    # Background process resurrection monitor
     ├─ system_guard.pyw # WMI/Mutex system guard
     └─ win_utils.py   # Windows API helper utilities
```
