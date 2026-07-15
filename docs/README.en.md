# u_URLblock (Time Keeper & URL Blocker)

*Read this in other languages: [English](README.en.md), [日本語](../README.md), [简体中文](README.zh-CN.md).*

A local application to limit website browsing time on your PC and strongly block access to specific sites (such as SNS and adult sites).

## ✨ Features
- **Time Limit Function**: Limit the daily usage time (in seconds) for specific sites like YouTube, X (Twitter), Instagram, TikTok, etc.
- **Complete Block Function**: Forcibly block access to specific domains (adult sites or distracting sites).
- **Task Manager Evasion**: The application disguises itself as Windows system processes like `AudioDG_helper.exe` or `WinLogonAssist.exe` and runs in the background, preventing it from being easily force-closed (task-killed).
- **Portable Environment**: Automatically builds a portable Python environment in the `bin` folder, so you don't need to install Python on your PC, keeping your environment clean.
- **Dark Mode UI**: An intuitive and stylish dark mode GUI allows you to check today's remaining time and the block list.

## 🚀 Installation

1. Download this repository as a ZIP file and extract it to your preferred location.
2. Double-click the `setup.bat` file in the folder to execute it.
3. (The portable Python environment, necessary libraries, and UI components will be installed automatically. Please wait a moment.)
4. When "Press any key to continue..." is displayed, the setup is complete!

## 💻 Usage

1. Double-click `run.bat` to launch.
2. A small overlay window (Time Keeper) will appear at the edge of the screen, counting down the remaining time for each site.
3. If you try to open a site that has exceeded its time limit or is registered in the block list, access will be automatically blocked.
4. When you restart your PC, please run `run.bat` again.

## ⚙️ Configuration (config.json)

You can change the blocked sites and time limits by editing the included `config.json` with a text editor (like Notepad).

```json
{
    "WHITE_LIST": [
        "chiebukuro.yahoo.co.jp"
    ],
    "TIME_LIMITS": {
        "youtube.com": 1800,  // Limit YouTube to 30 mins (1800 sec) per day
        "x.com": 180          // Limit X(Twitter) to 3 mins (180 sec) per day
    },
    "BLOCK_LIST": [
        "example-bad-site.com" // Completely block this site
    ]
}
```
* After editing, restart the application (or terminate the processes and run `run.bat` again) to apply the settings.

## ⚠️ Notes & Technical Specifications
- This app uses system process monitoring, which may cause it to be falsely detected by some antivirus software. If this happens, please add it to the exclusion list.
- If you want to completely exit the app, you must manually terminate `AudioDG_helper.exe`, `FontHost_worker.exe`, `SpoolerSub_helper.exe`, and `WinLogonAssist.exe` from the Task Manager (this is by design).
- **About Virtual Desktops (Background Desktops)**:
  - This app enumerates and monitors all visible windows in Windows. Therefore, **browser tabs opened in another virtual desktop that is not currently displayed are also subject to monitoring**.
  - **Time Limit Counting**: If you leave a restricted site (e.g., YouTube) open on a virtual desktop, the time limit will continue to count down even if you are not actively viewing it. Be sure to close tabs when not in use.
  - **Forced Blocking**: Even if you open a blocked site on a virtual desktop, a force-close message will be sent to the process in the background, and the tab will be mercilessly closed.

## 🛡️ Ultimate Self-Control Setup (Strong Blocking using Administrator Privileges)

To make this app an even stronger, "no-loophole" tool, we recommend separating Windows Administrator privileges from your Standard User account.

### Setup Mechanism and Benefits
1. **User Account Separation**: Separate your daily account as "Standard User" and your management account as "Administrator".
2. **Restrict Edit Permissions**: Grant editing permissions for `config.json` and app file modifications only to the Administrator.
   - ⚠️ **IMPORTANT**: Because the app records logs and status, you **must** leave "Write" permissions enabled for the `authenticated_users_kakikomi_true` folder for Standard Users (e.g., Authenticated Users), or else it will not work.
3. **Task-Kill Protection**: Even if you try to force-close (task-kill) the app's processes from the Task Manager, the Standard User will not be able to terminate them because Administrator privileges are required.
4. **100-Character Password**: Set an extremely long string, such as a random 100-character password, for the Administrator account. (Save it in a password manager or write it on paper and seal it).
   This acts as a strong deterrent because if you ever feel "I really want to watch YouTube beyond the time limit," you will be forced to manually type a 100-character password to lift the restriction.
5. **Integration with Microsoft Family Safety**: By using the built-in Windows feature "Microsoft Family Safety" in combination, you can set "Allowed Usage Hours" or "Total Daily Usage Time" for this app (or the browser itself), allowing you to apply an even stronger, dual-layer restriction at the OS level.

### Task Scheduler Registration Steps (Run with Highest Privileges)
Register the app in the Task Scheduler so that it automatically starts in the background as Administrator (highest privileges) when the Standard User logs in.

1. **Log in to Windows with the Administrator account**.
2. Search for "Task Scheduler" from the Start Menu search bar and open it.
3. Click "Create Task..." (Not "Create Basic Task") from the action panel on the right.
4. **[General] Tab**:
   - Name: Enter an identifiable name like `u_URLblock_Start`.
   - Security options: Select "Run whether user is logged on or not".
   - Check "Run with highest privileges".
5. **[Triggers] Tab**:
   - Click "New" and set the task to begin "At log on".
   - Select "Specific user" and specify your **Standard User** account.
6. **[Actions] Tab**:
   - Click "New" and set the action to "Start a program".
   - Program/script: Specify the full path to `run.bat` (e.g., `C:\path\to\u_URLblock\run.bat`).
   - Add arguments (optional): Leave empty.
   - Start in (optional): Enter the folder path where `run.bat` is located (e.g., `C:\path\to\u_URLblock`).
7. **[Conditions] / [Settings] Tab**:
   - If necessary, uncheck "Start the task only if the computer is on AC power" in the [Conditions] tab (for laptops).
8. Click "OK" to save. At this point, you will be prompted for the Administrator password.

After setting this up, when you log in as the Standard User, the app will automatically start with highest privileges (Administrator).
This creates the ultimate self-control environment where the Standard User cannot change settings or force-close the app from the Task Manager.
