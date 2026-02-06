from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
import uuid
from pathlib import Path

from .persona import parse_soul_md


@dataclass
class Agent:
    name: str
    soul_md_path: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    social_handles: Dict[str, str] = field(default_factory=dict)
    wallet_address: Optional[str] = None
    character_reference_id: Optional[str] = None
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    persona: Dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.soul_md_path:
            raise ValueError("soul_md_path is required")

        p = Path(self.soul_md_path)
        if not p.exists():
            raise FileNotFoundError(self.soul_md_path)

        self.persona = parse_soul_md(self.soul_md_path)
"""
Agent core model - US-001: Agent Persona Instantiation
To be implemented per specs/functional.md and specs/technical.md
"""
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel


class Persona(BaseModel):
    """Agent persona from SOUL.md"""
    voice_tone: list[str] = []
    core_values: list[str] = []
    directives: list[str] = []
    backstory: str = ""


class Agent(BaseModel):
    """
    Agent Profile Schema
    See: specs/technical.md - Agent Profile
    """
    agent_id: UUID = uuid4()
    name: str
    bio: Optional[str] = None
    persona: Optional[Persona] = None
    wallet_address: Optional[str] = None
    character_reference_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    status: str = "active"
    
    class Config:
        # Allow arbitrary types for UUID
        arbitrary_types_allowed = True


# TODO: Implement per US-001 acceptance criteria
# - Load SOUL.md file and parse
# - Create wallet via Coinbase AgentKit
# - Store in PostgreSQL