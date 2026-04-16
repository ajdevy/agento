"""Conversation store for memory system."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    """Message role."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationMessage(BaseModel):
    """Conversation message."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Conversation(BaseModel):
    """Conversation entity."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Conversation"
    messages: list[ConversationMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: dict[str, Any] = Field(default_factory=dict)
    is_archived: bool = False
    message_count: int = 0

    def add_message(
        self,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        """Add a message to the conversation."""
        message = ConversationMessage(
            role=role,
            content=content,
            metadata=metadata or {},
        )
        self.messages.append(message)
        self.updated_at = datetime.now()
        self.message_count = len(self.messages)
        return message

    def get_messages_by_role(
        self,
        role: MessageRole,
    ) -> list[ConversationMessage]:
        """Get messages by role."""
        return [m for m in self.messages if m.role == role]

    def get_last_n_messages(
        self,
        n: int,
    ) -> list[ConversationMessage]:
        """Get last N messages."""
        return self.messages[-n:] if self.messages else []


@dataclass
class ConversationStats:
    """Conversation statistics."""

    total_conversations: int = 0
    total_messages: int = 0
    total_users: int = 0
    total_assistants: int = 0
    average_messages_per_conversation: float = 0.0


class ConversationStore:
    """Store conversations with persistence."""

    def __init__(
        self,
        max_conversations: int = 100,
        max_messages_per_conversation: int = 1000,
    ):
        self.max_conversations = max_conversations
        self.max_messages_per_conversation = max_messages_per_conversation
        self._conversations: dict[str, Conversation] = {}
        self._conversation_order: list[str] = []

    def create_conversation(
        self,
        title: str = "New Conversation",
        metadata: dict[str, Any] | None = None,
    ) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(
            title=title,
            metadata=metadata or {},
        )
        self._conversations[conversation.id] = conversation
        self._conversation_order.append(conversation.id)
        self._enforce_max_conversations()
        return conversation

    def get_conversation(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        """Get a conversation by ID."""
        return self._conversations.get(conversation_id)

    def delete_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """Delete a conversation."""
        if conversation_id not in self._conversations:
            return False

        del self._conversations[conversation_id]
        if conversation_id in self._conversation_order:
            self._conversation_order.remove(conversation_id)
        return True

    def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage | None:
        """Add a message to a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return None

        if len(conversation.messages) >= self.max_messages_per_conversation:
            return None

        message = conversation.add_message(role, content, metadata)
        self._move_to_end(conversation_id)
        return message

    def get_messages(
        self,
        conversation_id: str,
        limit: int | None = None,
    ) -> list[ConversationMessage]:
        """Get messages from a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return []

        messages = conversation.messages
        if limit:
            messages = messages[-limit:]
        return messages

    def search_conversations(
        self,
        query: str,
    ) -> list[Conversation]:
        """Search conversations by content."""
        query_lower = query.lower()
        results = []

        for conversation in self._conversations.values():
            if query_lower in conversation.title.lower():
                results.append(conversation)
                continue

            for message in conversation.messages:
                if query_lower in message.content.lower():
                    results.append(conversation)
                    break

        return results

    def archive_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """Archive a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False

        conversation.is_archived = True
        return True

    def unarchive_conversation(
        self,
        conversation_id: str,
    ) -> bool:
        """Unarchive a conversation."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return False

        conversation.is_archived = False
        return True

    def get_active_conversations(
        self,
        limit: int | None = None,
    ) -> list[Conversation]:
        """Get active (non-archived) conversations."""
        active = [c for c in self._conversations.values() if not c.is_archived]
        active.sort(key=lambda x: x.updated_at, reverse=True)

        if limit:
            active = active[:limit]
        return active

    def get_archived_conversations(
        self,
        limit: int | None = None,
    ) -> list[Conversation]:
        """Get archived conversations."""
        archived = [c for c in self._conversations.values() if c.is_archived]
        archived.sort(key=lambda x: x.updated_at, reverse=True)

        if limit:
            archived = archived[:limit]
        return archived

    def clear_all(self) -> None:
        """Clear all conversations."""
        self._conversations.clear()
        self._conversation_order.clear()

    def get_stats(self) -> ConversationStats:
        """Get conversation statistics."""
        total_messages = sum(c.message_count for c in self._conversations.values())
        user_messages = sum(
            len(c.get_messages_by_role(MessageRole.USER))
            for c in self._conversations.values()
        )
        assistant_messages = sum(
            len(c.get_messages_by_role(MessageRole.ASSISTANT))
            for c in self._conversations.values()
        )

        avg_messages = (
            total_messages / len(self._conversations) if self._conversations else 0.0
        )

        return ConversationStats(
            total_conversations=len(self._conversations),
            total_messages=total_messages,
            total_users=user_messages,
            total_assistants=assistant_messages,
            average_messages_per_conversation=avg_messages,
        )

    def _move_to_end(self, conversation_id: str) -> None:
        """Move conversation to end of order."""
        if conversation_id in self._conversation_order:
            self._conversation_order.remove(conversation_id)
        self._conversation_order.append(conversation_id)

    def _enforce_max_conversations(self) -> None:
        """Enforce maximum conversations limit."""
        while len(self._conversations) > self.max_conversations:
            if self._conversation_order:
                oldest_id = self._conversation_order[0]
                self.delete_conversation(oldest_id)

    def export_conversation(
        self,
        conversation_id: str,
    ) -> dict[str, Any] | None:
        """Export conversation as dict."""
        conversation = self._conversations.get(conversation_id)
        if not conversation:
            return None

        return conversation.model_dump(mode="json")

    def import_conversation(
        self,
        data: dict[str, Any],
    ) -> Conversation | None:
        """Import conversation from dict."""
        try:
            conversation = Conversation.model_validate(data)
            self._conversations[conversation.id] = conversation
            if conversation.id not in self._conversation_order:
                self._conversation_order.append(conversation.id)
            return conversation
        except Exception:
            return None

    def get_all_conversations(self) -> list[Conversation]:
        """Get all conversations ordered by update time."""
        return [
            self._conversations[cid]
            for cid in reversed(self._conversation_order)
            if cid in self._conversations
        ]
