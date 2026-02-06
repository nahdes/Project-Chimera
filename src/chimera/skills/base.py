from __future__ import annotations
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type


class SkillInput(BaseModel):
    pass


class SkillOutput(BaseModel):
    success: bool
    error_message: str | None = None


class Skill(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, input_data: SkillInput) -> SkillOutput:  # type: ignore[override]
        raise NotImplementedError

    @abstractmethod
    def get_input_schema(self) -> Type[SkillInput]:
        raise NotImplementedError

    @abstractmethod
    def get_output_schema(self) -> Type[SkillOutput]:
        raise NotImplementedError
