
"""
Project Chimera: Autonomous Influencer Network

A production-grade system for managing AI-powered virtual influencers.
"""

__version__ = "0.1.0"
__author__ = "AiQEM.tech"

from chimera.core.agent import Agent, Persona
from chimera.core.task import Task
from chimera.core.result import Result

__all__ = [
    "Agent",
    "Persona", 
    "Task",
    "Result",
]