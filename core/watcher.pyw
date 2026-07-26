"""
watcher.pyw

Background watchdog worker. Periodically checks running system security processes
and restarts any terminated processes to maintain high availability and self-healing.
"""

import time
import os
import sys
import ctypes
from typing import List, Tuple

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if sys.stdout is None:
    class DummyStream:
        def write(self, text: str) -> None: pass
        def flush(self) -> None: pass
    sys.stdout = DummyStream()
    sys.stderr = DummyStream()

from win_utils import ensure_processes_running

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR: str = os.path.dirname(BASE_DIR)
MY_FILENAME: str = os.path.basename(__file__)

PYTHON_BIN: str = os.path.join(ROOT_DIR, "bin")
TARGETS: List[Tuple[str, str]] = [
    ("main.pyw", os.path.join(PYTHON_BIN, "AudioDG_helper.exe")),
    ("monitor.pyw", os.path.join(PYTHON_BIN, "SpoolerSub_helper.exe")),
    ("watcher.pyw", os.path.join(PYTHON_BIN, "FontHost_worker.exe")),
    ("system_guard.pyw", os.path.join(PYTHON_BIN, "WinLogonAssist.exe")),
]


def main() -> None:
    """
    Main watchdog loop. Acquires process mutex and continuously checks process vitality.
    """
    ERROR_ALREADY_EXISTS = 183
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "URLBlocker_Watcher_Mutex_07")  # noqa: F841
    if ctypes.windll.kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return

    while True:
        try:
            ensure_processes_running(BASE_DIR, MY_FILENAME, TARGETS)
        except Exception:
            pass
        time.sleep(0.2)


if __name__ == "__main__":
    main()
