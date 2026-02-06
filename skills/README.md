# Chimera Agent Skills

## Overview

Skills are the runtime capabilities that Chimera agents use to accomplish tasks autonomously. Each skill represents a specific competency with well-defined input/output contracts.

**Philosophy:** Skills are business logic. MCP Tools are technical integrations.

---

## Skill Architecture

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Any, Dict

class SkillInput(BaseModel):
    """Base class for skill inputs"""
    pass

class SkillOutput(BaseModel):
    """Base class for skill outputs"""
    success: bool
    error_message: str | None = None

class Skill(ABC):
    """Base class for all skills"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable skill description"""
        pass

    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:
        """Execute the skill with given input"""
        pass

    @abstractmethod
    def get_input_schema(self) -> type[SkillInput]:
        """Return the Pydantic model for input validation"""
        pass

    @abstractmethod
    def get_output_schema(self) -> type[SkillOutput]:
        """Return the Pydantic model for output validation"""
        pass
```

---

## Available Skills (MVP)

### 1. skill_analyze_trends

**Purpose:** Detect and analyze emerging trends from multiple data sources  
**Input:** Topic category, timeframe, relevance threshold  
**Output:** List of trending topics with insights and recommended actions  
**Estimated Execution Time:** 30-60 seconds  
**Cost per Execution:** ~$0.05 (LLM inference for analysis)

[View Documentation →](./skill_analyze_trends/README.md)

---

### 2. skill_generate_social_post

**Purpose:** Generate platform-optimized social media posts with persona consistency  
**Input:** Topic, platform, tone, agent persona  
**Output:** Text content, hashtags, engagement score estimate  
**Estimated Execution Time:** 10-20 seconds  
**Cost per Execution:** ~$0.02 (LLM inference)

[View Documentation →](./skill_generate_social_post/README.md)

---

### 3. skill_generate_character_image

**Purpose:** Generate images featuring agent's character with visual consistency  
**Input:** Prompt, character reference ID, style preferences  
**Output:** Image URL, metadata, cost  
**Estimated Execution Time:** 20-40 seconds  
**Cost per Execution:** ~$0.10 (image generation API)

[View Documentation →](./skill_generate_character_image/README.md)

---

## Skill Development Guidelines

### 1. Input Validation

Always use Pydantic for input validation:

```python
from pydantic import BaseModel, Field, validator

class MySkillInput(SkillInput):
    topic: str = Field(..., min_length=1, max_length=200)
    timeframe_hours: int = Field(default=24, ge=1, le=168)

    @validator('topic')
    def topic_must_be_meaningful(cls, v):
        if len(v.split()) < 2:
            raise ValueError('Topic must be at least 2 words')
        return v
```

---

### 2. Error Handling

Skills must handle all failure modes:

```python
async def execute(self, input_data: MySkillInput) -> MySkillOutput:
    try:
        result = await self._do_work(input_data)
        return MySkillOutput(success=True, data=result)
    except RateLimitError as e:
        logger.warning(f"Rate limited: {e}")
        return MySkillOutput(
            success=False,
            error_message=f"Rate limit exceeded: {e.retry_after}s"
        )
    except Exception as e:
        logger.error(f"Skill execution failed: {e}", exc_info=True)
        return MySkillOutput(
            success=False,
            error_message=f"Unexpected error: {str(e)}"
        )
```

---

### 3. Observability

Log all skill executions:

```python
async def execute(self, input_data: MySkillInput) -> MySkillOutput:
    start_time = time.time()
    trace_id = get_current_trace_id()

    logger.info(
        f"[{trace_id}] Starting skill execution",
        extra={
            "skill_name": self.name,
            "input_summary": input_data.dict()
        }
    )

    result = await self._do_work(input_data)

    duration = time.time() - start_time
    logger.info(
        f"[{trace_id}] Skill execution completed",
        extra={
            "skill_name": self.name,
            "duration_seconds": duration,
            "success": result.success
        }
    )

    return result
```

---

### 4. Testing Requirements

Each skill must have:

**Unit Tests:**

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_skill_executes_successfully():
    skill = MySkill()
    input_data = MySkillInput(topic="AI trends", timeframe_hours=24)

    # Mock MCP tool responses
    skill.mcp_client.call_tool = AsyncMock(return_value=mock_data)

    result = await skill.execute(input_data)

    assert result.success is True
    assert result.data is not None
```

