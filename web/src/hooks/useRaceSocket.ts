/**
 * useRaceSocket Hook
 * 
 * Connects to the /ws/race WebSocket endpoint and provides race state
 * to React components. Handles:
 * - Connection lifecycle
 * - Late-joiner sync
 * - Snapshot buffering for interpolation
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { RaceSnapshot, SyncData, ServerMessage } from '../types';

export interface UseRaceSocketOptions {
    /** WebSocket URL (default: ws://localhost:8765/ws/race) */
    url?: string;
    /** Auto-reconnect on disconnect */
    autoReconnect?: boolean;
    /** Reconnect delay in ms */
    reconnectDelay?: number;
}

export interface RaceSocketState {
    /** Current connection status */
    status: 'connecting' | 'connected' | 'disconnected' | 'error';
    /** Latest race snapshot */
    snapshot: RaceSnapshot | null;
    /** Previous snapshot for interpolation */
    prevSnapshot: RaceSnapshot | null;
    /** Track length from sync data */
    trackLength: number;
    /** Error message if connection failed */
    error: string | null;
}

export interface RaceSocketActions {
    /** Start a new race */
    startRace: () => void;
    /** Stop the current race */
    stopRace: () => void;
    /** Send a ping to keep connection alive */
    ping: () => void;
    /** Manually reconnect */
    reconnect: () => void;
}

const DEFAULT_URL = 'ws://localhost:8765/ws/race';

export function useRaceSocket(
    options: UseRaceSocketOptions = {}
): RaceSocketState & RaceSocketActions {
    const {
        url = DEFAULT_URL,
        autoReconnect = true,
        reconnectDelay = 3000,
    } = options;

    const [status, setStatus] = useState<RaceSocketState['status']>('disconnected');
    const [snapshot, setSnapshot] = useState<RaceSnapshot | null>(null);
    const [prevSnapshot, setPrevSnapshot] = useState<RaceSnapshot | null>(null);
    const [trackLength, setTrackLength] = useState<number>(1500);
    const [error, setError] = useState<string | null>(null);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<number | null>(null);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        setStatus('connecting');
        setError(null);

        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
            setStatus('connected');
            console.log('[useRaceSocket] Connected to', url);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data) as ServerMessage;

                // Handle sync data (late-joiner)
                if ('type' in data && data.type === 'sync') {
                    const syncData = data as SyncData;
                    setTrackLength(syncData.track_length);
                    if (syncData.snapshot) {
                        setSnapshot(syncData.snapshot);
                    }
                    console.log('[useRaceSocket] Synced at tick', syncData.current_tick);
                    return;
                }

                // Handle error
                if ('type' in data && data.type === 'error') {
                    setError(data.message);
                    return;
                }

                // Handle pong
                if ('type' in data && data.type === 'pong') {
                    return;
                }

                // Handle race snapshot
                if ('tick' in data) {
                    const raceSnapshot = data as RaceSnapshot;
                    setPrevSnapshot(snapshot);
                    setSnapshot(raceSnapshot);
                }
            } catch (e) {
                console.error('[useRaceSocket] Parse error:', e);
            }
        };

        ws.onclose = () => {
            setStatus('disconnected');
            wsRef.current = null;
            console.log('[useRaceSocket] Disconnected');

            if (autoReconnect) {
                reconnectTimeoutRef.current = window.setTimeout(() => {
                    console.log('[useRaceSocket] Attempting reconnect...');
                    connect();
                }, reconnectDelay);
            }
        };

        ws.onerror = (e) => {
            setStatus('error');
            setError('WebSocket connection error');
            console.error('[useRaceSocket] Error:', e);
        };
    }, [url, autoReconnect, reconnectDelay, snapshot]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
        }
        wsRef.current?.close();
        wsRef.current = null;
        setStatus('disconnected');
    }, []);

    const send = useCallback((message: object) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        }
    }, []);

    const startRace = useCallback(() => {
        send({ action: 'start' });
    }, [send]);

    const stopRace = useCallback(() => {
        send({ action: 'stop' });
    }, [send]);

    const ping = useCallback(() => {
        send({ action: 'ping' });
    }, [send]);

    const reconnect = useCallback(() => {
        disconnect();
        connect();
    }, [disconnect, connect]);

    // Auto-connect on mount
    useEffect(() => {
        connect();
        return () => disconnect();
    }, [connect, disconnect]);

    return {
        status,
        snapshot,
        prevSnapshot,
        trackLength,
        error,
        startRace,
        stopRace,
        ping,
        reconnect,
    };
}
