export interface MissionSummary {
  id: string;
  title: string;
  difficulty: string;
  duration_seconds: number;
  scenario: string;
  objectives: string[];
  recommended_commands: string[];
}

export interface MissionStartRequest {
  mission_id: string;
  player_name?: string;
}

export interface MissionStartResponse {
  session_id: string;
  mission: MissionSummary;
  intro: string;
  first_prompt: string;
  step_index: number;
  total_steps: number;
  time_limit_seconds: number;
  started_at: string;
}

export interface CommandRequest {
  command: string;
}

export interface CommandResponse {
  accepted: boolean;
  terminal_output: string[];
  feedback: string;
  step_index: number;
  total_steps: number;
  mission_complete: boolean;
  next_prompt?: string | null;
  mistakes: number;
  score_awarded: number;
  total_score: number;
  time_remaining_seconds: number;
}

export interface HintResponse {
  step_index: number;
  hint: string;
  remaining_hints: number;
}

export interface SessionStatusResponse {
  session_id: string;
  mission_id: string;
  step_index: number;
  total_steps: number;
  mistakes: number;
  time_remaining_seconds: number;
  completed: boolean;
}
