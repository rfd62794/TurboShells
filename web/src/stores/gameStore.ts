/**
 * Game Store (Zustand)
 * 
 * Central state management for TurboShells.
 * Replaces PyGame's GameStateInterface.observe() pattern.
 */

import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type { RaceSnapshot, RosterTurtle, RaceHistoryEntry } from '../types';

// Game locations (mirrors PyGame scene_controller)
export type GameLocation =
    | 'main_menu'
    | 'roster'
    | 'race'
    | 'breeding'
    | 'shop'
    | 'voting'
    | 'profile'
    | 'settings';

export interface GameState {
    // Player state
    money: number;
    currentLocation: GameLocation;

    // Roster
    turtles: RosterTurtle[];
    selectedTurtleId: string | null;
    selectedRacers: string[]; // IDs of turtles selected for the race (max 4)
    showRetired: boolean;

    // Race state
    raceSnapshot: RaceSnapshot | null;
    prevSnapshot: RaceSnapshot | null;
    raceStatus: 'idle' | 'starting' | 'racing' | 'finished';
    currentBet: number;
    raceSpeedMultiplier: 1 | 2 | 4;

    // Race history
    raceHistory: RaceHistoryEntry[];

    // WebSocket status
    connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';

    // UI state
    isLoading: boolean;
    errorMessage: string | null;
}

export interface GameActions {
    // Navigation
    navigate: (location: GameLocation) => void;

    // Money
    setMoney: (amount: number) => void;
    addMoney: (amount: number) => void;
    spendMoney: (amount: number) => boolean;

    // Roster
    setTurtles: (turtles: RosterTurtle[]) => void;
    selectTurtle: (id: string | null) => void;
    toggleRacer: (id: string) => void;
    toggleShowRetired: () => void;
    startRace: () => Promise<void>;

    // Race
    setRaceSnapshot: (snapshot: RaceSnapshot | null) => void;
    setPrevSnapshot: (snapshot: RaceSnapshot | null) => void;
    setRaceStatus: (status: GameState['raceStatus']) => void;
    setBet: (amount: number) => void;
    setSpeedMultiplier: (speed: 1 | 2 | 4) => void;

    // History
    setRaceHistory: (history: RaceHistoryEntry[]) => void;

    // Connection
    setConnectionStatus: (status: GameState['connectionStatus']) => void;

    // UI
    setLoading: (loading: boolean) => void;
    setError: (message: string | null) => void;

    // Fetch helpers
    fetchRoster: () => Promise<void>;
    fetchHistory: () => Promise<void>;
}

const API_BASE = 'http://localhost:8765/api';

export const useGameStore = create<GameState & GameActions>()(
    devtools(
        (set, get) => ({
            // Initial state
            money: 1000,
            currentLocation: 'main_menu',
            turtles: [],
            selectedTurtleId: null,
            selectedRacers: [],
            showRetired: false,
            raceSnapshot: null,
            prevSnapshot: null,
            raceStatus: 'idle',
            currentBet: 0,
            raceSpeedMultiplier: 1,
            raceHistory: [],
            connectionStatus: 'disconnected',
            isLoading: false,
            errorMessage: null,

            // Navigation
            navigate: (location) => set({ currentLocation: location }),

            // Money
            setMoney: (amount) => set({ money: amount }),
            addMoney: (amount) => set((state) => ({ money: state.money + amount })),
            spendMoney: (amount) => {
                const { money } = get();
                if (money >= amount) {
                    set({ money: money - amount });
                    return true;
                }
                return false;
            },

            // Roster
            setTurtles: (turtles) => set({ turtles }),
            selectTurtle: (id) => set({ selectedTurtleId: id }),
            toggleRacer: (id: string) => set((state) => {
                const isSelected = state.selectedRacers.includes(id);
                if (isSelected) {
                    return { selectedRacers: [] }; // Deselect
                } else {
                    return { selectedRacers: [id] }; // Select ONLY this one (exclusive)
                }
            }),
            toggleShowRetired: () => set((state) => ({ showRetired: !state.showRetired })),

            // Race
            setRaceSnapshot: (snapshot) => set({ raceSnapshot: snapshot }),
            setPrevSnapshot: (snapshot) => set({ prevSnapshot: snapshot }),
            setRaceStatus: (status) => set({ raceStatus: status }),
            setBet: (amount) => set({ currentBet: amount }),
            setSpeedMultiplier: (speed) => set({ raceSpeedMultiplier: speed }),

            // History
            setRaceHistory: (history) => set({ raceHistory: history }),

            // Connection
            setConnectionStatus: (status) => set({ connectionStatus: status }),

            // UI
            setLoading: (loading) => set({ isLoading: loading }),
            setError: (message) => set({ errorMessage: message }),

            // Fetch helpers
            fetchRoster: async () => {
                set({ isLoading: true });
                try {
                    const res = await fetch(`${API_BASE}/turtles`);
                    if (res.ok) {
                        const turtles = await res.json();
                        set({ turtles, isLoading: false });
                    } else {
                        throw new Error('Failed to fetch roster');
                    }
                } catch (e) {
                    set({ errorMessage: String(e), isLoading: false });
                }
            },

            fetchHistory: async () => {
                try {
                    const res = await fetch(`${API_BASE}/history?limit=20`);
                    if (res.ok) {
                        const history = await res.json();
                        set({ raceHistory: history });
                    }
                } catch (e) {
                    console.error('Failed to fetch history:', e);
                }
            },

            startRace: async () => {
                const { selectedRacers, currentBet, navigate, spendMoney } = get();

                if (selectedRacers.length === 0) {
                    set({ errorMessage: "Select at least one turtle!" });
                    return;
                }

                if (currentBet > 0 && !spendMoney(currentBet)) {
                    set({ errorMessage: "Not enough money!" });
                    return;
                }

                set({ isLoading: true, errorMessage: null });

                try {
                    // Assuming we bet on the FIRST selected turtle for now
                    const payload = {
                        turtle_ids: selectedRacers,
                    };

                    const res = await fetch(`${API_BASE}/races/start`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });

                    if (res.ok) {
                        set({ isLoading: false, raceStatus: 'starting' });
                        navigate('race');
                    } else {
                        throw new Error('Failed to start race');
                    }
                } catch (e) {
                    set({ isLoading: false, errorMessage: 'Failed to start race: ' + String(e) });
                }
            },
        }),
        { name: 'TurboShells' }
    )
);

// Selectors for common patterns
export const selectMoney = (state: GameState) => state.money;
export const selectTurtles = (state: GameState) => state.turtles;
export const selectActiveTurtles = (state: GameState) =>
    state.turtles.filter(t => !state.showRetired || t.total_races > 0);
export const selectRaceSnapshot = (state: GameState) => state.raceSnapshot;
export const selectIsRacing = (state: GameState) => state.raceStatus === 'racing';
