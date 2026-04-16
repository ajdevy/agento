"""Persistence layer for memory storage."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agento.domain.ports.memory_port import MemoryEntry


@dataclass
class StorageMetadata:
    """Storage metadata."""

    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    total_entries: int = 0
    storage_type: str = "json"


@dataclass
class MemorySnapshot:
    """Snapshot of memory state."""

    metadata: StorageMetadata
    entries: list[MemoryEntry]


class MemoryPersistence:
    """Persist memory to disk."""

    def __init__(
        self,
        storage_dir: Path | str | None = None,
        format: str = "json",
    ):
        if storage_dir is None:
            storage_dir = Path.home() / ".agento" / "memory"
        self.storage_dir = Path(storage_dir)
        self.format = format
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """Ensure storage directory exists."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        entries: list[MemoryEntry],
        filename: str = "memory.json",
    ) -> bool:
        """Save memory entries to disk."""
        try:
            path = self.storage_dir / filename

            metadata = StorageMetadata(
                total_entries=len(entries),
                last_updated=datetime.now(),
            )

            snapshot = MemorySnapshot(
                metadata=metadata,
                entries=entries,
            )

            data = {
                "metadata": {
                    "version": snapshot.metadata.version,
                    "created_at": snapshot.metadata.created_at.isoformat(),
                    "last_updated": snapshot.metadata.last_updated.isoformat(),
                    "total_entries": snapshot.metadata.total_entries,
                    "storage_type": snapshot.metadata.storage_type,
                },
                "entries": [
                    {
                        "id": entry.id,
                        "content": entry.content,
                        "metadata": entry.metadata,
                        "vector": entry.vector,
                    }
                    for entry in entries
                ],
            }

            with open(path, "w") as f:
                json.dump(data, f, indent=2)

            return True

        except OSError:
            return False

    def load(
        self,
        filename: str = "memory.json",
    ) -> list[MemoryEntry] | None:
        """Load memory entries from disk."""
        try:
            path = self.storage_dir / filename

            if not path.exists():
                return None

            with open(path) as f:
                data = json.load(f)

            entries = []
            for entry_data in data.get("entries", []):
                entry = MemoryEntry(
                    id=entry_data["id"],
                    content=entry_data["content"],
                    metadata=entry_data.get("metadata", {}),
                    vector=entry_data.get("vector"),
                )
                entries.append(entry)

            return entries

        except (OSError, json.JSONDecodeError, KeyError):
            return None

    def get_metadata(
        self,
        filename: str = "memory.json",
    ) -> StorageMetadata | None:
        """Get storage metadata."""
        try:
            path = self.storage_dir / filename

            if not path.exists():
                return None

            with open(path) as f:
                data = json.load(f)

            meta = data.get("metadata", {})
            return StorageMetadata(
                version=meta.get("version", "1.0"),
                created_at=datetime.fromisoformat(
                    meta.get("created_at", datetime.now().isoformat())
                ),
                last_updated=datetime.fromisoformat(
                    meta.get("last_updated", datetime.now().isoformat())
                ),
                total_entries=meta.get("total_entries", 0),
                storage_type=meta.get("storage_type", "json"),
            )

        except (OSError, json.JSONDecodeError, KeyError, ValueError):
            return None

    def delete(
        self,
        filename: str = "memory.json",
    ) -> bool:
        """Delete a memory file."""
        try:
            path = self.storage_dir / filename
            if path.exists():
                path.unlink()
                return True
            return False

        except OSError:
            return False

    def exists(
        self,
        filename: str = "memory.json",
    ) -> bool:
        """Check if memory file exists."""
        return (self.storage_dir / filename).exists()

    def list_files(self) -> list[str]:
        """List all memory files."""
        try:
            return [f.name for f in self.storage_dir.glob("*.json")]
        except OSError:
            return []

    def get_storage_size(self) -> int:
        """Get total storage size in bytes."""
        try:
            total = 0
            for path in self.storage_dir.glob("*.json"):
                total += path.stat().st_size
            return total
        except OSError:
            return 0

    def clear_all(self) -> int:
        """Clear all memory files."""
        count = 0
        try:
            for path in self.storage_dir.glob("*.json"):
                path.unlink()
                count += 1
        except OSError:
            pass
        return count

    def backup(
        self,
        backup_name: str | None = None,
    ) -> str | None:
        """Create a backup of current memory."""
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"memory_backup_{timestamp}.json"

        source = self.storage_dir / "memory.json"
        if not source.exists():
            return None

        try:
            dest = self.storage_dir / backup_name
            import shutil

            shutil.copy2(source, dest)
            return backup_name

        except OSError:
            return None

    def restore(
        self,
        backup_name: str,
        target_name: str = "memory.json",
    ) -> bool:
        """Restore from a backup."""
        source = self.storage_dir / backup_name
        if not source.exists():
            return False

        try:
            dest = self.storage_dir / target_name
            import shutil

            shutil.copy2(source, dest)
            return True

        except OSError:
            return False

    def list_backups(self) -> list[str]:
        """List available backups."""
        try:
            return [f.name for f in self.storage_dir.glob("memory_backup_*.json")]
        except OSError:
            return []
