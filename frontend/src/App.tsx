import { useEffect, useMemo, useState } from 'react';
import './App.css';
import { api } from './api/client';
import { MissionList } from './components/MissionList';
import { SessionHud } from './components/SessionHud';
import { TerminalView } from './components/TerminalView';
import { useCountdown } from './hooks/useCountdown';
import type {
  CommandResponse,
  MissionStartResponse,
  MissionSummary,
} from './types/api';

function App() {
  const [missions, setMissions] = useState<MissionSummary[]>([]);
  const [selectedMission, setSelectedMission] = useState<MissionSummary>();
  const [playerName, setPlayerName] = useState('');
  const [session, setSession] = useState<MissionStartResponse | null>(null);
  const [terminalLines, setTerminalLines] = useState<string[]>([]);
  const [mistakes, setMistakes] = useState(0);
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMissionComplete, setMissionComplete] = useState(false);
  const { secondsRemaining, start, stop, setSecondsRemaining } = useCountdown(0);

  useEffect(() => {
    api
      .listMissions()
      .then(setMissions)
      .catch((error) => {
        setFeedback(`Failed to load missions: ${error.message}`);
      });
  }, []);

  const missionTitle = session?.mission.title ?? selectedMission?.title ?? 'SysAdmin Simulator';

  const startMission = async () => {
    if (!selectedMission || isLoading) {
      return;
    }

    setIsLoading(true);
    setFeedback(null);
    try {
      const response = await api.startMission({
        mission_id: selectedMission.id,
        player_name: playerName || undefined,
      });
      setSession(response);
      setMistakes(response.step_index);
      setScore(0);
      setMissionComplete(false);
      const introLines = [
        `Mission: ${response.mission.title}`,
        response.mission.scenario,
        '',
        response.intro,
        '',
        `First task: ${response.first_prompt}`,
      ];
      setTerminalLines(introLines);
      start(response.time_limit_seconds);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setFeedback(`Unable to start mission: ${message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const appendTerminalOutput = (lines: string | string[]) => {
    setTerminalLines((prev) => prev.concat(lines));
  };

  const handleCommand = async (command: string) => {
    if (!command || !session || isMissionComplete) {
      return;
    }

    appendTerminalOutput(`$ ${command}`);

    try {
      const result = await api.submitCommand(session.session_id, { command });
      processCommandResponse(result);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      appendTerminalOutput(`Error: ${message}`);
      setFeedback(`Command failed: ${message}`);
    }
  };

  const processCommandResponse = (result: CommandResponse) => {
    appendTerminalOutput(result.terminal_output);
    setMistakes(result.mistakes);
    setScore(result.total_score);
    setFeedback(result.feedback);
    setSecondsRemaining(result.time_remaining_seconds);
    setSession((prev) => (prev ? { ...prev, step_index: result.step_index } : prev));

    if (result.next_prompt) {
      appendTerminalOutput(['', result.next_prompt]);
    }

    if (result.mission_complete) {
      setMissionComplete(true);
      stop();
      appendTerminalOutput(['', 'Mission complete! Update the status page and celebrate.']);
    }
  };

  const handleHint = async () => {
    if (!session) {
      return;
    }
    try {
      const response = await api.requestHint(session.session_id);
      appendTerminalOutput([`Hint: ${response.hint}`]);
      setFeedback(`Hint used. ${response.remaining_hints} hints remain.`);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown error';
      setFeedback(`Hint failed: ${message}`);
    }
  };

  const handleAbort = () => {
    setSession(null);
    setTerminalLines([]);
    setMistakes(0);
    setScore(0);
    setMissionComplete(false);
    setFeedback('Mission aborted. Select a mission to deploy again.');
    stop();
  };

  const isSessionActive = Boolean(session && !isMissionComplete);

  const playerBadge = useMemo(() => playerName || 'Cadet', [playerName]);
  const promptLabel = useMemo(
    () => playerBadge.toLowerCase().replace(/\s+/g, '-'),
    [playerBadge],
  );

  return (
    <div className="app">
      <header>
        <h1>SysAdmin Simulator</h1>
        <p className="subtitle">Built by Aymane Qouraiche • Train for the on-call trenches</p>
      </header>

      <main className="layout">
        <aside className="sidebar">
          <div className="player-input">
            <label htmlFor="playerName">Callsign</label>
            <input
              id="playerName"
              type="text"
              value={playerName}
              placeholder="Aymane Qouraiche"
              onChange={(event) => setPlayerName(event.target.value)}
            />
          </div>
          <MissionList
            missions={missions}
            selectedId={selectedMission?.id}
            onSelect={setSelectedMission}
          />
          <button
            type="button"
            className="primary"
            onClick={startMission}
            disabled={!selectedMission || isLoading}
          >
            {isLoading ? 'Launching…' : 'Start Mission'}
          </button>
          <button
            type="button"
            className="secondary"
            onClick={handleAbort}
            disabled={!session}
          >
            Abort Mission
          </button>
        </aside>

        <section className="workspace">
          <SessionHud
            missionTitle={missionTitle}
            playerName={playerBadge}
            timeRemaining={secondsRemaining}
            score={score}
            mistakes={mistakes}
            stepIndex={session?.step_index ?? 0}
            totalSteps={session?.total_steps ?? selectedMission?.objectives.length ?? 0}
          />

          <div className="terminal-area">
            <TerminalView
              lines={terminalLines}
              disabled={!isSessionActive}
              onCommand={handleCommand}
              promptLabel={promptLabel}
            />
            <div className="terminal-controls">
              <button type="button" onClick={handleHint} disabled={!session || isMissionComplete}>
                Request Hint
              </button>
              <span className="feedback">{feedback}</span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
