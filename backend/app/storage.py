from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from .models import CustomData, CustomDataCreate


class JsonStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.custom_path = self.data_dir / "custom_data.json"
        self._lock = Lock()
        if not self.custom_path.exists():
            self.custom_path.write_text("[]", encoding="utf-8")

    def list_custom_data(self, algorithm_id: str | None = None) -> list[CustomData]:
        rows = self._read_rows()
        if algorithm_id:
            rows = [row for row in rows if row.get("algorithm_id") == algorithm_id]
        return [CustomData(**row) for row in rows]

    def create_custom_data(self, payload: CustomDataCreate) -> CustomData:
        with self._lock:
            rows = self._read_rows_unlocked()
            next_id = max((int(row["id"]) for row in rows), default=0) + 1
            row: dict[str, Any] = {
                "id": next_id,
                "algorithm_id": payload.algorithm_id,
                "name": payload.name,
                "input": payload.input,
                "created_at": datetime.now().isoformat(),
            }
            rows.append(row)
            self._write_rows_unlocked(rows)
            return CustomData(**row)

    def delete_custom_data(self, item_id: int) -> bool:
        with self._lock:
            rows = self._read_rows_unlocked()
            kept = [row for row in rows if int(row["id"]) != item_id]
            if len(kept) == len(rows):
                return False
            self._write_rows_unlocked(kept)
            return True

    def _read_rows(self) -> list[dict[str, Any]]:
        with self._lock:
            return self._read_rows_unlocked()

    def _read_rows_unlocked(self) -> list[dict[str, Any]]:
        try:
            content = self.custom_path.read_text(encoding="utf-8")
            data = json.loads(content)
        except json.JSONDecodeError:
            data = []
        if not isinstance(data, list):
            return []
        return [row for row in data if isinstance(row, dict)]

    def _write_rows_unlocked(self, rows: list[dict[str, Any]]) -> None:
        self.custom_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
