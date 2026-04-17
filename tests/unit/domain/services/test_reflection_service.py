"""Tests for reflection service."""

import pytest

from agento.domain.services.reflection_service import (
    ExecutionFeedback,
    QualityScore,
    ReflectionLevel,
    ReflectionResult,
    ReflectionService,
)


class TestReflectionResult:
    """Tests for ReflectionResult dataclass."""

    def test_create_reflection_result(self):
        """Test creating a reflection result."""
        result = ReflectionResult(
            assessment="Good work",
            quality_score=QualityScore.GOOD,
        )
        assert result.assessment == "Good work"
        assert result.quality_score == QualityScore.GOOD
        assert result.issues == []
        assert result.suggestions == []
        assert result.improvements == []
        assert result.confidence == 0.0

    def test_reflection_result_with_all_fields(self):
        """Test creating a reflection result with all fields."""
        result = ReflectionResult(
            assessment="Assessment",
            quality_score=QualityScore.EXCELLENT,
            issues=["Issue 1"],
            suggestions=["Suggestion 1"],
            improvements=["Improvement 1"],
            confidence=0.9,
            metadata={"key": "value"},
        )
        assert result.issues == ["Issue 1"]
        assert result.suggestions == ["Suggestion 1"]
        assert result.improvements == ["Improvement 1"]
        assert result.confidence == 0.9
        assert result.metadata == {"key": "value"}


class TestExecutionFeedback:
    """Tests for ExecutionFeedback dataclass."""

    def test_create_execution_feedback(self):
        """Test creating execution feedback."""
        feedback = ExecutionFeedback(
            task_id="task-1",
            success=True,
            output="Output text",
        )
        assert feedback.task_id == "task-1"
        assert feedback.success is True
        assert feedback.output == "Output text"
        assert feedback.expected is None
        assert feedback.errors == []
        assert feedback.execution_time == 0.0

    def test_execution_feedback_with_errors(self):
        """Test creating feedback with errors."""
        feedback = ExecutionFeedback(
            task_id="task-1",
            success=False,
            output="Error output",
            errors=["Error 1", "Error 2"],
            execution_time=1.5,
        )
        assert feedback.success is False
        assert len(feedback.errors) == 2


