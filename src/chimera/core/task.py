"""
Task core model - US-012: Decompose Goal into Tasks
To be implemented per specs/functional.md and specs/technical.md
"""
from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    """
    Task Object Schema
    See: specs/technical.md - Task Object
    """
    task_id: UUID = uuid4()
    agent_id: UUID
    campaign_id: Optional[UUID] = None
    task_type: str
    priority: int = 5
    status: str = "pending"
    input_data: dict[str, Any] = {}
    dependencies: list[UUID] = []
    assigned_worker_id: Optional[UUID] = None
    created_at: datetime = datetime.utcnow()
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    trace_id: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# TODO: Implement per US-012 acceptance criteria