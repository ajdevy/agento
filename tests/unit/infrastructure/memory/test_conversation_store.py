"""Tests for conversation store."""

import pytest

from agento.infrastructure.memory.conversation_store import (
    Conversation,
    ConversationMessage,
    ConversationStore,
    MessageRole,
)


@pytest.fixture
def store():
    """Create a fresh conversation store."""
    return ConversationStore(max_conversations=10)


class TestConversationStore:
    """Test conversation store functionality."""

    def test_create_conversation(self, store):
        """Test creating a conversation."""
        conversation = store.create_conversation("Test Conversation")

        assert conversation is not None
        assert conversation.title == "Test Conversation"
        assert conversation.message_count == 0

    def test_get_conversation(self, store):
        """Test getting a conversation."""
        created = store.create_conversation("Test")
        retrieved = store.get_conversation(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id

    def test_get_nonexistent_conversation(self, store):
        """Test getting nonexistent conversation."""
        result = store.get_conversation("nonexistent-id")
        assert result is None

    def test_delete_conversation(self, store):
        """Test deleting a conversation."""
        created = store.create_conversation("Test")
        result = store.delete_conversation(created.id)

        assert result is True
        assert store.get_conversation(created.id) is None

    def test_add_message(self, store):
        """Test adding a message."""
        conversation = store.create_conversation()
        message = store.add_message(
            conversation.id,
            MessageRole.USER,
            "Hello",
        )

        assert message is not None
        assert message.content == "Hello"
        assert message.role == MessageRole.USER

    def test_get_messages(self, store):
        """Test getting messages."""
        conversation = store.create_conversation()
        store.add_message(conversation.id, MessageRole.USER, "Hello")
        store.add_message(conversation.id, MessageRole.ASSISTANT, "Hi there")

        messages = store.get_messages(conversation.id)
        assert len(messages) == 2

    def test_get_messages_with_limit(self, store):
        """Test getting messages with limit."""
        conversation = store.create_conversation()
        for i in range(5):
            store.add_message(conversation.id, MessageRole.USER, f"Message {i}")

        messages = store.get_messages(conversation.id, limit=3)
        assert len(messages) == 3

    def test_search_conversations(self, store):
        """Test searching conversations."""
        store.create_conversation("Python tutorial")
        store.create_conversation("JavaScript guide")

        results = store.search_conversations("Python")
        assert len(results) == 1
        assert "Python" in results[0].title

    def test_search_by_message_content(self, store):
        """Test searching by message content."""
        conv = store.create_conversation("Test")
        store.add_message(conv.id, MessageRole.USER, "Important information")

        results = store.search_conversations("Important")
        assert len(results) == 1

    def test_archive_conversation(self, store):
        """Test archiving a conversation."""
        conversation = store.create_conversation()
        result = store.archive_conversation(conversation.id)

        assert result is True
        assert conversation.is_archived is True

    def test_unarchive_conversation(self, store):
        """Test unarchiving a conversation."""
        conversation = store.create_conversation()
        store.archive_conversation(conversation.id)

        result = store.unarchive_conversation(conversation.id)
        assert result is True
        assert conversation.is_archived is False

    def test_get_active_conversations(self, store):
        """Test getting active conversations."""
        active1 = store.create_conversation("Active 1")
        active2 = store.create_conversation("Active 2")
        archived = store.create_conversation("Archived")
        store.archive_conversation(archived.id)

        active = store.get_active_conversations()
        assert len(active) == 2
        assert all(not c.is_archived for c in active)

    def test_get_archived_conversations(self, store):
        """Test getting archived conversations."""
        store.create_conversation("Active")
        archived = store.create_conversation("Archived")
        store.archive_conversation(archived.id)

        archived_list = store.get_archived_conversations()
        assert len(archived_list) == 1
        assert archived_list[0].is_archived is True

    def test_clear_all(self, store):
        """Test clearing all conversations."""
        store.create_conversation("Conv 1")
        store.create_conversation("Conv 2")

        store.clear_all()

        assert len(store.get_all_conversations()) == 0

    def test_get_stats(self, store):
        """Test getting statistics."""
        conv = store.create_conversation()
        store.add_message(conv.id, MessageRole.USER, "Hello")
        store.add_message(conv.id, MessageRole.ASSISTANT, "Hi")

        stats = store.get_stats()
        assert stats.total_conversations == 1
        assert stats.total_messages == 2
        assert stats.total_users == 1
        assert stats.total_assistants == 1

    def test_export_conversation(self, store):
        """Test exporting a conversation."""
        conversation = store.create_conversation("Export Test")
        store.add_message(conversation.id, MessageRole.USER, "Hello")

        exported = store.export_conversation(conversation.id)
        assert exported is not None
        assert exported["title"] == "Export Test"

    def test_import_conversation(self, store):
        """Test importing a conversation."""
        data = {
            "id": "test-id",
            "title": "Imported",
            "messages": [],
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "metadata": {},
            "is_archived": False,
            "message_count": 0,
        }

        imported = store.import_conversation(data)
        assert imported is not None
        assert imported.title == "Imported"

    def test_max_conversations_limit(self):
        """Test max conversations limit."""
        store = ConversationStore(max_conversations=2)
        store.create_conversation("Conv 1")
        store.create_conversation("Conv 2")
        store.create_conversation("Conv 3")

        assert len(store.get_all_conversations()) == 2


class TestConversation:
    """Test Conversation model."""

    def test_add_message(self):
        """Test adding a message to conversation."""
        conv = Conversation(title="Test")
        message = conv.add_message(MessageRole.USER, "Hello")

        assert len(conv.messages) == 1
        assert message.content == "Hello"

    def test_get_messages_by_role(self):
        """Test getting messages by role."""
        conv = Conversation(title="Test")
        conv.add_message(MessageRole.USER, "User msg")
        conv.add_message(MessageRole.ASSISTANT, "Assistant msg")

        user_msgs = conv.get_messages_by_role(MessageRole.USER)
        assert len(user_msgs) == 1

    def test_get_last_n_messages(self):
        """Test getting last N messages."""
        conv = Conversation(title="Test")
        for i in range(5):
            conv.add_message(MessageRole.USER, f"Message {i}")

        last_3 = conv.get_last_n_messages(3)
        assert len(last_3) == 3


class TestConversationMessage:
    """Test ConversationMessage model."""

    def test_create_message(self):
        """Test creating a message."""
        msg = ConversationMessage(role=MessageRole.USER, content="Test")

        assert msg.content == "Test"
        assert msg.role == MessageRole.USER
        assert msg.id is not None
