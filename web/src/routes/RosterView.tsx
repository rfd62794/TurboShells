/**
 * Roster View Page
 * 
 * Replicates PyGame's RosterPanel with turtle grid and betting controls.
 */

import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useGameStore } from '../stores';
import { TurtleCard } from '../components/cards/TurtleCard';
import '../styles/retro.css';

export default function RosterView() {
    const navigate = useNavigate();
    const {
        turtles,
        money,
        currentBet,
        selectedTurtleId,
        activeRacerId,
        showRetired,
        fetchRoster,
        selectTurtle,
        setActiveRacer,
        setBet,
        toggleShowRetired,
    } = useGameStore();

    useEffect(() => {
        fetchRoster();
    }, [fetchRoster]);

    const activeTurtles = turtles.filter(t =>
        showRetired || t.total_races === 0 || t.total_wins > 0
    );

    const handleSelectRacer = (turtleId: string) => {
        setActiveRacer(turtleId);
    };

    const handleStartRace = () => {
        if (activeRacerId) {
            navigate('/race');
        }
    };

    return (
        <div className="roster-view">
            <header className="roster-header pygame-panel">
                <button className="back-btn pygame-btn" onClick={() => navigate('/menu')}>
                    ← Back
                </button>
                <h1 className="retro-text">Turtle Roster</h1>
                <div className="money-badge">
                    <span>${money.toLocaleString()}</span>
                </div>
            </header>

            <main className="roster-content">
                {/* Betting Controls */}
                <section className="betting-controls pygame-panel">
                    <h3 className="retro-text">Race Setup</h3>
                    <div className="bet-slider">
                        <label>Bet Amount: ${currentBet}</label>
                        <input
                            type="range"
                            min={0}
                            max={Math.min(money, 500)}
                            step={10}
                            value={currentBet}
                            onChange={(e) => setBet(Number(e.target.value))}
                        />
                    </div>
                    <div className="active-racer">
                        {activeRacerId ? (
                            <span>Racing: {turtles.find(t => t.turtle_id === activeRacerId)?.name}</span>
                        ) : (
                            <span className="hint">Select a turtle to race</span>
                        )}
                    </div>
                    <button
                        className="pygame-btn start-btn"
                        onClick={handleStartRace}
                        disabled={!activeRacerId}
                    >
                        🏁 Start Race
                    </button>
                </section>

                {/* View Toggle */}
                <div className="view-toggle">
                    <label>
                        <input
                            type="checkbox"
                            checked={showRetired}
                            onChange={toggleShowRetired}
                        />
                        Show Retired Turtles
                    </label>
                </div>

                {/* Turtle Grid */}
                <section className="turtle-grid">
                    {activeTurtles.length === 0 ? (
                        <div className="empty-state pygame-panel">
                            <p>No turtles in roster!</p>
                            <button className="pygame-btn" onClick={() => navigate('/shop')}>
                                Visit Shop →
                            </button>
                        </div>
                    ) : (
                        activeTurtles.map(turtle => (
                            <TurtleCard
                                key={turtle.turtle_id}
                                turtle={turtle}
                                isSelected={selectedTurtleId === turtle.turtle_id}
                                isActiveRacer={activeRacerId === turtle.turtle_id}
                                onSelect={() => selectTurtle(turtle.turtle_id)}
                                onSetRacer={() => handleSelectRacer(turtle.turtle_id)}
                            />
                        ))
                    )}
                </section>
            </main>
        </div>
    );
}
