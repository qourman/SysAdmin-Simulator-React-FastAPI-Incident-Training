import type {
  CommandRequest,
  CommandResponse,
  HintResponse,
  MissionStartRequest,
  MissionStartResponse,
  MissionSummary,
  SessionStatusResponse,
} from '../types/api';

const API_URL = (
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000/api'
).replace(/\/$/, '');

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!resp.ok) {
    const detail = await resp.text();
    throw new Error(detail || resp.statusText);
  }

  return (await resp.json()) as T;
}

export const api = {
  listMissions: () => request<MissionSummary[]>('/missions'),
  startMission: (payload: MissionStartRequest) =>
    request<MissionStartResponse>('/missions/start', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  submitCommand: (sessionId: string, payload: CommandRequest) =>
    request<CommandResponse>(`/missions/${sessionId}/command`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  requestHint: (sessionId: string) =>
    request<HintResponse>(`/missions/${sessionId}/hint`, {
      method: 'POST',
    }),
  fetchSessionStatus: (sessionId: string) => request<SessionStatusResponse>(`/missions/${sessionId}`),
};
