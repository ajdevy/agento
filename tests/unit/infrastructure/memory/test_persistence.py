"""Tests for memory persistence."""

import tempfile
from pathlib import Path

import pytest

from agento.domain.ports.memory_port import MemoryEntry
from agento.infrastructure.memory.persistence import MemoryPersistence


@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def persistence(temp_dir):
    """Create a persistence instance."""
    return MemoryPersistence(storage_dir=temp_dir)


@pytest.fixture
def sample_entries():
    """Create sample memory entries."""
    return [
        MemoryEntry(id="1", content="Test content 1"),
        MemoryEntry(id="2", content="Test content 2"),
        MemoryEntry(id="3", content="Test content 3"),
    ]


class TestMemoryPersistence:
    """Test persistence functionality."""

    def test_save_and_load(self, persistence, sample_entries):
        """Test saving and loading memories."""
        result = persistence.save(sample_entries)
        assert result is True

        loaded = persistence.load()
        assert loaded is not None
        assert len(loaded) == 3

    def test_load_nonexistent(self, persistence):
        """Test loading nonexistent file."""
        loaded = persistence.load("nonexistent.json")
        assert loaded is None

    def test_exists(self, persistence, sample_entries):
        """Test checking if file exists."""
        assert persistence.exists() is False

        persistence.save(sample_entries)
        assert persistence.exists() is True

    def test_delete(self, persistence, sample_entries):
        """Test deleting a file."""
        persistence.save(sample_entries)
        assert persistence.exists() is True

        result = persistence.delete()
        assert result is True
        assert persistence.exists() is False

    def test_get_metadata(self, persistence, sample_entries):
        """Test getting metadata."""
        persistence.save(sample_entries)

        metadata = persistence.get_metadata()
        assert metadata is not None
        assert metadata.total_entries == 3

    def test_get_metadata_nonexistent(self, persistence):
        """Test getting metadata for nonexistent file."""
        metadata = persistence.get_metadata()
        assert metadata is None

    def test_list_files(self, persistence, sample_entries):
        """Test listing files."""
        persistence.save(sample_entries)
        persistence.save(sample_entries, "backup.json")

        files = persistence.list_files()
        assert "memory.json" in files
        assert "backup.json" in files

    def test_get_storage_size(self, persistence, sample_entries):
        """Test getting storage size."""
        persistence.save(sample_entries)

        size = persistence.get_storage_size()
        assert size > 0

    def test_clear_all(self, persistence, sample_entries):
        """Test clearing all files."""
        persistence.save(sample_entries)
        persistence.save(sample_entries, "backup.json")

        count = persistence.clear_all()
        assert count >= 2

    def test_backup(self, persistence, sample_entries):
        """Test creating a backup."""
        persistence.save(sample_entries)

        backup_name = persistence.backup()
        assert backup_name is not None

        backups = persistence.list_backups()
        assert backup_name in backups

    def test_restore(self, persistence, sample_entries):
        """Test restoring from backup."""
        persistence.save(sample_entries)
        backup_name = persistence.backup()

        persistence.delete()

        result = persistence.restore(backup_name)
        assert result is True

        loaded = persistence.load()
        assert loaded is not None
        assert len(loaded) == 3

    def test_restore_nonexistent(self, persistence):
        """Test restoring nonexistent backup."""
        result = persistence.restore("nonexistent.json")
        assert result is False

    def test_list_backups(self, persistence, sample_entries):
        """Test listing backups."""
        persistence.save(sample_entries)
        persistence.backup("memory_backup_1.json")
        persistence.backup("memory_backup_2.json")

        backups = persistence.list_backups()
        assert len(backups) >= 2


class TestStorageDirectoryCreation:
    """Test storage directory creation."""

    def test_creates_directory(self, temp_dir):
        """Test that directory is created if not exists."""
        new_dir = temp_dir / "new" / "nested" / "dir"
        persistence = MemoryPersistence(storage_dir=new_dir)

        assert new_dir.exists()
