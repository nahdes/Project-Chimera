# Skill: Generate Character Image

## Overview

**Skill Name:** `skill_generate_character_image`  
**Purpose:** Generate images featuring agent's character with visual consistency  
**Version:** 1.0.0  
**Status:** Specification Complete | Implementation Pending

---

## Description

This skill generates character-consistent images by automatically applying the agent's character reference LoRA to all image generation requests. This ensures visual brand consistency across all agent-created media.

---

## Input/Output Contract

### Input Schema

```python
class GenerateCharacterImageInput(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=1000)
    character_reference_id: str = Field(..., description="LoRA identifier from agent profile")
    style: Literal["portrait", "landscape", "square", "story"] = Field(default="square")
    aspect_ratio: str = Field(default="1:1", description="e.g., '16:9', '4:3'")
    quality: Literal["standard", "high", "ultra"] = Field(default="standard")
```

### Output Schema

```python
class GenerateCharacterImageOutput(BaseModel):
    success: bool
    error_message: str | None = None

    image_url: str = Field(default="", description="Cloud storage URL")

    image_metadata: dict = Field(
        default={},
        description="Width, height, file_size, format"
    )

    generation_model: str = Field(default="", description="e.g., 'ideogram-v2'")
    cost_usd: float = Field(default=0.0, description="Generation cost")

    safety_passed: bool = Field(default=True, description="No NSFW/violence detected")
```

---

## Execution Flow

1. **Character Reference Lock** → Auto-inject character_reference_id into prompt
2. **Call Image Generation API** → mcp-server-ideogram or midjourney
3. **Safety Check** → NSFW/violence detection
4. **Upload to Storage** → S3/Cloud Storage
5. **Return URL**

---

## MCP Tools Used

- **mcp-server-ideogram** or **mcp-server-midjourney** for image generation
- **Safety API** for content filtering

---

## Cost: ~$0.10 per image (standard quality)

## Execution Time: 20-40 seconds

---

_"A face is worth a thousand words. Consistency is priceless."_
