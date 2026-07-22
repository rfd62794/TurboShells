import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { supabase } from '../lib/supabase';
import { seedStarterTurtle } from '../lib/turtleFactory';
import type { RosterTurtle, RaceHistoryEntry, RaceSnapshot } from '../types';

export interface GameState {
    money: number;
    turtles: RosterTurtle[];
    selectedTurtleId: string | null;
    selectedRacers: string[];
    showRetired: boolean;
    raceSnapshot: RaceSnapshot | null;
    raceStatus: 'idle' | 'racing' | 'finished';
    currentBet: number;
    raceSpeedMultiplier: 1 | 2 | 4;
    raceHistory: RaceHistoryEntry[];
    isLoading: boolean;
    errorMessage: string | null;
}

export interface GameActions {
    setMoney: (amount: number) => void;
    addMoney: (amount: number) => void;
    spendMoney: (amount: number) => boolean;
    persistMoney: (amount: number) => Promise<void>;

    setTurtles: (turtles: RosterTurtle[]) => void;
    selectTurtle: (id: string | null) => void;
    toggleRacer: (id: string) => void;
    toggleShowRetired: () => void;

    setRaceSnapshot: (snapshot: RaceSnapshot | null) => void;
    setRaceStatus: (status: GameState['raceStatus']) => void;
    setBet: (amount: number) => void;
    setSpeedMultiplier: (speed: 1 | 2 | 4) => void;
    setRaceHistory: (history: RaceHistoryEntry[]) => void;
    setLoading: (v: boolean) => void;
    setError: (msg: string | null) => void;

    fetchRoster: () => Promise<void>;
    fetchHistory: () => Promise<void>;
    init: () => Promise<void>;
}

export const useGameStore = create<GameState & GameActions>()(
    devtools(
        (set, get) => ({
            money: 1000,
            turtles: [],
            selectedTurtleId: null,
            selectedRacers: [],
            showRetired: false,
            raceSnapshot: null,
            raceStatus: 'idle',
            currentBet: 0,
            raceSpeedMultiplier: 1,
            raceHistory: [],
            isLoading: false,
            errorMessage: null,

            setMoney: (amount) => set({ money: amount }),
            addMoney: (amount) => set((s) => ({ money: s.money + amount })),
            spendMoney: (amount) => {
                const { money } = get();
                if (money >= amount) { set({ money: money - amount }); return true; }
                return false;
            },
            persistMoney: async (amount) => {
                set({ money: amount });
                await supabase
                    .from('game_state')
                    .update({ money: amount, updated_at: new Date().toISOString() })
                    .eq('id', 'default');
            },

            setTurtles: (turtles) => set({ turtles }),
            selectTurtle: (id) => set({ selectedTurtleId: id }),
            toggleRacer: (id) => set((s) => ({
                selectedRacers: s.selectedRacers.includes(id) ? [] : [id],
            })),
            toggleShowRetired: () => set((s) => ({ showRetired: !s.showRetired })),

            setRaceSnapshot: (snapshot) => set({ raceSnapshot: snapshot }),
            setRaceStatus: (status) => set({ raceStatus: status }),
            setBet: (amount) => set({ currentBet: amount }),
            setSpeedMultiplier: (speed) => set({ raceSpeedMultiplier: speed }),
            setRaceHistory: (history) => set({ raceHistory: history }),
            setLoading: (v) => set({ isLoading: v }),
            setError: (msg) => set({ errorMessage: msg }),

            fetchRoster: async () => {
                set({ isLoading: true });
                const { data, error } = await supabase
                    .from('turtles')
                    .select('*')
                    .order('created_at', { ascending: true });
                if (error) { set({ errorMessage: error.message, isLoading: false }); return; }
                set({ turtles: (data as RosterTurtle[]) ?? [], isLoading: false });
            },

            fetchHistory: async () => {
                const { data } = await supabase
                    .from('race_results')
                    .select('*')
                    .order('raced_at', { ascending: false })
                    .limit(30);
                if (data) set({ raceHistory: data as RaceHistoryEntry[] });
            },

            init: async () => {
                set({ isLoading: true });

                // Load game state (money)
                const { data: gs } = await supabase
                    .from('game_state')
                    .select('*')
                    .eq('id', 'default')
                    .maybeSingle();

                if (gs) set({ money: gs.money, raceSpeedMultiplier: gs.race_speed as 1 | 2 | 4 });

                // Load roster
                const { data: turtles } = await supabase
                    .from('turtles')
                    .select('*')
                    .order('created_at', { ascending: true });

                const roster = (turtles ?? []) as RosterTurtle[];

                // Seed a starter turtle if roster is empty
                if (roster.length === 0) {
                    const starter = await seedStarterTurtle();
                    if (starter) set({ turtles: [starter] });
                } else {
                    set({ turtles: roster });
                }

                // Load history
                const { data: history } = await supabase
                    .from('race_results')
                    .select('*')
                    .order('raced_at', { ascending: false })
                    .limit(30);

                set({ raceHistory: (history ?? []) as RaceHistoryEntry[], isLoading: false });
            },
        }),
        { name: 'TurboShells' }
    )
);
