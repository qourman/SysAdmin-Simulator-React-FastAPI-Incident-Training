import type { MissionSummary } from '../types/api';

interface MissionListProps {
  missions: MissionSummary[];
  selectedId?: string;
  onSelect: (mission: MissionSummary) => void;
}

export function MissionList({ missions, selectedId, onSelect }: MissionListProps) {
  if (!missions.length) {
    return <p className="empty">No missions loaded yet.</p>;
  }

  return (
    <ul className="mission-list">
      {missions.map((mission) => {
        const isSelected = mission.id === selectedId;
        return (
          <li key={mission.id} className={isSelected ? 'mission mission--selected' : 'mission'}>
            <button type="button" onClick={() => onSelect(mission)}>
              <div className="mission__header">
                <h3>{mission.title}</h3>
                <span className="mission__badge">{mission.difficulty}</span>
              </div>
              <p>{mission.scenario}</p>
              <ul className="mission__objectives">
                {mission.objectives.map((objective) => (
                  <li key={objective}>{objective}</li>
                ))}
              </ul>
              <div className="mission__meta">
                <span>{Math.ceil(mission.duration_seconds / 60)} min limit</span>
                <span>Commands: {mission.recommended_commands.join(', ')}</span>
              </div>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
