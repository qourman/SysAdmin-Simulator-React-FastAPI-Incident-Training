from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .schemas import CommandResponse, MissionSummary


@dataclass
class MissionStep:
    id: str
    prompt: str
    expected_commands: List[str]
    success_output: List[str]
    next_prompt: Optional[str]
    hint: str
    score: int


@dataclass
class Mission:
    id: str
    title: str
    difficulty: str
    duration_seconds: int
    scenario: str
    objectives: List[str]
    recommended_commands: List[str]
    intro: str
    steps: List[MissionStep]

    def summary(self) -> MissionSummary:
        return MissionSummary(
            id=self.id,
            title=self.title,
            difficulty=self.difficulty,
            duration_seconds=self.duration_seconds,
            scenario=self.scenario,
            objectives=self.objectives,
            recommended_commands=self.recommended_commands,
        )


@dataclass
class MissionSession:
    session_id: str
    mission_id: str
    step_index: int = 0
    mistakes: int = 0
    total_score: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    time_limit_seconds: int = 900
    history: List[str] = field(default_factory=list)
    last_hint_index: Optional[int] = None

    @property
    def expires_at(self) -> datetime:
        return self.started_at + timedelta(seconds=self.time_limit_seconds)

    def time_remaining(self) -> int:
        remaining = int((self.expires_at - datetime.utcnow()).total_seconds())
        return max(0, remaining)


class MissionStore:
    def __init__(self) -> None:
        self._missions: Dict[str, Mission] = {}
        self._sessions: Dict[str, MissionSession] = {}

    def list_missions(self) -> List[MissionSummary]:
        return [mission.summary() for mission in self._missions.values()]

    def get_mission(self, mission_id: str) -> Mission:
        if mission_id not in self._missions:
            raise KeyError("Mission not found")
        return self._missions[mission_id]

    def register_mission(self, mission: Mission) -> None:
        self._missions[mission.id] = mission

    def create_session(self, mission_id: str) -> MissionSession:
        mission = self.get_mission(mission_id)
        session = MissionSession(
            session_id=str(uuid.uuid4()),
            mission_id=mission_id,
            time_limit_seconds=mission.duration_seconds,
        )
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> MissionSession:
        if session_id not in self._sessions:
            raise KeyError("Session not found")
        return self._sessions[session_id]

    def evaluate_command(
        self,
        session_id: str,
        command: str,
    ) -> CommandResponse:
        session = self.get_session(session_id)
        mission = self.get_mission(session.mission_id)

        if session.step_index >= len(mission.steps):
            return CommandResponse(
                accepted=False,
                terminal_output=["Mission already completed"],
                feedback="No more tasks left. Great work!",
                step_index=session.step_index,
                total_steps=len(mission.steps),
                mission_complete=True,
                next_prompt=None,
                mistakes=session.mistakes,
                score_awarded=0,
                total_score=session.total_score,
                time_remaining_seconds=session.time_remaining(),
            )

        if session.time_remaining() <= 0:
            session.mistakes += 1
            return CommandResponse(
                accepted=False,
                terminal_output=["Session expired"],
                feedback="Time is up! Restart the mission to try again.",
                step_index=session.step_index,
                total_steps=len(mission.steps),
                mission_complete=False,
                mistakes=session.mistakes,
                score_awarded=0,
                total_score=session.total_score,
                time_remaining_seconds=0,
            )

        current_step = mission.steps[session.step_index]
        normalized = command.strip().lower()
        session.history.append(command)

        # allow slight variations by checking startswith for expected patterns
        matched = any(
            normalized.startswith(expected) for expected in current_step.expected_commands
        )

        if matched:
            session.total_score += current_step.score
            session.step_index += 1
            next_prompt = (
                mission.steps[session.step_index].prompt
                if session.step_index < len(mission.steps)
                else current_step.next_prompt
            )
            success = CommandResponse(
                accepted=True,
                terminal_output=current_step.success_output,
                feedback="Great job!",
                step_index=session.step_index,
                total_steps=len(mission.steps),
                mission_complete=session.step_index >= len(mission.steps),
                next_prompt=next_prompt,
                mistakes=session.mistakes,
                score_awarded=current_step.score,
                total_score=session.total_score,
                time_remaining_seconds=session.time_remaining(),
            )
            return success

        session.mistakes += 1
        return CommandResponse(
            accepted=False,
            terminal_output=["command not recognized"],
            feedback="That didn't solve it. Check the mission objectives and try another command.",
            step_index=session.step_index,
            total_steps=len(mission.steps),
            mission_complete=False,
            next_prompt=None,
            mistakes=session.mistakes,
            score_awarded=0,
            total_score=session.total_score,
            time_remaining_seconds=session.time_remaining(),
        )

    def request_hint(self, session_id: str) -> str:
        session = self.get_session(session_id)
        mission = self.get_mission(session.mission_id)
        if session.step_index >= len(mission.steps):
            return "Mission complete! No hints needed."

        current_step = mission.steps[session.step_index]
        session.last_hint_index = session.step_index
        return current_step.hint

    def session_status(self, session_id: str) -> MissionSession:
        return self.get_session(session_id)


store = MissionStore()


