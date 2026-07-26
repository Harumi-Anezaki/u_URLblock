"""
data_manager.py

Handles secure application configuration loading, folder hiding/locking via Windows file attributes,
and encrypted, checksum-verified usage time tracking with thread-safe file locks.
"""

import os
import json
import datetime
import random
import hashlib
import base64
import zlib
import subprocess
import filelock
from typing import Dict, Any, Tuple, Optional

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR: str = os.path.dirname(BASE_DIR)
WRITABLE_DIR: str = os.path.join(ROOT_DIR, "authenticated_users_kakikomi_true")
os.makedirs(WRITABLE_DIR, exist_ok=True)

JSON_FILE: str = "usage_log.json"
CONFIG_FILE: str = "config.json"


def load_config() -> Dict[str, Any]:
    """
    Loads the user configuration from config.json located in the project root directory.

    Returns:
        Dict[str, Any]: A dictionary containing WHITE_LIST, TIME_LIMITS, and BLOCK_LIST.
    """
    config_path = os.path.join(ROOT_DIR, CONFIG_FILE)
    if not os.path.exists(config_path):
        return {"WHITE_LIST": [], "TIME_LIMITS": {}, "BLOCK_LIST": []}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"WHITE_LIST": [], "TIME_LIMITS": {}, "BLOCK_LIST": []}


class FolderLocker:
    """
    Secures and hides the writable runtime directory by writing a lock file and setting hidden attributes.
    """

    def __init__(self) -> None:
        """Initializes the FolderLocker and applies lock attributes."""
        self.lock_path: str = os.path.join(WRITABLE_DIR, "system.lock")
        self.file_handle: Optional[Any] = None
        self.lock()

    def lock(self) -> None:
        """Creates the lock file and sets the Windows hidden attribute."""
        try:
            self.file_handle = open(self.lock_path, "w")
            self.file_handle.write("LOCKED")
            self.file_handle.flush()
            subprocess.run(["attrib", "+h", self.lock_path], creationflags=0x08000000)
        except BaseException:
            pass


class UsageManager:
    """
    Manages daily domain usage tracking with XOR/zlib/base64 encryption, dual checksum verification,
    and process-safe file locking.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Initializes the UsageManager with time limit rules from the configuration.

        Args:
            config (Dict[str, Any]): Application configuration dictionary.
        """
        self.filepath: str = os.path.join(WRITABLE_DIR, JSON_FILE)
        self.lock: filelock.FileLock = filelock.FileLock(self.filepath + ".lock")
        self.time_limits: Dict[str, int] = config.get("TIME_LIMITS", {})
        self.secret_key1: str = "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8"
        self.secret_key2: str = "Z9Y8X7W6-V5U4-T3S2-R1Q0-P9O8N7M6L5K4"
        self.data: Dict[str, Any] = self.load_data()

    def _xor_crypt(self, text: str, key: str) -> str:
        """
        Performs cyclic XOR encryption/decryption on a string using a secret key.

        Args:
            text (str): Input string.
            key (str): Secret encryption key.

        Returns:
            str: XOR encrypted/decrypted string.
        """
        return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

    def _calculate_checksums(self, encoded_data_str: str) -> Tuple[str, str]:
        """
        Calculates SHA-256 and MD5 cryptographic checksums for data integrity validation.

        Args:
            encoded_data_str (str): Base64 encoded payload string.

        Returns:
            Tuple[str, str]: A tuple of (SHA-256 hash, MD5 hash).
        """
        sha_hash = hashlib.sha256((encoded_data_str + self.secret_key1).encode('utf-8')).hexdigest()
        md5_hash = hashlib.md5((encoded_data_str + self.secret_key2).encode('utf-8')).hexdigest()
        return sha_hash, md5_hash

    def load_data(self) -> Dict[str, Any]:
        """
        Safely loads, decrypts, and verifies today's domain usage time tracking data.
        If data is tampered or from a previous day, resets to default or penalty state.

        Returns:
            Dict[str, Any]: Tracking dictionary containing 'date' and 'usage'.
        """
        today_str = datetime.date.today().isoformat()
        default_data = {"date": today_str, "usage": {k: 0 for k in self.time_limits}}
        penalty_data = {"date": today_str, "usage": {k: 999999 for k in self.time_limits}}

        def reset_and_save(is_penalty: bool = False) -> Dict[str, Any]:
            self.data = penalty_data if is_penalty else default_data
            self.save_data()
            return self.data

        try:
            with self.lock.acquire(timeout=2):
                if not os.path.exists(self.filepath):
                    return reset_and_save(is_penalty=True)

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
                except Exception:
                    return reset_and_save(is_penalty=True)
        except filelock.Timeout:
            return reset_and_save(is_penalty=True)

    def save_data(self) -> None:
        """
        Compresses, encrypts, signs, and saves usage time data to disk under a file lock.
        """
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

            with self.lock.acquire(timeout=2):
                with open(self.filepath, 'w', encoding='utf-8') as f:
                    json.dump(content_to_save, f)
                    f.flush()
                    os.fsync(f.fileno())
        except BaseException:
            pass

    def add_usage(self, domain: str, seconds: float) -> None:
        """
        Adds elapsed browsing seconds to a monitored domain and commits to secure storage.

        Args:
            domain (str): The domain name being monitored.
            seconds (float): Elapsed time in seconds to add.
        """
        self.data = self.load_data()
        today_str = datetime.date.today().isoformat()
        if self.data["date"] != today_str:
            self.data = {"date": today_str, "usage": {k: 0 for k in self.time_limits}}

        if domain not in self.data["usage"]:
            self.data["usage"][domain] = 0

        self.data["usage"][domain] += seconds
        self.save_data()

    def get_usage(self, domain: str) -> int:
        """
        Retrieves the total accumulated usage seconds for a domain today.

        Args:
            domain (str): The monitored domain name.

        Returns:
            int: Total usage time in seconds.
        """
        return int(self.data["usage"].get(domain, 0))
