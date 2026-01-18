/**
 * TypeScript interfaces matching Python Pydantic models.
 * 
 * These types ensure type-safety between the Python backend and
 * TypeScript frontend. They mirror the structure of:
 * - src/engine/models.py
 * - src/engine/genome_codec.py
 */

/**
 * Turtle state snapshot from the server.
 * Matches Python TurtleState model.
 */
export interface TurtleState {
    id: string;
    name: string;
    x: number;
    y: number;
    angle: number;
    current_energy: number;
    max_energy: number;
    is_resting: boolean;
    finished: boolean;
    rank: number | null;
    genome: string;
}

/**
 * Terrain segment for track rendering.
 * Matches Python TerrainSegment model.
 */
export interface TerrainSegment {
    start_distance: number;
    end_distance: number;
    terrain_type: 'grass' | 'water' | 'rock' | 'sand' | 'mud' | 'boost';
}

/**
 * Complete race state at a single tick.
 * This is the primary payload received via WebSocket.
 */
export interface RaceSnapshot {
    tick: number;
    elapsed_ms: number;
    track_length: number;
    turtles: TurtleState[];
    terrain_ahead: TerrainSegment[];
    finished: boolean;
    winner_id: string | null;
}

/**
 * Sync data sent to late-joining clients.
 */
export interface SyncData {
    type: 'sync';
    track_length: number;
    physics_hz: number;
    broadcast_hz: number;
    current_tick: number;
    snapshot: RaceSnapshot | null;
}

/**
 * Error message from server.
 */
export interface ErrorMessage {
    type: 'error';
    message: string;
}

/**
 * Pong response from server.
 */
export interface PongMessage {
    type: 'pong';
    timestamp: number;
}

/**
 * Union of all possible server messages.
 */
export type ServerMessage = RaceSnapshot | SyncData | ErrorMessage | PongMessage;

/**
 * Parsed genome for Paper Doll rendering.
 * Decoded from genome string like "B1-S2-P0-CFF0000"
 */
export interface ParsedGenome {
    bodyType: number;
    shellType: number;
    patternType: number;
    color: string; // Hex color like "FF0000"
}

/**
 * Interpolated turtle state for smooth rendering.
 * Extends TurtleState with render-specific fields.
 */
export interface RenderTurtle extends TurtleState {
    /** Previous x position for interpolation */
    prevX: number;
    /** Previous y position for interpolation */
    prevY: number;
    /** Parsed genome for Paper Doll */
    parsedGenome: ParsedGenome;
}