**Integration Tests:**

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_skill_with_real_mcp():
    """Test with actual MCP servers (slower, more realistic)"""
    skill = MySkill()
    input_data = MySkillInput(topic="Python programming")

    result = await skill.execute(input_data)

    assert result.success is True
    # Validate output structure
    assert isinstance(result.data, list)
```

**Performance Benchmarks:**

```python
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_skill_performance():
    skill = MySkill()
    input_data = MySkillInput(topic="Test topic")

    start = time.time()
    result = await skill.execute(input_data)
    duration = time.time() - start

    # Skill should complete in under 60 seconds
    assert duration < 60.0
```

---

## Skill Registration

Skills are auto-discovered at startup:

```python
# skills/__init__.py
from .skill_analyze_trends import AnalyzeTrendsSkill
from .skill_generate_social_post import GenerateSocialPostSkill
from .skill_generate_character_image import GenerateCharacterImageSkill

_SKILLS_REGISTRY = [
    AnalyzeTrendsSkill(),
    GenerateSocialPostSkill(),
    GenerateCharacterImageSkill(),
]

def get_all_skills() -> list[Skill]:
    """Return all registered skills"""
    return _SKILLS_REGISTRY

def get_skill_by_name(name: str) -> Skill | None:
    """Get skill by name"""
    for skill in _SKILLS_REGISTRY:
        if skill.name == name:
            return skill
    return None
```

---

## Skill Execution in Worker

Workers execute skills based on task type:

```python
# services/worker/worker_service.py
from skills import get_skill_by_name

class WorkerService:
    async def execute_task(self, task: Task) -> Result:
        # Map task type to skill name
        skill_name = task.type  # e.g., "analyze_trends"

        # Get skill
        skill = get_skill_by_name(skill_name)
        if not skill:
            raise UnknownSkillError(f"No skill registered for {skill_name}")

        # Validate input against skill's schema
        InputSchema = skill.get_input_schema()
        try:
            validated_input = InputSchema(**task.input_data)
        except ValidationError as e:
            return Result(
                task_id=task.task_id,
                status="failure",
                error_details={"validation_error": str(e)}
            )

        # Execute skill
        output = await skill.execute(validated_input)

        # Create result
        return Result(
            task_id=task.task_id,
            worker_id=self.worker_id,
            status="success" if output.success else "failure",
            output_data=output.dict(),
            metadata={
                "skill_name": skill.name,
                "execution_time_ms": ...
            }
        )
```

---

## Skill Composition

Skills can call other skills:

```python
class ComplexSkill(Skill):
    async def execute(self, input_data: ComplexSkillInput) -> ComplexSkillOutput:
        # Step 1: Analyze trends
        analyze_skill = get_skill_by_name("analyze_trends")
        trends = await analyze_skill.execute(AnalyzeTrendsInput(...))

        # Step 2: Generate post based on top trend
        if trends.success and trends.data:
            top_trend = trends.data[0]
            post_skill = get_skill_by_name("generate_social_post")
            post = await post_skill.execute(GenerateSocialPostInput(
                topic=top_trend.topic
            ))

            return ComplexSkillOutput(success=True, post=post)

        return ComplexSkillOutput(success=False)
```

---

## Future Skills (Post-MVP)

### Planned Skills

- `skill_reply_to_comment`: Generate contextual replies to audience comments
- `skill_schedule_campaign`: Plan multi-day content campaigns
- `skill_analyze_engagement`: Analyze post performance and suggest improvements
- `skill_identify_sponsorship`: Detect potential sponsorship opportunities
- `skill_manage_budget`: Optimize resource allocation across tasks
- `skill_cross_platform_post`: Adapt content for multiple platforms simultaneously

---

## Skill Versioning

Skills follow semantic versioning:

```python
class MySkill(Skill):
    VERSION = "1.2.0"  # MAJOR.MINOR.PATCH

    # MAJOR: Breaking changes to input/output schema
    # MINOR: New features, backward compatible
    # PATCH: Bug fixes
```

---

## Best Practices

### ✅ DO:

- Define clear input/output contracts
- Handle all error cases gracefully
- Log execution details for observability
- Write comprehensive tests
- Document example usage
- Keep skills focused (single responsibility)

### ❌ DON'T:

- Make skills depend on specific MCP server implementations
- Store state in skill instances (skills should be stateless)
- Perform long-running operations without timeouts
- Throw unhandled exceptions
- Mix business logic with I/O operations

---

## Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Python Async Best Practices](https://docs.python.org/3/library/asyncio.html)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Project Chimera Technical Spec](../specs/technical.md)

---

_"A skill is a promise. Its contract is the guarantee. Its tests are the proof."_
