from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional


class AgentProfile(BaseModel):
    agent_id: str
    name: str
    bio: Optional[str] = Field(default="", max_length=500)
    persona: Dict[str, Any] = Field(default_factory=dict)
    social_handles: Dict[str, str] = Field(default_factory=dict)
    wallet_address: Optional[str] = None
    character_reference_id: Optional[str] = None
    status: str = Field(default="active")

    @validator("status")
    def status_must_be_enum(cls, v):
        if v not in ["active", "paused", "archived"]:
            raise ValueError("invalid status")
        return v


class Task(BaseModel):
    task_id: str
    agent_id: str
    type: str
    priority: int = Field(default=5, ge=1, le=10)
    status: str = Field(default="pending")
    input_data: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)
    trace_id: Optional[str] = None


class Result(BaseModel):
    result_id: str
    task_id: str
    worker_id: str
    status: str
    output_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
