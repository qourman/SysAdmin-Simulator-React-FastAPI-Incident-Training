from contextlib import asynccontextmanager
from typing import List

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .missions import MissionSession, store
from .schemas import (
    ApiMessage,
    CommandRequest,
    CommandResponse,
    HintResponse,
    MissionSummary,
    MissionStartRequest,
    MissionStartResponse,
    SessionStatusResponse,
)


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Could load missions from external source here
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix=settings.api_prefix)


def validate_session(session_id: str) -> MissionSession:
    try:
        return store.get_session(session_id)
    except KeyError as exc:  # pragma: no cover - FastAPI handles custom
        raise HTTPException(status_code=404, detail="Session not found") from exc


@app.get("/health", response_model=ApiMessage)
def health_check() -> ApiMessage:
    return ApiMessage(detail="ok")


@router.get("/missions", response_model=List[MissionSummary])
def list_missions() -> List[MissionSummary]:
    return store.list_missions()


@router.post("/missions/start", response_model=MissionStartResponse)
def start_mission(payload: MissionStartRequest) -> MissionStartResponse:
    try:
        mission = store.get_mission(payload.mission_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Mission not found") from exc

    session = store.create_session(payload.mission_id)
    first_step = mission.steps[0]
    return MissionStartResponse(
        session_id=session.session_id,
        mission=mission.summary(),
        intro=mission.intro,
        first_prompt=first_step.prompt,
        step_index=session.step_index,
        total_steps=len(mission.steps),
        time_limit_seconds=session.time_limit_seconds,
        started_at=session.started_at,
    )


@router.post("/missions/{session_id}/command", response_model=CommandResponse)
def submit_command(session_id: str, payload: CommandRequest) -> CommandResponse:
    try:
        response = store.evaluate_command(session_id, payload.command)
        return response
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/missions/{session_id}/hint", response_model=HintResponse)
def request_hint(session_id: str) -> HintResponse:
    session = validate_session(session_id)
    mission = store.get_mission(session.mission_id)

    hint = store.request_hint(session_id)
    remaining = max(0, len(mission.steps) - session.step_index - 1)
    return HintResponse(
        step_index=session.step_index,
        hint=hint,
        remaining_hints=remaining,
    )


@router.get("/missions/{session_id}", response_model=SessionStatusResponse)
def session_status(session_id: str) -> SessionStatusResponse:
    session = validate_session(session_id)
    mission = store.get_mission(session.mission_id)
    return SessionStatusResponse(
        session_id=session.session_id,
        mission_id=mission.id,
        step_index=session.step_index,
        total_steps=len(mission.steps),
        mistakes=session.mistakes,
        time_remaining_seconds=session.time_remaining(),
        completed=session.step_index >= len(mission.steps),
    )


@app.exception_handler(Exception)
async def handle_errors(_: Request, exc: Exception):  # pragma: no cover - fallback logging
    # In production we would log the exception here
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.include_router(router)

