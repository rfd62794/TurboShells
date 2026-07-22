import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useGameStore } from '../stores';
import { TurtleCard } from '../components/cards/TurtleCard';
import { supabase } from '../lib/supabase';
import { breedStats } from '../lib/turtleFactory';
import type { RosterTurtle } from '../types';
import '../styles/retro.css';
import './BreedingLab.css';

const BREED_COST = 200;

const NAMES = [
    'Apex', 'Nexus', 'Titan', 'Prism', 'Vortex', 'Cipher', 'Zenith',
    'Relic', 'Forge', 'Nova', 'Comet', 'Flare', 'Ember', 'Drift',
];

function randomName() {
    return NAMES[Math.floor(Math.random() * NAMES.length)];
}

function blendGenomes(a: string, b: string): string {
    const parse = (g: string) => {
        const parts: Record<string, string> = {};
        g.split('-').forEach(p => { if (p) parts[p[0]] = p.slice(1); });
        return parts;
    };
    const ga = parse(a);
    const gb = parse(b);
    const pick = (key: string) => Math.random() < 0.5 ? (ga[key] ?? gb[key]) : (gb[key] ?? ga[key]);
    return `B${pick('B')}-S${pick('S')}-P${pick('P')}-C${pick('C')}`;
}

export default function BreedingLab() {
    const navigate = useNavigate();
    const { turtles, money, persistMoney, fetchRoster } = useGameStore();
    const [parentA, setParentA] = useState<string | null>(null);
    const [parentB, setParentB] = useState<string | null>(null);
    const [isBreeding, setIsBreeding] = useState(false);
    const [result, setResult] = useState<RosterTurtle | null>(null);
    const [error, setError] = useState<string | null>(null);

    const activeTurtles = turtles.filter(t => !t.is_retired);

    const handleSelect = (id: string) => {
        if (parentA === id) { setParentA(null); return; }
        if (parentB === id) { setParentB(null); return; }
        if (!parentA) { setParentA(id); return; }
        if (!parentB) { setParentB(id); return; }
        setParentA(id);
        setParentB(null);
    };

    const handleBreed = async () => {
        if (!parentA || !parentB) return;
        if (money < BREED_COST) { setError('Not enough money to breed!'); return; }

        setIsBreeding(true);
        setError(null);

        const pA = turtles.find(t => t.id === parentA)!;
        const pB = turtles.find(t => t.id === parentB)!;
        const stats = breedStats(pA, pB);
        const genome = blendGenomes(pA.genome, pB.genome);
        const name = randomName();

        const { data, error: dbErr } = await supabase
            .from('turtles')
            .insert({
                name,
                ...stats,
                genome,
                generation: Math.max(pA.generation, pB.generation) + 1,
                parent_a_id: pA.id,
                parent_b_id: pB.id,
            })
            .select()
            .single();

        if (dbErr) { setError(dbErr.message); setIsBreeding(false); return; }

        // Retire parents
        await supabase
            .from('turtles')
            .update({ is_retired: true })
            .in('id', [parentA, parentB]);

        await persistMoney(money - BREED_COST);
        await fetchRoster();

        setResult(data as RosterTurtle);
        setParentA(null);
        setParentB(null);
        setIsBreeding(false);
    };

    const pAData = turtles.find(t => t.id === parentA);
    const pBData = turtles.find(t => t.id === parentB);
    const canBreed = parentA && parentB && money >= BREED_COST && !isBreeding;

    return (
        <div className="breeding-lab">
            <header className="pygame-panel breeding-header">
                <button className="pygame-btn" onClick={() => navigate('/menu')}>← Back</button>
                <h1 className="retro-text">Breeding Lab</h1>
                <div className="money-badge">${money.toLocaleString()}</div>
            </header>

            <main className="breeding-main">
                {/* Instructions */}
                <section className="breeding-info pygame-panel">
                    <p className="retro-text" style={{ fontSize: '0.55rem', color: 'var(--text-secondary)', margin: 0 }}>
                        Select 2 parents to create offspring. Parents are retired. Cost: ${BREED_COST}.
                    </p>
                    <p style={{ fontSize: '0.55rem', color: 'var(--accent-green-light)', margin: '0.5rem 0 0' }}>
                        Child inherits the BEST stat from each parent + a small mutation bonus.
                    </p>
                </section>

                {/* Parent Slots */}
                <section className="parent-slots">
                    <div className={`parent-slot pygame-panel ${parentA ? 'filled' : 'empty'}`}>
                        <h3 className="retro-text slot-label">Parent A</h3>
                        {pAData ? (
                            <div className="slot-content">
                                <strong>{pAData.name}</strong>
                                <div className="mini-stats">
                                    <span>SPD {pAData.speed.toFixed(1)}</span>
                                    <span>NRG {pAData.max_energy.toFixed(0)}</span>
                                    <span>RCV {pAData.recovery.toFixed(1)}</span>
                                </div>
                                <button className="pygame-btn clear-btn" onClick={() => setParentA(null)}>✕ Clear</button>
                            </div>
                        ) : (
                            <p className="slot-hint">Click a turtle below</p>
                        )}
                    </div>

                    <div className="breed-arrow">
                        <div className="arrow-icon">+</div>
                        {canBreed && (
                            <button className="pygame-btn breed-btn" onClick={handleBreed} disabled={!canBreed}>
                                {isBreeding ? '🧬 Breeding...' : '🧬 Breed!'}
                            </button>
                        )}
                    </div>

                    <div className={`parent-slot pygame-panel ${parentB ? 'filled' : 'empty'}`}>
                        <h3 className="retro-text slot-label">Parent B</h3>
                        {pBData ? (
                            <div className="slot-content">
                                <strong>{pBData.name}</strong>
                                <div className="mini-stats">
                                    <span>SPD {pBData.speed.toFixed(1)}</span>
                                    <span>NRG {pBData.max_energy.toFixed(0)}</span>
                                    <span>RCV {pBData.recovery.toFixed(1)}</span>
                                </div>
                                <button className="pygame-btn clear-btn" onClick={() => setParentB(null)}>✕ Clear</button>
                            </div>
                        ) : (
                            <p className="slot-hint">Click a turtle below</p>
                        )}
                    </div>
                </section>

                {/* Result */}
                {result && (
                    <section className="breed-result pygame-panel">
                        <h3 className="retro-text" style={{ fontSize: '0.7rem', color: 'var(--accent-gold)' }}>
                            New Turtle Born!
                        </h3>
                        <div className="result-turtle">
                            <strong>{result.name}</strong>
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.6rem' }}>Gen {result.generation}</span>
                            <div className="mini-stats">
                                <span>SPD {result.speed.toFixed(1)}</span>
                                <span>NRG {result.max_energy.toFixed(0)}</span>
                                <span>RCV {result.recovery.toFixed(1)}</span>
                                <span>SWM {result.swim.toFixed(1)}</span>
                                <span>CLB {result.climb.toFixed(1)}</span>
                            </div>
                        </div>
                        <button className="pygame-btn" onClick={() => setResult(null)}>Dismiss</button>
                    </section>
                )}

                {error && <div className="error-message pygame-panel">{error}</div>}

                {/* Turtle Picker */}
                <section className="turtle-picker">
                    <h3 className="retro-text section-title">Your Turtles</h3>
                    {activeTurtles.length === 0 ? (
                        <div className="empty-state pygame-panel">
                            <p>No active turtles! Visit the shop to buy more.</p>
                            <button className="pygame-btn" onClick={() => navigate('/shop')}>Visit Shop →</button>
                        </div>
                    ) : (
                        <div className="turtle-grid">
                            {activeTurtles.map(turtle => (
                                <TurtleCard
                                    key={turtle.id}
                                    turtle={turtle}
                                    isSelected={parentA === turtle.id || parentB === turtle.id}
                                    onSelect={() => handleSelect(turtle.id)}
                                />
                            ))}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}
