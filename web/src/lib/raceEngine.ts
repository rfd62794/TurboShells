/**
 * Client-side race simulation engine.
 * Mirrors the Python race_engine.py physics at 60Hz.
 */

export type TerrainType = 'grass' | 'water' | 'rocks' | 'sand' | 'mud' | 'boost';

export interface TerrainSegment {
    start: number;
    end: number;
    type: TerrainType;
}

export interface RaceTurtle {
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
    // mutable race state
    current_energy: number;
    race_distance: number;
    is_resting: boolean;
    finished: boolean;
    rank: number | null;
    is_npc: boolean;
}

export interface RaceSnapshot {
    tick: number;
    elapsed_ms: number;
    track_length: number;
    turtles: RaceTurtle[];
    terrain: TerrainSegment[];
    finished: boolean;
    winner_id: string | null;
    finishers: string[];
}

const RECOVERY_THRESHOLD = 0.5;
const TERRAIN_DIFFICULTY = 0.8;

function getTerrainAt(distance: number, terrain: TerrainSegment[]): TerrainType {
    for (const seg of terrain) {
        if (distance >= seg.start && distance < seg.end) return seg.type;
    }
    return 'grass';
}

function terrainSpeedMult(type: TerrainType, turtle: RaceTurtle): number {
    switch (type) {
        case 'water':  return (turtle.swim / 10) * TERRAIN_DIFFICULTY;
        case 'rocks':  return (turtle.climb / 10) * TERRAIN_DIFFICULTY;
        case 'sand':   return (turtle.recovery / 10) * TERRAIN_DIFFICULTY;
        case 'mud':    return (turtle.current_energy / turtle.max_energy) * TERRAIN_DIFFICULTY;
        case 'boost':  return 1.4;
        default:       return 1.0;
    }
}

function generateTerrain(trackLength: number): TerrainSegment[] {
    const segments: TerrainSegment[] = [];
    const types: TerrainType[] = ['grass', 'water', 'rocks', 'sand', 'mud', 'boost'];
    let pos = 0;
    // First 10% always grass
    segments.push({ start: 0, end: trackLength * 0.1, type: 'grass' });
    pos = trackLength * 0.1;

    while (pos < trackLength * 0.95) {
        const type = types[Math.floor(Math.random() * types.length)];
        const len = trackLength * (0.05 + Math.random() * 0.15);
        segments.push({ start: pos, end: Math.min(pos + len, trackLength * 0.95), type });
        pos += len;
    }
    segments.push({ start: pos, end: trackLength, type: 'grass' });
    return segments;
}

export function generateNpcTurtle(index: number): RaceTurtle {
    const statBase = 3 + Math.random() * 5;
    return {
        id: `npc-${index}-${Date.now()}`,
        name: `NPC ${['Blaze', 'Rocket', 'Zoom', 'Flash', 'Dash'][index % 5]}`,
        speed: statBase + Math.random() * 2,
        max_energy: 80 + Math.random() * 40,
        recovery: 0.8 + Math.random() * 0.6,
        swim: statBase + Math.random() * 2,
        climb: statBase + Math.random() * 2,
        stamina: statBase + Math.random() * 2,
        luck: Math.random() * 5,
        genome: `B${Math.floor(Math.random()*4)}-S${Math.floor(Math.random()*4)}-P${Math.floor(Math.random()*3)}-C${Math.floor(Math.random()*0xFFFFFF).toString(16).padStart(6,'0')}`,
        current_energy: 100 + Math.random() * 40,
        race_distance: 0,
        is_resting: false,
        finished: false,
        rank: null,
        is_npc: true,
    };
}

export class RaceEngine {
    private turtles: RaceTurtle[];
    private terrain: TerrainSegment[];
    private trackLength: number;
    private tick: number = 0;
    private elapsed_ms: number = 0;
    private finishers: string[] = [];
    private winner_id: string | null = null;
    private finished: boolean = false;

    constructor(turtles: RaceTurtle[], trackLength = 1000) {
        this.trackLength = trackLength;
        this.terrain = generateTerrain(trackLength);
        // Deep-clone turtles so we don't mutate the store
        this.turtles = turtles.map(t => ({
            ...t,
            current_energy: t.max_energy,
            race_distance: 0,
            is_resting: false,
            finished: false,
            rank: null,
        }));
    }

    step(dtMs: number, speedMult: 1 | 2 | 4 = 1): RaceSnapshot {
        if (this.finished) return this.snapshot();

        const physicsSteps = speedMult;
        const dtPerStep = dtMs / physicsSteps;

        for (let s = 0; s < physicsSteps; s++) {
            this.tick++;
            this.elapsed_ms += dtPerStep;

            for (const turtle of this.turtles) {
                if (turtle.finished) continue;

                if (turtle.is_resting) {
                    turtle.current_energy += turtle.recovery * (dtPerStep / 16.67);
                    if (turtle.current_energy >= turtle.max_energy * RECOVERY_THRESHOLD) {
                        turtle.is_resting = false;
                    }
                    continue;
                }

                // Deplete energy
                const energyCost = 0.5 * (dtPerStep / 16.67);
                turtle.current_energy = Math.max(0, turtle.current_energy - energyCost);

                if (turtle.current_energy <= 0) {
                    turtle.is_resting = true;
                    continue;
                }

                const terrain = getTerrainAt(turtle.race_distance, this.terrain);
                const mult = terrainSpeedMult(terrain, turtle);
                const luckBonus = 1 + (turtle.luck / 100) * (Math.random() - 0.5) * 0.2;
                const move = (turtle.speed * mult * luckBonus * (dtPerStep / 16.67)) * 0.8;
                turtle.race_distance += move;

                if (turtle.race_distance >= this.trackLength && !turtle.finished) {
                    turtle.finished = true;
                    turtle.race_distance = this.trackLength;
                    const rank = this.finishers.length + 1;
                    turtle.rank = rank;
                    this.finishers.push(turtle.id);
                    if (rank === 1) this.winner_id = turtle.id;
                }
            }

            const allDone = this.turtles.every(t => t.finished);
            if (allDone) {
                this.finished = true;
                break;
            }
        }

        return this.snapshot();
    }

    private snapshot(): RaceSnapshot {
        return {
            tick: this.tick,
            elapsed_ms: this.elapsed_ms,
            track_length: this.trackLength,
            turtles: this.turtles.map(t => ({ ...t })),
            terrain: this.terrain,
            finished: this.finished,
            winner_id: this.winner_id,
            finishers: [...this.finishers],
        };
    }

    getTrackLength() { return this.trackLength; }
    getTerrain() { return this.terrain; }
    isFinished() { return this.finished; }
}
