from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MissionStepSchema(BaseModel):
    id: str
    goal: str
    hint: str


class MissionSummary(BaseModel):
    id: str
    title: str
    difficulty: str
    duration_seconds: int = Field(..., ge=30)
    scenario: str
    objectives: List[str]
    recommended_commands: List[str] = Field(default_factory=list)


class MissionStartRequest(BaseModel):
    mission_id: str
    player_name: Optional[str] = Field(default=None, max_length=64)


class MissionStartResponse(BaseModel):
    session_id: str
    mission: MissionSummary
    intro: str
    first_prompt: str
    step_index: int
    total_steps: int
    time_limit_seconds: int
    started_at: datetime


class CommandRequest(BaseModel):
    command: str = Field(..., min_length=1)


class CommandResponse(BaseModel):
    accepted: bool
    terminal_output: List[str]
    feedback: str
    step_index: int
    total_steps: int
    mission_complete: bool
    next_prompt: Optional[str] = None
    mistakes: int
    score_awarded: int
    total_score: int
    time_remaining_seconds: int


class HintResponse(BaseModel):
    step_index: int
    hint: str
    remaining_hints: int


class SessionStatusResponse(BaseModel):
    session_id: str
    mission_id: str
    step_index: int
    total_steps: int
    mistakes: int
    time_remaining_seconds: int
    completed: bool


class ApiMessage(BaseModel):
    detail: str
