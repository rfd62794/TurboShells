/**
 * useRoster Hook
 * 
 * Fetches the turtle roster from the REST API on mount.
 * This populates the UI before the WebSocket race starts.
 */

import { useState, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:8765/api';

export interface RosterTurtle {
    id: number;
    turtle_id: string;
    name: string;
    speed: number;
    max_energy: number;
    recovery: number;
    swim: number;
    climb: number;
    genome: string;
    total_races: number;
    total_wins: number;
    created_at: string;
}

export interface RaceHistoryEntry {
    id: number;
    race_id: string;
    turtle_name: string;
    rank: number;
    final_distance: number;
    final_time_ms: number;
    raced_at: string;
}

export interface UseRosterResult {
    turtles: RosterTurtle[];
    history: RaceHistoryEntry[];
    loading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
}

export function useRoster(): UseRosterResult {
    const [turtles, setTurtles] = useState<RosterTurtle[]>([]);
    const [history, setHistory] = useState<RaceHistoryEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchRoster = useCallback(async () => {
        setLoading(true);
        setError(null);

        try {
            const [turtlesRes, historyRes] = await Promise.all([
                fetch(`${API_BASE}/turtles`),
                fetch(`${API_BASE}/history?limit=20`),
            ]);

            if (!turtlesRes.ok) {
                throw new Error(`Failed to fetch turtles: ${turtlesRes.status}`);
            }

            const turtlesData = await turtlesRes.json();
            setTurtles(turtlesData);

            if (historyRes.ok) {
                const historyData = await historyRes.json();
                setHistory(historyData);
            }

            console.log(`[useRoster] Loaded ${turtlesData.length} turtles`);
        } catch (e) {
            const message = e instanceof Error ? e.message : 'Unknown error';
            setError(message);
            console.error('[useRoster] Error:', message);
        } finally {
            setLoading(false);
        }
    }, []);

    // Fetch on mount
    useEffect(() => {
        fetchRoster();
    }, [fetchRoster]);

    return {
        turtles,
        history,
        loading,
        error,
        refresh: fetchRoster,
    };
}
