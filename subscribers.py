"""
subscribers.py – Persistent subscriber store backed by a JSON file.

Users who run /subscribe are added; /unsubscribe removes them.
The list is persisted so it survives bot restarts.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_PATH = Path(os.getenv("SUBSCRIBERS_FILE", "subscribers.json"))


class SubscriberStore:
    """Thread-safe (asyncio single-thread) JSON-backed set of chat IDs."""

    def __init__(self, path: Path = _DEFAULT_PATH) -> None:
        self._path = path
        self._ids: set[int] = self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> set[int]:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                return set(int(x) for x in data)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not read %s: %s – starting fresh.", self._path, exc)
        return set()

    def _save(self) -> None:
        try:
            self._path.write_text(json.dumps(sorted(self._ids)))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to save subscribers to %s: %s", self._path, exc)

    # ── Public API ────────────────────────────────────────────────────────────

    def add(self, chat_id: int) -> bool:
        """Add a subscriber.  Returns True if it was newly added."""
        if chat_id in self._ids:
            return False
        self._ids.add(chat_id)
        self._save()
        return True

    def remove(self, chat_id: int) -> bool:
        """Remove a subscriber.  Returns True if it was present."""
        if chat_id not in self._ids:
            return False
        self._ids.discard(chat_id)
        self._save()
        return True

    def all(self) -> list[int]:
        """Return a snapshot list of all subscribed chat IDs."""
        return list(self._ids)

    def __contains__(self, chat_id: int) -> bool:
        return chat_id in self._ids

    def __len__(self) -> int:
        return len(self._ids)


# Module-level singleton used by main.py
store = SubscriberStore()
