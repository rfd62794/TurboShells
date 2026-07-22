export type { DbTurtle, DbRaceResult, DbGameState } from '../lib/supabase';
export type { RaceSnapshot, RaceTurtle, TerrainSegment, TerrainType } from '../lib/raceEngine';

export interface RosterTurtle {
    id: string;
    name: string;
    speed: number;
    max_energy: number;
    recovery: number;
    swim: number;
    climb: number;
    stamina: number;
    luck: number;
    genome: string;
    total_races: number;
    total_wins: number;
    generation: number;
    parent_a_id: string | null;
    parent_b_id: string | null;
    is_retired: boolean;
    created_at: string;
}

export interface RaceHistoryEntry {
    id: string;
    race_id: string;
    turtle_id: string | null;
    turtle_name: string;
    rank: number;
    final_distance: number;
    final_time_ms: number;
    bet_amount: number;
    won_bet: boolean;
    raced_at: string;
}

export interface ParsedGenome {
    bodyType: number;
    shellType: number;
    patternType: number;
    color: string;
}

// Legacy WebSocket types kept for compile compatibility
export interface SyncData {
    type: 'sync';
    track_length: number;
    current_tick: number;
    snapshot: unknown;
}

export interface ServerMessage {
    type: string;
    [key: string]: unknown;
}
