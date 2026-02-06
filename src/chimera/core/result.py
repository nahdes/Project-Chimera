"""
Result core model - US-014: Execute Task in Isolation
To be implemented per specs/functional.md and specs/technical.md
"""
from typing import Optional, Any
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel


class Result(BaseModel):
    """
    Result Object Schema
    See: specs/technical.md - Result Object
    """
    result_id: UUID = uuid4()
    task_id: UUID
    worker_id: UUID
    status: str
    output_data: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = {}
    error_details: Optional[dict[str, str]] = None
    created_at: datetime = datetime.utcnow()
    trace_id: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


# TODO: Implement per US-014 acceptance criteria