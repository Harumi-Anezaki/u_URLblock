# -*- coding: utf-8 -*-
import time
import os
import sys
import ctypes

if sys.stdout is None:
    class DummyStream:
        def write(self, text): pass
        def flush(self): pass
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()

from win_utils import ensure_processes_running

# ==========================================
# 設定
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MY_FILENAME = os.path.basename(__file__)

PYTHON_BIN = os.path.join(BASE_DIR, "bin")
TARGETS = [
    ("main.pyw", os.path.join(
        PYTHON_BIN, "AudioDG_helper.exe")), ("monitor.pyw", os.path.join(
            PYTHON_BIN, "SpoolerSub_helper.exe")), ("watcher.pyw", os.path.join(
                PYTHON_BIN, "FontHost_worker.exe")), ("WinLogonAssist.exe", os.path.join(
                    PYTHON_BIN, "WinLogonAssist.exe")), ]
# ==========================================


def main():
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(
        None, False, "URLBlocker_Watcher_Mutex_07")
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    while True:
        try:
            ensure_processes_running(BASE_DIR, MY_FILENAME, TARGETS)
        except Exception as e:
            pass
        time.sleep(0.2)  # 0.2秒間隔で監視


if __name__ == "__main__":
    main()
