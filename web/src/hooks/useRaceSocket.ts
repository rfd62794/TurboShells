// Legacy WebSocket hook — kept for reference, not used in the web game.
// The web game uses the client-side RaceEngine instead.

import type { RaceSnapshot } from '../types';

export interface BufferedSnapshot extends RaceSnapshot {
    receivedAt: number;
}

export function useRaceSocket() {
    return {
        status: 'disconnected' as const,
        snapshot: null as RaceSnapshot | null,
        snapshotBuffer: [] as BufferedSnapshot[],
        trackLength: 1500,
        error: null as string | null,
        startRace: () => {},
        stopRace: () => {},
        setSpeed: (_s: 1 | 2 | 4) => {},
        ping: () => {},
        reconnect: () => {},
    };
}
