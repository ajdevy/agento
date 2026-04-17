"""Reflection service - self-assessment and improvement."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ReflectionLevel(Enum):
    """Reflection depth levels."""

    NONE = "none"
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


class QualityScore(Enum):
    """Quality assessment scores."""

    EXCELLENT = 5
    GOOD = 4
    ADEQUATE = 3
    NEEDS_IMPROVEMENT = 2
    POOR = 1


@dataclass
class ReflectionResult:
    """Result of reflection."""

    assessment: str
    quality_score: QualityScore
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionFeedback:
    """Feedback on task execution."""

    task_id: str
    success: bool
    output: str
    expected: str | None = None
    errors: list[str] = field(default_factory=list)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class ReflectionService:
    """Service for self-reflection and quality assessment."""

    def __init__(
        self,
        llm_client: Any | None = None,
        reflection_level: ReflectionLevel = ReflectionLevel.BASIC,
    ):
        self.llm_client = llm_client
        self.reflection_level = reflection_level
        self._reflection_history: list[ReflectionResult] = []

    async def reflect(
        self,
        content: str,
        context: dict[str, Any] | None = None,
        criteria: list[str] | None = None,
    ) -> ReflectionResult:
        """Reflect on content and provide assessment."""
        try:
            if self.llm_client and self.reflection_level != ReflectionLevel.NONE:
                return await self._llm_reflection(content, context, criteria)
            return self._rule_based_reflection(content, context, criteria)

        except Exception as e:
            return ReflectionResult(
                assessment=f"Reflection failed: {e!s}",
                quality_score=QualityScore.POOR,
                issues=[str(e)],
            )

    async def _llm_reflection(
        self,
        content: str,
        context: dict[str, Any] | None,
        criteria: list[str] | None,
    ) -> ReflectionResult:
        """Use LLM for reflection."""
        context = context or {}
        criteria = criteria or ["correctness", "completeness", "clarity"]

        assert self.llm_client is not None

        prompt = f"""Reflect on this output and assess its quality:

Content: {content}

Context: {context}

Assessment Criteria: {", ".join(criteria)}