store.register_mission(
    Mission(
        id="missing-route",
        title="Restore Network Connectivity",
        difficulty="Intermediate",
        duration_seconds=900,
        scenario="A remote employee lost connectivity after a VPN disconnect.",
        objectives=[
            "Inspect network interface configuration",
            "Restore missing default route",
            "Verify connectivity",
        ],
        recommended_commands=["ip addr", "ip route", "ping"],
        intro=(
            "You're on call and Aymane Qouraiche trusts you with restoring service."
            " The user reports they can't reach any websites after their VPN session dropped."
        ),
        steps=[
            MissionStep(
                id="inspect",
                prompt="Check the active network interfaces and identify any missing routes.",
                expected_commands=["ip addr", "sudo ip addr", "ifconfig"],
                success_output=[
                    "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST> mtu 1500",
                    "    inet 10.0.0.42/24 brd 10.0.0.255 scope global eth0",
                ],
                next_prompt="Nice. The default gateway is missing. Add a route via 10.0.0.1.",
                hint="Use ip route add to define the default route.",
                score=100,
            ),
            MissionStep(
                id="route",
                prompt="Add the missing default route using the correct gateway.",
                expected_commands=[
                    "ip route add default via 10.0.0.1",
                    "sudo ip route add default via 10.0.0.1",
                ],
                success_output=["Route added: default via 10.0.0.1 dev eth0"],
                next_prompt="Great! Confirm the fix by pinging 8.8.8.8.",
                hint="Use ping with ctrl+c to stop after a few replies.",
                score=150,
            ),
            MissionStep(
                id="ping",
                prompt="Validate connectivity by pinging a well-known IP.",
                expected_commands=["ping 8.8.8.8", "ping -c 4 8.8.8.8"],
                success_output=[
                    "PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.",
                    "64 bytes from 8.8.8.8: icmp_seq=1 ttl=115 time=22.0 ms",
                    "--- 8.8.8.8 ping statistics ---",
                    "3 packets transmitted, 3 received, 0% packet loss",
                ],
                next_prompt="All set! The user confirms internet access is back.",
                hint="A simple ping test should do.",
                score=200,
            ),
        ],
    )
)

store.register_mission(
    Mission(
        id="log-chaos",
        title="Calm a Crashing Service",
        difficulty="Advanced",
        duration_seconds=1200,
        scenario="A containerized web service keeps restarting on production and users see 503 errors.",
        objectives=[
            "Inspect recent service logs",
            "Identify the failing dependency",
            "Restart the service after applying the fix",
        ],
        recommended_commands=["journalctl", "systemctl status", "systemctl restart"],
        intro=(
            "Traffic is spiking and leadership paged you directly, Aymane Qouraiche."
            " The API is flapping and customers are complaining."
        ),
        steps=[
            MissionStep(
                id="logs",
                prompt="Check the service logs for the last five minutes and spot the crash loop.",
                expected_commands=[
                    "journalctl -u web-api --since -5m",
                    "sudo journalctl -u web-api --since -5m",
                ],
                success_output=[
                    "Oct 10 11:02:01 api-host web-api[4242]: ImportError: cannot import name 'connect_db'",
                    "Oct 10 11:02:01 api-host systemd[1]: web-api.service: Main process exited, code=exited",
                ],
                next_prompt="Looks like a missing dependency. Inspect the service status for clues.",
                hint="Use journalctl with --since to narrow down logs.",
                score=120,
            ),
            MissionStep(
                id="status",
                prompt="Check the service status to confirm the failing unit and environment.",
                expected_commands=["systemctl status web-api", "sudo systemctl status web-api"],
                success_output=[
                    "web-api.service - Web API",
                    "   Loaded: loaded (/etc/systemd/system/web-api.service; enabled)",
                    "   Active: failed (Result: exit-code)",
                    "   Process: 4242 ExecStart=/opt/web-api/start.sh (code=exited, status=1/FAILURE)",
                ],
                next_prompt="Add the missing dependency and restart the service to confirm.",
                hint="systemctl status provides the recent log tail too.",
                score=160,
            ),
            MissionStep(
                id="restart",
                prompt="Restart the service now that the dependency is fixed in the container image.",
                expected_commands=[
                    "systemctl restart web-api",
                    "sudo systemctl restart web-api",
                ],
                success_output=[
                    "web-api.service - Web API",
                    "   Active: active (running)",
                ],
                next_prompt="Service is running steady. Update status page and breathe.",
                hint="Use systemctl restart followed by status to double-check.",
                score=220,
            ),
        ],
    )
)

store.register_mission(
    Mission(
        id="sandbox-check",
        title="Warm Up Diagnostics",
        difficulty="Beginner",
        duration_seconds=300,
        scenario="A practice host needs a basic health check before training begins.",
        objectives=[
            "Print the working directory",
            "List the files in the directory",
        ],
        recommended_commands=["pwd", "ls"],
        intro="Use this quick mission to verify the terminal and scoring flow before tackling tougher incidents.",
        steps=[
            MissionStep(
                id="pwd",
                prompt="Confirm where you're located in the filesystem.",
                expected_commands=["pwd", "printf $PWD", "echo $PWD"],
                success_output=["/home/sysadmin"],
                next_prompt="Great. Now enumerate the files so you know what tools are available.",
                hint="Run pwd or an equivalent command to print the current directory.",
                score=25,
            ),
            MissionStep(
                id="ls",
                prompt="List the files to ensure your toolkit is present.",
                expected_commands=["ls", "ls -la"],
                success_output=[
                    "tools.sh  runbook.md  diagnostics.log",
                ],
                next_prompt="Sandbox checks out. You're ready for the real missions!",
                hint="Use ls to display directory contents.",
                score=50,
            ),
        ],
    )
)
