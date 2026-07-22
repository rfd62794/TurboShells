import { useNavigate } from 'react-router-dom';
import { useEffect, useRef, useCallback } from 'react';
import confetti from 'canvas-confetti';
import { useGameStore } from '../stores';
import { RaceEngine, generateNpcTurtle } from '../lib/raceEngine';
import type { RaceTurtle } from '../types';
import type { RosterTurtle } from '../types';
import { supabase } from '../lib/supabase';
import '../styles/retro.css';
import './RaceView.css';

const TRACK_LENGTH = 1200;

function TurtleRaceBar({ turtle, trackLength }: { turtle: RaceTurtle; trackLength: number }) {
    const pct = Math.min(100, (turtle.race_distance / trackLength) * 100);
    return (
        <div className={`race-turtle-row ${turtle.finished ? 'finished' : ''} ${turtle.is_npc ? 'npc' : 'player'}`}>
            <span className="race-name">{turtle.is_npc ? '🤖' : '🐢'} {turtle.name}</span>
            <div className="race-track">
                <div
                    className={`race-fill ${turtle.is_resting ? 'resting' : ''}`}
                    style={{
                        width: `${pct}%`,
                        background: turtle.finished ? '#ffd700' : (turtle.is_npc ? '#666' : '#228B22'),
                    }}
                />
                <span className="race-turtle-icon" style={{ left: `${pct}%` }}>
                    {turtle.finished ? '🏆' : turtle.is_resting ? '💤' : '🐢'}
                </span>
            </div>
            <div className="race-energy">
                <div
                    className="energy-fill"
                    style={{
                        width: `${Math.max(0, (turtle.current_energy / turtle.max_energy) * 100)}%`,
                        background: turtle.current_energy < turtle.max_energy * 0.3 ? '#ff4444' : '#33cc33',
                    }}
                />
            </div>
            {turtle.rank && <span className="rank-badge">#{turtle.rank}</span>}
        </div>
    );
}

export default function RaceView() {
    const navigate = useNavigate();
    const {
        turtles,
        selectedRacers,
        currentBet,
        raceSpeedMultiplier,
        money,
        raceSnapshot,
        raceStatus,
        setRaceSnapshot,
        setRaceStatus,
        setSpeedMultiplier,
        persistMoney,
        fetchRoster,
        fetchHistory,
    } = useGameStore();

    const engineRef = useRef<RaceEngine | null>(null);
    const rafRef = useRef<number>(0);
    const lastTimeRef = useRef<number>(0);
    const payoutDoneRef = useRef(false);

    const buildRacers = useCallback((): RaceTurtle[] => {
        const playerTurtles: RaceTurtle[] = turtles
            .filter(t => selectedRacers.includes(t.id))
            .map((t: RosterTurtle) => ({
                ...t,
                current_energy: t.max_energy,
                race_distance: 0,
                is_resting: false,
                finished: false,
                rank: null,
                is_npc: false,
            }));

        // Pad to 4 total with NPCs
        const npcCount = Math.max(0, 4 - playerTurtles.length);
        const npcs = Array.from({ length: npcCount }, (_, i) => generateNpcTurtle(i));
        return [...playerTurtles, ...npcs];
    }, [turtles, selectedRacers]);

    const startRace = useCallback(() => {
        payoutDoneRef.current = false;
        const racers = buildRacers();
        engineRef.current = new RaceEngine(racers, TRACK_LENGTH);
        lastTimeRef.current = performance.now();
        setRaceStatus('racing');

        const tick = (now: number) => {
            if (!engineRef.current) return;
            const dt = Math.min(now - lastTimeRef.current, 50);
            lastTimeRef.current = now;
            const snap = engineRef.current.step(dt, raceSpeedMultiplier);
            setRaceSnapshot(snap);
            if (!snap.finished) {
                rafRef.current = requestAnimationFrame(tick);
            } else {
                setRaceStatus('finished');
            }
        };
        rafRef.current = requestAnimationFrame(tick);
    }, [buildRacers, raceSpeedMultiplier, setRaceSnapshot, setRaceStatus]);

    // Auto-start when arriving on this page with racers selected
    useEffect(() => {
        if (raceStatus === 'idle' && selectedRacers.length > 0) {
            startRace();
        }
        return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // Payout + persist when race finishes
    useEffect(() => {
        if (raceStatus !== 'finished' || !raceSnapshot || payoutDoneRef.current) return;
        payoutDoneRef.current = true;

        const snap = raceSnapshot;
        const playerWon = snap.winner_id !== null && selectedRacers.includes(snap.winner_id);
        const winnings = playerWon && currentBet > 0 ? currentBet * 3 : 0;
        const newMoney = money + winnings - currentBet;

        persistMoney(newMoney);

        if (playerWon) {
            confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 }, colors: ['#FFD700', '#FFA500', '#228B22'] });
        }

        // Save results to Supabase
        const raceId = `race-${Date.now()}`;
        const results = snap.turtles
            .filter(t => !t.is_npc && t.rank !== null)
            .map(t => ({
                race_id: raceId,
                turtle_id: t.id,
                turtle_name: t.name,
                rank: t.rank ?? 99,
                final_distance: t.race_distance,
                final_time_ms: snap.elapsed_ms,
                bet_amount: selectedRacers.includes(t.id) ? currentBet : 0,
                won_bet: playerWon && t.id === snap.winner_id,
            }));

        (async () => {
            if (results.length > 0) {
                await supabase.from('race_results').insert(results);
            }
            // Update turtle stats
            for (const t of snap.turtles.filter(t => !t.is_npc)) {
                const isWin = t.rank === 1;
                await supabase
                    .from('turtles')
                    .update({
                        total_races: turtles.find(r => r.id === t.id)!.total_races + 1,
                        total_wins: turtles.find(r => r.id === t.id)!.total_wins + (isWin ? 1 : 0),
                    })
                    .eq('id', t.id);
            }
            await fetchRoster();
            await fetchHistory();
        })();
    }, [raceStatus, raceSnapshot, selectedRacers, currentBet, money, persistMoney, turtles, fetchRoster, fetchHistory]);

    const handleBack = () => {
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        setRaceStatus('idle');
        setRaceSnapshot(null);
        navigate('/roster');
    };

    const handleRestart = () => {
        if (rafRef.current) cancelAnimationFrame(rafRef.current);
        setRaceStatus('idle');
        setRaceSnapshot(null);
        setTimeout(() => startRace(), 50);
    };

    const snap = raceSnapshot;
    const playerTurtle = snap?.turtles.find(t => selectedRacers.includes(t.id));
    const winner = snap?.winner_id ? snap.turtles.find(t => t.id === snap.winner_id) : null;
    const playerWon = winner && selectedRacers.includes(winner.id);
    const winnings = playerWon && currentBet > 0 ? currentBet * 3 : 0;

    return (
        <div className="race-view">
            <header className="race-header pygame-panel">
                <button className="pygame-btn" onClick={handleBack}>← Back</button>
                <h1 className="retro-text">🏁 Race</h1>
                <div className="race-header-right">
                    <span className="money-badge">${money.toLocaleString()}</span>
                    {currentBet > 0 && <span className="bet-badge">Bet: ${currentBet}</span>}
                </div>
            </header>

            <main className="race-main">
                {/* Status Banner */}
                {raceStatus === 'finished' && snap && (
                    <div className={`result-banner pygame-panel ${playerWon ? 'win' : 'lose'}`}>
                        {playerWon ? (
                            <>
                                <span className="result-emoji">🏆</span>
                                <span className="result-text">{winner?.name} WINS!</span>
                                {winnings > 0 && <span className="payout">+${winnings.toLocaleString()}</span>}
                            </>
                        ) : (
                            <>
                                <span className="result-emoji">💔</span>
                                <span className="result-text">{winner?.name} wins</span>
                                {currentBet > 0 && <span className="payout loss">-${currentBet}</span>}
                            </>
                        )}
                    </div>
                )}

                {/* Race Track */}
                <section className="race-tracks pygame-panel">
                    {snap?.turtles.map(t => (
                        <TurtleRaceBar key={t.id} turtle={t} trackLength={TRACK_LENGTH} />
                    )) ?? (
                        <div className="race-loading">Starting race...</div>
                    )}
                </section>

                {/* Stats */}
                {snap && (
                    <div className="race-stats pygame-panel">
                        <span>Tick: {snap.tick}</span>
                        <span>Time: {(snap.elapsed_ms / 1000).toFixed(1)}s</span>
                        {playerTurtle && (
                            <span>Your turtle: {(playerTurtle.race_distance / TRACK_LENGTH * 100).toFixed(0)}%</span>
                        )}
                    </div>
                )}
            </main>

            <footer className="race-footer pygame-panel">
                <div className="speed-controls">
                    <span className="retro-text" style={{ fontSize: '0.5rem' }}>Speed:</span>
                    {([1, 2, 4] as const).map(s => (
                        <button
                            key={s}
                            className={`pygame-btn speed-btn ${raceSpeedMultiplier === s ? 'active' : ''}`}
                            onClick={() => setSpeedMultiplier(s)}
                        >
                            {s}x
                        </button>
                    ))}
                </div>

                {raceStatus === 'finished' ? (
                    <button className="pygame-btn primary-btn" onClick={handleRestart}>
                        🔄 Race Again
                    </button>
                ) : (
                    <button
                        className="pygame-btn"
                        disabled={raceStatus !== 'racing'}
                        onClick={() => { if (rafRef.current) cancelAnimationFrame(rafRef.current); setRaceStatus('finished'); }}
                    >
                        ⏩ Skip
                    </button>
                )}

                {raceStatus === 'finished' && (
                    <button className="pygame-btn" onClick={() => navigate('/menu')}>
                        Main Menu
                    </button>
                )}
            </footer>
        </div>
    );
}
