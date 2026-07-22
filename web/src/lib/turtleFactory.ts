import { supabase } from '../lib/supabase';
import type { RosterTurtle } from '../types';

const TURTLE_NAMES = [
    'Shellsworth', 'Turbo', 'Blaze', 'Pebbles', 'Rocky',
    'Mossy', 'Speedy', 'Crawler', 'Ironback', 'Swift',
    'Drifter', 'Crunchie', 'Shard', 'Tide', 'Flint',
];

function rng(min: number, max: number) {
    return min + Math.random() * (max - min);
}

function randomGenome(): string {
    const b = Math.floor(Math.random() * 4);
    const s = Math.floor(Math.random() * 4);
    const p = Math.floor(Math.random() * 3);
    const c = Math.floor(Math.random() * 0xFFFFFF).toString(16).padStart(6, '0');
    return `B${b}-S${s}-P${p}-C${c}`;
}

export async function seedStarterTurtle(): Promise<RosterTurtle | null> {
    const name = TURTLE_NAMES[Math.floor(Math.random() * TURTLE_NAMES.length)];
    const { data, error } = await supabase
        .from('turtles')
        .insert({
            name,
            speed: rng(3, 6),
            max_energy: rng(80, 120),
            recovery: rng(0.7, 1.3),
            swim: rng(3, 7),
            climb: rng(3, 7),
            stamina: rng(3, 7),
            luck: rng(2, 6),
            genome: randomGenome(),
            generation: 0,
        })
        .select()
        .single();

    if (error) { console.error('Seed failed:', error); return null; }
    return data as RosterTurtle;
}

export async function createShopTurtle(tier: 'basic' | 'advanced' | 'champion'): Promise<RosterTurtle | null> {
    const statRanges: Record<typeof tier, [number, number]> = {
        basic:    [2, 5],
        advanced: [4, 7],
        champion: [6, 10],
    };
    const [lo, hi] = statRanges[tier];
    const name = TURTLE_NAMES[Math.floor(Math.random() * TURTLE_NAMES.length)];
    const { data, error } = await supabase
        .from('turtles')
        .insert({
            name,
            speed: rng(lo, hi),
            max_energy: rng(70 + lo * 5, 100 + hi * 5),
            recovery: rng(0.5 + lo * 0.05, 1.0 + hi * 0.05),
            swim: rng(lo, hi),
            climb: rng(lo, hi),
            stamina: rng(lo, hi),
            luck: rng(lo / 2, hi / 2),
            genome: randomGenome(),
            generation: 0,
        })
        .select()
        .single();

    if (error) { console.error('Shop turtle creation failed:', error); return null; }
    return data as RosterTurtle;
}

export function breedStats(parentA: RosterTurtle, parentB: RosterTurtle) {
    const mutate = (val: number) => val + (Math.random() - 0.4) * 0.5;
    return {
        speed:      mutate(Math.max(parentA.speed, parentB.speed)),
        max_energy: mutate(Math.max(parentA.max_energy, parentB.max_energy)),
        recovery:   mutate(Math.max(parentA.recovery, parentB.recovery)),
        swim:       mutate(Math.max(parentA.swim, parentB.swim)),
        climb:      mutate(Math.max(parentA.climb, parentB.climb)),
        stamina:    mutate(Math.max(parentA.stamina, parentB.stamina)),
        luck:       mutate(Math.max(parentA.luck, parentB.luck)),
    };
}

export function shopPriceForTurtle(turtle: RosterTurtle): number {
    const avg = (turtle.speed + turtle.max_energy / 10 + turtle.recovery * 10 + turtle.swim + turtle.climb) / 5;
    return Math.round(avg * 50 + 50);
}
