/**
 * Race HUD Component
 * 
 * Overlay for race controls and status.
 * Replicates PyGame's RaceHUDPanel.
 */

import type { RaceSnapshot } from '../../types';
import './RaceHUD.css';

interface RaceHUDProps {
    snapshot: RaceSnapshot | null;
    bet: number;
    money: number;
    speedMultiplier: 1 | 2 | 4;
    onSpeedChange: (speed: 1 | 2 | 4) => void;
    onBack: () => void;
    connectionStatus: string;
}

export function RaceHUD({
    snapshot,
    bet,
    money,
    speedMultiplier,
    onSpeedChange,
    onBack,
    connectionStatus,
}: RaceHUDProps) {
    const isRacing = snapshot && !snapshot.finished;

    return (
        <div className="race-hud">
            {/* Top Bar */}
            <header className="hud-header pygame-panel">
                <button className="pygame-btn back-btn" onClick={onBack}>
                    ← Back
                </button>
                <div className="race-info retro-text">
                    <span>RACE</span>
                    {snapshot && (
                        <>
                            <span className="separator">|</span>
                            <span>Speed: {speedMultiplier}x</span>
                            <span className="separator">|</span>
                            <span>Bet: ${bet}</span>
                        </>
                    )}
                </div>
                <div className="money-badge">
                    ${money.toLocaleString()}
                </div>
            </header>

            {/* Speed Controls */}
            <div className="speed-controls pygame-panel">
                <button
                    className={`pygame-btn ${speedMultiplier === 1 ? 'active' : ''}`}
                    onClick={() => onSpeedChange(1)}
                    disabled={!isRacing}
                >
                    1x
                </button>
                <button
                    className={`pygame-btn ${speedMultiplier === 2 ? 'active' : ''}`}
                    onClick={() => onSpeedChange(2)}
                    disabled={!isRacing}
                >
                    2x
                </button>
                <button
                    className={`pygame-btn ${speedMultiplier === 4 ? 'active' : ''}`}
                    onClick={() => onSpeedChange(4)}
                    disabled={!isRacing}
                >
                    4x
                </button>
            </div>

            {/* Race Status */}
            {snapshot && (
                <div className="race-status">
                    <span className="tick">Tick: {snapshot.tick}</span>
                    <span className="time">{(snapshot.elapsed_ms / 1000).toFixed(1)}s</span>
                </div>
            )}

            {/* Winner Banner (Centered Overlay) */}
            {snapshot && snapshot.finished && snapshot.winner_id && (
                <div className="winner-banner retro-text">
                    🏆 Winner: {snapshot.turtles.find(t => t.id === snapshot.winner_id)?.name}
                </div>
            )}

            {/* Connection Status */}
            <div className={`connection-indicator ${connectionStatus}`}>
                <span className="dot" />
                <span>{connectionStatus}</span>
            </div>

            {/* Turtle Stamina Bars */}
            {snapshot && (
                <div className="stamina-bars">
                    {snapshot.turtles.map((turtle, i) => {
                        const energyPercent = (turtle.current_energy / turtle.max_energy) * 100;
                        return (
                            <div key={turtle.id} className="stamina-row">
                                <span className="turtle-name">{turtle.name}</span>
                                <div className="stamina-bar-container">
                                    <div
                                        className="stamina-bar-fill"
                                        style={{
                                            width: `${energyPercent}%`,
                                            backgroundColor: energyPercent > 50 ? '#22ff22' : energyPercent > 25 ? '#ffff22' : '#ff2222'
                                        }}
                                    />
                                </div>
                                <span className="position">#{i + 1}</span>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
