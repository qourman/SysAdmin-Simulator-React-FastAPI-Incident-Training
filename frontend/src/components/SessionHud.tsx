interface SessionHudProps {
  missionTitle?: string;
  playerName?: string;
  timeRemaining: number;
  score: number;
  mistakes: number;
  stepIndex: number;
  totalSteps: number;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
    .toString()
    .padStart(2, '0');
  const secs = Math.floor(seconds % 60)
    .toString()
    .padStart(2, '0');
  return `${mins}:${secs}`;
}

export function SessionHud({
  missionTitle,
  playerName,
  timeRemaining,
  score,
  mistakes,
  stepIndex,
  totalSteps,
}: SessionHudProps) {
  return (
    <section className="hud">
      <div>
        <h2>{missionTitle ?? 'Select a mission'}</h2>
        {playerName ? <p className="hud__player">Commander: {playerName}</p> : null}
      </div>
      <div className="hud__stats">
        <span>Time: {formatTime(timeRemaining)}</span>
        <span>Score: {score}</span>
        <span>Mistakes: {mistakes}</span>
        <span>
          Step: {Math.min(stepIndex + 1, totalSteps)} / {totalSteps || 1}
        </span>
      </div>
    </section>
  );
}