Provide:
1. Quality score (1-5)
2. Issues found
3. Suggestions for improvement
"""

        response = await self.llm_client.chat(
            messages=[{"role": "user", "content": prompt}]
        )

        result = self._parse_llm_response(str(response.content), content)
        self._reflection_history.append(result)

        return result

    def _rule_based_reflection(
        self,
        content: str,
        context: dict[str, Any] | None,
        criteria: list[str] | None,
    ) -> ReflectionResult:
        """Rule-based reflection when LLM is not available."""
        context = context or {}
        criteria = criteria or ["correctness", "completeness", "clarity"]

        issues: list[str] = []
        suggestions: list[str] = []
        improvements: list[str] = []

        content_lower = content.lower()
        content_length = len(content)

        if content_length < 50 and "error" not in content_lower:
            issues.append("Content may be too brief")
            suggestions.append("Provide more detailed explanation")

        if "error" in content_lower or "failed" in content_lower:
            issues.append("Content indicates an error or failure")
            suggestions.append("Handle the error case more gracefully")

        if "TODO" in content or "FIXME" in content:
            issues.append("Contains incomplete code markers")
            suggestions.append("Replace TODOs with actual implementation")

        if not content.strip():
            issues.append("Content is empty")
            suggestions.append("Provide meaningful content")

        if "except" in content_lower and "pass" in content_lower:
            suggestions.append("Handle exceptions with meaningful logic")

        score = self._calculate_quality_score(content, issues)
        confidence = self._calculate_confidence(content, issues)

        result = ReflectionResult(
            assessment=self._generate_assessment(content, issues),
            quality_score=score,
            issues=issues,
            suggestions=suggestions,
            improvements=improvements,
            confidence=confidence,
            metadata={
                "content_length": content_length,
                "criteria": criteria,
            },
        )

        self._reflection_history.append(result)
        return result

    def _parse_llm_response(
        self,
        response: str,
        original_content: str,
    ) -> ReflectionResult:
        """Parse LLM reflection response."""
        lines = response.strip().split("\n")

        score = QualityScore.ADEQUATE
        issues: list[str] = []
        suggestions: list[str] = []

        for line in lines:
            line_lower = line.lower()
            if "score" in line_lower or "rating" in line_lower:
                if "5" in line or "excellent" in line_lower:
                    score = QualityScore.EXCELLENT
                elif "4" in line or "good" in line_lower:
                    score = QualityScore.GOOD
                elif "3" in line or "adequate" in line_lower:
                    score = QualityScore.ADEQUATE
                elif "2" in line or "improve" in line_lower:
                    score = QualityScore.NEEDS_IMPROVEMENT
                elif "1" in line or "poor" in line_lower:
                    score = QualityScore.POOR

            if "issue" in line_lower or "problem" in line_lower:
                issues.append(line.strip())

            if "suggest" in line_lower or "improve" in line_lower:
                suggestions.append(line.strip())

        return ReflectionResult(
            assessment=response[:200] if response else "Assessment complete",
            quality_score=score,
            issues=issues,
            suggestions=suggestions,
            confidence=0.8 if self.llm_client else 0.5,
        )

    def _calculate_quality_score(
        self,
        content: str,
        issues: list[str],
    ) -> QualityScore:
        """Calculate quality score based on rules."""
        score: float = 5.0

        if len(content) < 50:
            score -= 1
        if len(content) > 5000:
            score -= 1
        if not content.strip():
            score -= 2
        if "error" in content.lower():
            score -= 1
        if issues:
            score -= len(issues) * 0.5

        if score >= 5:
            return QualityScore.EXCELLENT
        elif score >= 4:
            return QualityScore.GOOD
        elif score >= 3:
            return QualityScore.ADEQUATE
        elif score >= 2:
            return QualityScore.NEEDS_IMPROVEMENT
        else:
            return QualityScore.POOR

    def _calculate_confidence(
        self,
        content: str,
        issues: list[str],
    ) -> float:
        """Calculate confidence in the assessment."""
        confidence = 0.7

        if self.llm_client:
            confidence += 0.2

        if len(content) > 100:
            confidence += 0.1

        if len(issues) == 0:
            confidence += 0.1

        return min(1.0, max(0.0, confidence))

    def _generate_assessment(
        self,
        content: str,
        issues: list[str],
    ) -> str:
        """Generate a text assessment."""
        if not content.strip():
            return "Content is empty - no assessment possible"

        if not issues:
            return "Content appears well-formed with no obvious issues"

        if len(issues) == 1:
            return f"One issue found: {issues[0]}"

        return f"Found {len(issues)} issues in content"

    async def reflect_on_execution(
        self,
        feedback: ExecutionFeedback,
    ) -> ReflectionResult:
        """Reflect on task execution feedback."""
        content = feedback.output

        context = {
            "task_id": feedback.task_id,
            "success": feedback.success,
            "execution_time": feedback.execution_time,
            "errors": feedback.errors,
        }

        return await self.reflect(content, context)

    async def suggest_improvements(
        self,
        content: str,
        past_reflections: list[ReflectionResult] | None = None,
    ) -> list[str]:
        """Suggest improvements based on reflection history."""
        past_reflections = past_reflections or []

        suggestions: list[str] = []

        issue_counts: dict[str, int] = {}
        for reflection in past_reflections:
            for issue in reflection.issues:
                normalized = issue.lower().strip()
                issue_counts[normalized] = issue_counts.get(normalized, 0) + 1

        for issue, count in issue_counts.items():
            if count >= 2:
                suggestions.append(f"Address recurring issue: {issue}")

        current_reflection = await self.reflect(content)
        suggestions.extend(current_reflection.suggestions)

        return suggestions[:5]

    def get_reflection_history(self) -> list[ReflectionResult]:
        """Get reflection history."""
        return self._reflection_history.copy()

    def clear_history(self) -> None:
        """Clear reflection history."""
        self._reflection_history.clear()

    def get_average_quality(self) -> float:
        """Get average quality score from history."""
        if not self._reflection_history:
            return 0.0

        total = sum(r.quality_score.value for r in self._reflection_history)
        return total / len(self._reflection_history)
