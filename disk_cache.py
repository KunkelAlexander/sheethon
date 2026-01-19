# disk_cache.py
import json
import os
import threading
from typing import Any, Dict, Optional


class DiskCache:
    def __init__(self, path: str):
        self.path = path
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load full JSON dict from disk into memory."""
        if not os.path.exists(self.path):
            return

        with self._lock:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f) or {}
            except Exception:
                # If file is corrupted / empty, just start fresh
                self._cache = {}

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in memory and rewrite the full cache to disk."""
        with self._lock:
            self._cache[key] = value
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f)
