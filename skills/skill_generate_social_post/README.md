# Skill: Generate Social Post

## Overview

**Skill Name:** `skill_generate_social_post`  
**Purpose:** Generate platform-optimized social media posts with persona consistency  
**Version:** 1.0.0  
**Status:** Specification Complete | Implementation Pending

---

## Description

This skill generates engaging social media content tailored to specific platforms (Twitter, Instagram, TikTok) while maintaining the agent's unique persona and voice. It optimizes for platform constraints (character limits, hashtag conventions) and predicts engagement potential.

---

## Input/Output Contract

### Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal

class GenerateSocialPostInput(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    platform: Literal["twitter", "instagram", "tiktok"] = Field(...)
    tone: str | None = Field(default=None, description="Optional tone override")
    agent_persona: dict = Field(..., description="Agent's SOUL.md parsed data")
    context: dict | None = Field(default=None, description="Additional context (trends, related posts)")
    include_hashtags: bool = Field(default=True)
    max_length: int | None = Field(default=None, description="Override platform default")
```

---

### Output Schema

```python
class GenerateSocialPostOutput(BaseModel):
    success: bool
    error_message: str | None = None

    text_content: str = Field(default="", description="Main post text")
    hashtags: List[str] = Field(default=[], description="Recommended hashtags")

    estimated_engagement_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Predicted engagement (0-1)"
    )

    persona_consistency_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="How well it matches persona"
    )

    safety_check: dict = Field(
        default={},
        description="Content moderation results"
    )

    metadata: dict = Field(default={})
```

---

## Execution Flow

1. **Load Persona Context** → Extract voice_tone, core_values from SOUL.md
2. **Platform Constraints** → Apply character limits (Twitter: 280, Instagram: 2200)
3. **Generate Content** → LLM call with persona-aware prompt
4. **Generate Hashtags** → Extract/suggest relevant hashtags
5. **Safety Check** → Content moderation API (OpenAI Moderation)
6. **Estimate Engagement** → Simple heuristic or ML model
7. **Return Output**

---

## MCP Tools Used

- **LLM API** (Gemini 3 Pro or Claude Opus) for content generation
- **OpenAI Moderation API** for safety checks
- **mcp-server-weaviate** for retrieving similar successful posts

---

## Cost: ~$0.02 per execution

## Execution Time: 10-20 seconds

---

_"Content is king. Consistency is the kingdom."_