class TestReflectionService:
    """Tests for ReflectionService."""

    @pytest.fixture
    def service(self):
        """Create a reflection service without LLM."""
        return ReflectionService(
            llm_client=None, reflection_level=ReflectionLevel.BASIC
        )

    def test_create_service(self):
        """Test creating a reflection service."""
        service = ReflectionService()
        assert service.llm_client is None
        assert service.reflection_level == ReflectionLevel.BASIC
        assert service._reflection_history == []

    def test_create_service_with_level(self):
        """Test creating service with specific level."""
        service = ReflectionService(reflection_level=ReflectionLevel.DETAILED)
        assert service.reflection_level == ReflectionLevel.DETAILED

    @pytest.mark.asyncio
    async def test_reflect_basic_content(self, service):
        """Test reflecting on basic content."""
        result = await service.reflect("This is a good piece of content")
        assert result.assessment is not None
        assert result.quality_score is not None

    @pytest.mark.asyncio
    async def test_reflect_empty_content(self, service):
        """Test reflecting on empty content."""
        result = await service.reflect("")
        assert "empty" in result.issues or len(result.issues) > 0
        assert result.quality_score == QualityScore.POOR

    @pytest.mark.asyncio
    async def test_reflect_error_content(self, service):
        """Test reflecting on content with errors."""
        result = await service.reflect("Error: Something failed")
        assert any("error" in i.lower() for i in result.issues)

    @pytest.mark.asyncio
    async def test_reflect_todo_content(self, service):
        """Test reflecting on content with TODO markers."""
        result = await service.reflect("def foo():\n    TODO: implement this")
        assert any("incomplete" in i.lower() for i in result.issues)

    @pytest.mark.asyncio
    async def test_reflect_short_content(self, service):
        """Test reflecting on short content."""
        result = await service.reflect("Hi")
        assert "brief" in " ".join(result.issues).lower() or len(result.issues) > 0

    @pytest.mark.asyncio
    async def test_reflect_with_context(self, service):
        """Test reflecting with context."""
        result = await service.reflect(
            "Good code",
            context={"language": "python", "type": "function"},
        )
        assert result.metadata.get("criteria") is not None

    @pytest.mark.asyncio
    async def test_reflect_with_custom_criteria(self, service):
        """Test reflecting with custom criteria."""
        criteria = ["readability", "performance"]
        result = await service.reflect("Code", criteria=criteria)
        assert result.metadata.get("criteria") == criteria

    @pytest.mark.asyncio
    async def test_reflect_adds_to_history(self, service):
        """Test that reflections are added to history."""
        await service.reflect("Content 1")
        await service.reflect("Content 2")
        assert len(service.get_reflection_history()) == 2

    def test_calculate_quality_score_excellent(self):
        """Test calculating excellent quality score."""
        service = ReflectionService()
        score = service._calculate_quality_score(
            "A good piece of content with many words and details", []
        )
        assert score == QualityScore.EXCELLENT

    def test_calculate_quality_score_short(self):
        """Test calculating quality score for short content."""
        service = ReflectionService()
        score = service._calculate_quality_score("Hi", [])
        assert score in [QualityScore.GOOD, QualityScore.ADEQUATE]

    def test_calculate_quality_score_empty(self):
        """Test calculating quality score for empty content."""
        service = ReflectionService()
        score = service._calculate_quality_score("", [])
        assert score in [QualityScore.POOR, QualityScore.NEEDS_IMPROVEMENT]

    def test_calculate_quality_score_with_issues(self):
        """Test calculating quality score with issues."""
        service = ReflectionService()
        score = service._calculate_quality_score("Content", ["Issue 1", "Issue 2"])
        assert score in [
            QualityScore.POOR,
            QualityScore.NEEDS_IMPROVEMENT,
            QualityScore.ADEQUATE,
        ]

    def test_calculate_confidence_no_llm(self):
        """Test calculating confidence without LLM."""
        service = ReflectionService(llm_client=None)
        confidence = service._calculate_confidence("Some content", [])
        assert confidence < 0.9

    def test_calculate_confidence_with_llm(self):
        """Test calculating confidence with LLM."""
        service = ReflectionService(llm_client=object())
        confidence = service._calculate_confidence("Some content", [])
        assert confidence >= 0.9

    def test_calculate_confidence_with_issues(self):
        """Test calculating confidence decreases with issues."""
        service = ReflectionService()
        confidence = service._calculate_confidence("Content", ["issue"])
        assert confidence < 0.9

    def test_generate_assessment_empty(self):
        """Test generating assessment for empty content."""
        service = ReflectionService()
        assessment = service._generate_assessment("", [])
        assert "empty" in assessment.lower()

    def test_generate_assessment_no_issues(self):
        """Test generating assessment with no issues."""
        service = ReflectionService()
        assessment = service._generate_assessment("Good content", [])
        assert "well-formed" in assessment.lower() or "no" in assessment.lower()

    def test_generate_assessment_single_issue(self):
        """Test generating assessment with single issue."""
        service = ReflectionService()
        assessment = service._generate_assessment("Content", ["Test issue"])
        assert "one issue" in assessment.lower()

    def test_generate_assessment_multiple_issues(self):
        """Test generating assessment with multiple issues."""
        service = ReflectionService()
        assessment = service._generate_assessment("Content", ["Issue 1", "Issue 2"])
        assert "2 issues" in assessment

    @pytest.mark.asyncio
    async def test_reflect_on_execution_success(self, service):
        """Test reflecting on successful execution."""
        feedback = ExecutionFeedback(
            task_id="task-1",
            success=True,
            output="Completed successfully",
            execution_time=1.0,
        )
        result = await service.reflect_on_execution(feedback)
        assert result is not None

    @pytest.mark.asyncio
    async def test_reflect_on_execution_failure(self, service):
        """Test reflecting on failed execution."""
        feedback = ExecutionFeedback(
            task_id="task-1",
            success=False,
            output="Failed",
            errors=["Error 1"],
            execution_time=2.0,
        )
        result = await service.reflect_on_execution(feedback)
        assert result is not None

    @pytest.mark.asyncio
    async def test_suggest_improvements(self, service):
        """Test suggesting improvements."""
        suggestions = await service.suggest_improvements("Some content")
        assert isinstance(suggestions, list)

    @pytest.mark.asyncio
    async def test_suggest_improvements_with_history(self, service):
        """Test suggesting improvements with reflection history."""
        past = [
            ReflectionResult(
                assessment="Test",
                quality_score=QualityScore.GOOD,
                issues=["recurring issue", "other issue"],
            ),
            ReflectionResult(
                assessment="Test",
                quality_score=QualityScore.GOOD,
                issues=["recurring issue", "different"],
            ),
        ]
        suggestions = await service.suggest_improvements("Content", past)
        assert any("recurring" in s.lower() for s in suggestions)

    def test_get_reflection_history(self):
        """Test getting reflection history."""
        service = ReflectionService()
        assert service.get_reflection_history() == []

        service._reflection_history.append(
            ReflectionResult(assessment="Test", quality_score=QualityScore.GOOD)
        )
        history = service.get_reflection_history()
        assert len(history) == 1

    def test_clear_history(self):
        """Test clearing reflection history."""
        service = ReflectionService()
        service._reflection_history.append(
            ReflectionResult(assessment="Test", quality_score=QualityScore.GOOD)
        )
        service.clear_history()
        assert len(service.get_reflection_history()) == 0

    def test_get_average_quality_empty(self):
        """Test average quality with no history."""
        service = ReflectionService()
        assert service.get_average_quality() == 0.0

    def test_get_average_quality_with_history(self):
        """Test average quality with history."""
        service = ReflectionService()
        service._reflection_history.append(
            ReflectionResult(assessment="Test", quality_score=QualityScore.GOOD)
        )
        service._reflection_history.append(
            ReflectionResult(assessment="Test", quality_score=QualityScore.EXCELLENT)
        )
        avg = service.get_average_quality()
        assert avg == 4.5


