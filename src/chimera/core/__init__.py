"""Core chimera package (src/chimera/core)."""

from .agent import Agent  # type: ignore
from .persona import parse_soul_md  # type: ignore
from .models import AgentProfile, Task, Result  # type: ignore

__all__ = ["Agent", "parse_soul_md", "AgentProfile", "Task", "Result"]
