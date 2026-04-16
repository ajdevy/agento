"""Summarization for conversation history."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from agento.infrastructure.memory.conversation_store import (
    ConversationMessage,
    MessageRole,
)


class SummaryStrategy(StrEnum):
    """Summarization strategy."""

    FIRST_LAST = "first_last"
    TRUNCATE = "truncate"
    EXTRACT_KEY_POINTS = "extract_key_points"
    CONDENSE = "condense"


@dataclass
class Summary:
    """Conversation summary."""

    content: str
    strategy: SummaryStrategy
    original_length: int
    summarized_length: int
    key_topics: list[str]


@dataclass
class SummarizerConfig:
    """Summarizer configuration."""

    max_summary_length: int = 500
    min_messages_for_summary: int = 10
    preserve_system_messages: bool = True
    strategy: SummaryStrategy = SummaryStrategy.TRUNCATE


class ConversationSummarizer:
    """Summarize conversation history."""

    def __init__(
        self,
        config: SummarizerConfig | None = None,
    ):
        self.config = config or SummarizerConfig()

    def summarize(
        self,
        messages: list[ConversationMessage],
    ) -> Summary:
        """Summarize conversation messages."""
        if len(messages) < self.config.min_messages_for_summary:
            full_content = self._combine_messages(messages)
            return Summary(
                content=full_content,
                strategy=SummaryStrategy.TRUNCATE,
                original_length=len(full_content),
                summarized_length=len(full_content),
                key_topics=self._extract_topics(full_content),
            )

        if self.config.strategy == SummaryStrategy.FIRST_LAST:
            return self._summarize_first_last(messages)
        elif self.config.strategy == SummaryStrategy.TRUNCATE:
            return self._summarize_truncate(messages)
        elif self.config.strategy == SummaryStrategy.EXTRACT_KEY_POINTS:
            return self._extract_key_points(messages)
        else:
            return self._summarize_truncate(messages)

    def _combine_messages(
        self,
        messages: list[ConversationMessage],
    ) -> str:
        """Combine messages into a single string."""
        parts = []
        for msg in messages:
            role_label = msg.role.value.capitalize()
            parts.append(f"{role_label}: {msg.content}")
        return "\n".join(parts)

    def _summarize_first_last(
        self,
        messages: list[ConversationMessage],
    ) -> Summary:
        """Summarize using first and last messages."""
        first_msgs = (
            messages[:3] if len(messages) > 6 else messages[: len(messages) // 2]
        )
        last_msgs = (
            messages[-3:] if len(messages) > 6 else messages[len(messages) // 2 :]
        )

        first_content = self._combine_messages(first_msgs)
        last_content = self._combine_messages(last_msgs)

        total_content = f"[First {len(first_msgs)} messages]\n{first_content}\n\n[Last {len(last_msgs)} messages]\n{last_content}"

        return Summary(
            content=total_content,
            strategy=SummaryStrategy.FIRST_LAST,
            original_length=len(self._combine_messages(messages)),
            summarized_length=len(total_content),
            key_topics=self._extract_topics(total_content),
        )

    def _summarize_truncate(
        self,
        messages: list[ConversationMessage],
    ) -> Summary:
        """Summarize by truncating to last N messages."""
        user_and_assistant = [
            m for m in messages if m.role in (MessageRole.USER, MessageRole.ASSISTANT)
        ]

        if len(user_and_assistant) <= self.config.min_messages_for_summary:
            full_content = self._combine_messages(messages)
            return Summary(
                content=full_content,
                strategy=SummaryStrategy.TRUNCATE,
                original_length=len(full_content),
                summarized_length=len(full_content),
                key_topics=self._extract_topics(full_content),
            )

        recent = user_and_assistant[-self.config.min_messages_for_summary :]

        parts = []
        if self.config.preserve_system_messages:
            system_msgs = [m for m in messages if m.role == MessageRole.SYSTEM]
            if system_msgs:
                parts.append(self._combine_messages(system_msgs[-2:]))

        parts.append(self._combine_messages(recent))

        summarized = "\n\n".join(parts)

        if len(summarized) > self.config.max_summary_length:
            summarized = summarized[: self.config.max_summary_length] + "..."

        return Summary(
            content=summarized,
            strategy=SummaryStrategy.TRUNCATE,
            original_length=len(self._combine_messages(messages)),
            summarized_length=len(summarized),
            key_topics=self._extract_topics(summarized),
        )

    def _extract_key_points(
        self,
        messages: list[ConversationMessage],
    ) -> Summary:
        """Extract key points from conversation."""
        content = self._combine_messages(messages)
        key_topics = self._extract_topics(content)

        key_points = []
        for topic in key_topics[:5]:
            key_points.append(f"- Discussed: {topic}")

        summarized = (
            "Key Topics:\n"
            + "\n".join(key_points)
            + f"\n\nRecent context:\n{content[-500:]}"
        )

        return Summary(
            content=summarized,
            strategy=SummaryStrategy.EXTRACT_KEY_POINTS,
            original_length=len(content),
            summarized_length=len(summarized),
            key_topics=key_topics,
        )

    def _extract_topics(self, content: str) -> list[str]:
        """Extract key topics from content."""
        keywords = self._get_topic_keywords()
        content_lower = content.lower()

        topics = []
        for keyword in keywords:
            if keyword in content_lower:
                topics.append(keyword)

        return topics[:5]

    def _get_topic_keywords(self) -> list[str]:
        """Get common topic keywords."""
        return [
            "python",
            "javascript",
            "code",
            "api",
            "database",
            "error",
            "bug",
            "fix",
            "test",
            "deploy",
            "docker",
            "git",
            "configuration",
            "setup",
            "install",
            "import",
            "function",
            "class",
            "module",
            "file",
            "project",
        ]

    def get_context_window(
        self,
        messages: list[ConversationMessage],
        window_size: int = 10,
    ) -> list[ConversationMessage]:
        """Get context window (last N messages)."""
        return messages[-window_size:] if messages else []

    def compress_messages(
        self,
        messages: list[ConversationMessage],
    ) -> list[ConversationMessage]:
        """Compress messages by merging similar consecutive ones."""
        if not messages:
            return []

        compressed: list[ConversationMessage] = []
        current_role = None
        current_content: list[str] = []

        for msg in messages:
            if msg.role == current_role and len(current_content) < 3:
                current_content.append(msg.content)
            else:
                if current_role is not None and current_content:
                    compressed.append(
                        ConversationMessage(
                            role=current_role,
                            content=" ".join(current_content),
                        )
                    )

                current_role = msg.role
                current_content = [msg.content]

        if current_role is not None and current_content:
            compressed.append(
                ConversationMessage(
                    role=current_role,
                    content=" ".join(current_content),
                )
            )

        return compressed

    def estimate_summary_quality(
        self,
        original: list[ConversationMessage],
        summary: Summary,
    ) -> float:
        """Estimate summary quality (0-1)."""
        if not original:
            return 0.0

        compression_ratio = summary.summarized_length / summary.original_length
        if summary.original_length == 0:
            compression_ratio = 1.0

        topic_coverage = len(summary.key_topics) / 5.0

        message_coverage = len(summary.content.split("\n")) / len(original)

        quality = (
            (1 - compression_ratio) * 0.4
            + topic_coverage * 0.3
            + min(message_coverage, 1.0) * 0.3
        )

        return max(0.0, min(1.0, quality))
