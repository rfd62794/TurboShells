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

    const genColor = turtle.genome.match(/C([0-9a-fA-F]{6})/)?.[1] ?? '228B22';

    return (
        <div
            className={`turtle-card pygame-panel ${isSelected ? 'selected' : ''} ${isActiveRacer ? 'active-racer' : ''} ${turtle.is_retired ? 'retired' : ''}`}
            onClick={onSelect}
        >
            <header className="card-header">
                <h4 className="turtle-name">{turtle.name}</h4>
                {isActiveRacer && <span className="racer-badge">🏁</span>}
                {turtle.is_retired && <span className="retired-badge">RET</span>}
            </header>

            <div className="card-body">
                <div className="genome-preview" style={{ background: `#${genColor}22`, border: `2px solid #${genColor}` }}>
                    🐢
                </div>

                <div className="stats-grid">
                    <div className="stat">
                        <span className="label">SPD</span>
                        <span className="value">{turtle.speed.toFixed(1)}</span>
                    </div>
                    <div className="stat">
                        <span className="label">NRG</span>
                        <span className="value">{turtle.max_energy.toFixed(0)}</span>
                    </div>
                    <div className="stat">
                        <span className="label">RCV</span>
                        <span className="value">{turtle.recovery.toFixed(2)}</span>
                    </div>
                    <div className="stat">
                        <span className="label">SWM</span>
                        <span className="value">{turtle.swim.toFixed(1)}</span>
                    </div>
                    <div className="stat">
                        <span className="label">CLB</span>
                        <span className="value">{turtle.climb.toFixed(1)}</span>
                    </div>
                    {turtle.generation > 0 && (
                        <div className="stat">
                            <span className="label">GEN</span>
                            <span className="value gen-badge">{turtle.generation}</span>
                        </div>
                    )}
                </div>

                <div className="record">
                    <span>{turtle.total_wins}W / {turtle.total_races}R</span>
                    <span className="win-rate">{winRate}%</span>
                </div>
            </div>

            {onSetRacer && !turtle.is_retired && (
                <button
                    className={`pygame-btn set-racer-btn ${isActiveRacer ? 'active' : ''}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        onSetRacer();
                    }}
                >
                    {isActiveRacer ? '✓ Selected' : 'Race This'}
                </button>
            )}
        </div>
    );
}
