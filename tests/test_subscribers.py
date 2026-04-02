"""
tests/test_subscribers.py – Unit tests for the SubscriberStore.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from subscribers import SubscriberStore


class TestSubscriberStore(unittest.TestCase):
    def _store(self) -> tuple[SubscriberStore, Path]:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            tmp = Path(f.name)
        return SubscriberStore(path=tmp), tmp

    # ── add / remove ──────────────────────────────────────────────────────────

    def test_add_new_subscriber(self):
        store, _ = self._store()
        self.assertTrue(store.add(111))
        self.assertIn(111, store)

    def test_add_duplicate_returns_false(self):
        store, _ = self._store()
        store.add(111)
        self.assertFalse(store.add(111))

    def test_remove_existing_subscriber(self):
        store, _ = self._store()
        store.add(111)
        self.assertTrue(store.remove(111))
        self.assertNotIn(111, store)

    def test_remove_nonexistent_returns_false(self):
        store, _ = self._store()
        self.assertFalse(store.remove(999))

    def test_len(self):
        store, _ = self._store()
        store.add(1)
        store.add(2)
        store.add(3)
        self.assertEqual(len(store), 3)

    # ── persistence ───────────────────────────────────────────────────────────

    def test_persists_after_add(self):
        store, path = self._store()
        store.add(42)
        store2 = SubscriberStore(path=path)
        self.assertIn(42, store2)

    def test_persists_after_remove(self):
        store, path = self._store()
        store.add(42)
        store.remove(42)
        store2 = SubscriberStore(path=path)
        self.assertNotIn(42, store2)

    def test_loads_existing_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump([10, 20, 30], f)
            path = Path(f.name)
        store = SubscriberStore(path=path)
        self.assertEqual(sorted(store.all()), [10, 20, 30])

    def test_handles_corrupt_file_gracefully(self):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write("not valid json{{")
            path = Path(f.name)
        store = SubscriberStore(path=path)   # should not raise
        self.assertEqual(len(store), 0)

    # ── all() ─────────────────────────────────────────────────────────────────

    def test_all_returns_snapshot(self):
        store, _ = self._store()
        store.add(1)
        store.add(2)
        snapshot = store.all()
        store.add(3)
        self.assertNotIn(3, snapshot)


if __name__ == "__main__":
    unittest.main()
