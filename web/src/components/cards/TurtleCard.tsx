/**
 * Turtle Card Component
 * 
 * Replicates PyGame's TurtleCard with stats display.
 */

import type { RosterTurtle } from '../../types';
import './TurtleCard.css';

interface TurtleCardProps {
    turtle: RosterTurtle;
    isSelected?: boolean;
    isActiveRacer?: boolean;
    onSelect?: () => void;
    onSetRacer?: () => void;
}

export function TurtleCard({
    turtle,
    isSelected = false,
    isActiveRacer = false,
    onSelect,
    onSetRacer,
}: TurtleCardProps) {
    const winRate = turtle.total_races > 0
        ? ((turtle.total_wins / turtle.total_races) * 100).toFixed(0)
        : '--';

    return (
        <div
            className={`turtle-card pygame-panel ${isSelected ? 'selected' : ''} ${isActiveRacer ? 'active-racer' : ''}`}
            onClick={onSelect}
        >
            <header className="card-header">
                <h4 className="turtle-name">{turtle.name}</h4>
                {isActiveRacer && <span className="racer-badge">🏁</span>}
            </header>

            <div className="card-body">
                <div className="genome-preview" title={turtle.genome}>
                    🐢
                </div>

                <div className="stats-grid">
                    <div className="stat">
                        <span className="label">SPD</span>
                        <span className="value">{turtle.speed.toFixed(0)}</span>
                    </div>
                    <div className="stat">
                        <span className="label">NRG</span>
                        <span className="value">{turtle.max_energy.toFixed(0)}</span>
                    </div>
                    <div className="stat">
                        <span className="label">RCV</span>
                        <span className="value">{turtle.recovery.toFixed(1)}</span>
                    </div>
                </div>

                <div className="record">
                    <span>{turtle.total_wins}W / {turtle.total_races}R</span>
                    <span className="win-rate">{winRate}%</span>
                </div>
            </div>

            {onSetRacer && (
                <button
                    className={`pygame-btn set-racer-btn ${isActiveRacer ? 'active' : ''}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        onSetRacer();
                    }}
                >
                    {isActiveRacer ? 'Leave Race' : 'Join Race'}
                </button>
            )}
        </div>
    );
}