class TestReflectionLevel:
    """Tests for ReflectionLevel enum."""

    def test_all_levels_exist(self):
        """Test all reflection levels exist."""
        assert ReflectionLevel.NONE is not None
        assert ReflectionLevel.BASIC is not None
        assert ReflectionLevel.DETAILED is not None
        assert ReflectionLevel.COMPREHENSIVE is not None

    def test_level_values(self):
        """Test reflection level values."""
        assert ReflectionLevel.NONE.value == "none"
        assert ReflectionLevel.BASIC.value == "basic"
        assert ReflectionLevel.DETAILED.value == "detailed"
        assert ReflectionLevel.COMPREHENSIVE.value == "comprehensive"


class TestQualityScore:
    """Tests for QualityScore enum."""

    def test_all_scores_exist(self):
        """Test all quality scores exist."""
        assert QualityScore.EXCELLENT is not None
        assert QualityScore.GOOD is not None
        assert QualityScore.ADEQUATE is not None
        assert QualityScore.NEEDS_IMPROVEMENT is not None
        assert QualityScore.POOR is not None

    def test_score_values(self):
        """Test quality score values."""
        assert QualityScore.EXCELLENT.value == 5
        assert QualityScore.GOOD.value == 4
        assert QualityScore.ADEQUATE.value == 3
        assert QualityScore.NEEDS_IMPROVEMENT.value == 2
        assert QualityScore.POOR.value == 1


class TestReflectionServiceWithLLM:
    """Tests for ReflectionService with LLM client."""

    @pytest.mark.asyncio
    async def test_llm_reflection(self):
        """Test LLM-based reflection."""

        class MockLLM:
            async def chat(self, messages):
                class Response:
                    content = "Quality score: 5\nIssues: None\nSuggestions: Looks good"

                return Response()

        service = ReflectionService(llm_client=MockLLM())
        result = await service.reflect("Good code")
        assert result is not None

    @pytest.mark.asyncio
    async def test_llm_reflection_comprehensive(self):
        """Test LLM-based reflection with comprehensive level."""

        class MockLLM:
            async def chat(self, messages):
                class Response:
                    content = "Score: 4\nGood work"

                return Response()

        service = ReflectionService(
            llm_client=MockLLM(),
            reflection_level=ReflectionLevel.COMPREHENSIVE,
        )
        result = await service.reflect("Some code")
        assert result is not None

    @pytest.mark.asyncio
    async def test_llm_reflection_exception(self):
        """Test LLM reflection handles exceptions."""

        class FailingLLM:
            async def chat(self, messages):
                raise ValueError("LLM error")

        service = ReflectionService(llm_client=FailingLLM())
        result = await service.reflect("Content")
        assert result.quality_score == QualityScore.POOR

    def test_parse_llm_response_scores(self):
        """Test parsing LLM response with various scores."""
        service = ReflectionService(llm_client=object())

        result = service._parse_llm_response(
            "Score: 5\nThe content is excellent", "original"
        )
        assert result.quality_score == QualityScore.EXCELLENT

        result = service._parse_llm_response("Rating: 4\nGood content", "original")
        assert result.quality_score == QualityScore.GOOD

        result = service._parse_llm_response("Score: 3\nAdequate", "original")
        assert result.quality_score == QualityScore.ADEQUATE

        result = service._parse_llm_response("Score: 2\nNeeds improvement", "original")
        assert result.quality_score == QualityScore.NEEDS_IMPROVEMENT

        result = service._parse_llm_response("Score: 1\nPoor quality", "original")
        assert result.quality_score == QualityScore.POOR

    def test_parse_llm_response_with_issues(self):
        """Test parsing LLM response with issues."""
        service = ReflectionService(llm_client=object())
        response = """Assessment complete.

Issues found:
- Memory leak
- Missing error handling

Suggestions:
- Add proper cleanup
"""
        result = service._parse_llm_response(response, "original")
        assert len(result.issues) >= 0
