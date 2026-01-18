/**
 * Roster View Page
 * 
 * Replicates PyGame's RosterPanel with turtle grid and betting controls.
 */

import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useGameStore } from '../stores';
import { TurtleCard } from '../components/cards/TurtleCard';
import { BetSlider } from '../components/BetSlider';
import '../styles/retro.css';

export default function RosterView() {
    const navigate = useNavigate();
    const {
        turtles,
        money,
        currentBet,
        selectedTurtleId,
        selectedRacers,
        showRetired,
        fetchRoster,
        selectTurtle,
        toggleRacer,
        setBet,
        toggleShowRetired,
        startRace,
        isLoading,
        errorMessage,
    } = useGameStore();

    useEffect(() => {
        fetchRoster();
    }, [fetchRoster]);

    const activeTurtles = turtles.filter(t =>
        showRetired || t.total_races === 0 || t.total_wins > 0
    );

    const handleToggleRacer = (turtleId: string) => {
        toggleRacer(turtleId);
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

                    <div className="bet-slider-wrapper">
                        <BetSlider
                            currentBet={currentBet}
                            maxBet={500}
                            money={money}
                            onChange={setBet}
                        />
                    </div>

                    <div className="active-racers-list">
                        <div className="retro-label">Lineup ({selectedRacers.length}/4):</div>
                        {selectedRacers.length === 0 ? (
                            <span className="hint">Select turtles from roster</span>
                        ) : (
                            <ul className="racer-names">
                                {selectedRacers.map(id => {
                                    const turtle = turtles.find(t => t.turtle_id === id);
                                    return <li key={id}>🐢 {turtle?.name}</li>;
                                })}
                            </ul>
                        )}
                    </div>

                    <button
                        className="pygame-btn start-btn"
                        onClick={startRace}
                        disabled={selectedRacers.length === 0 || isLoading}
                    >
                        {isLoading ? 'Starting...' : '🏁 Start Race'}
                    </button>
                    {/* Error Display */}
                    {errorMessage && <div className="error-message blink">{errorMessage}</div>}
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
                                isActiveRacer={selectedRacers.includes(turtle.turtle_id)}
                                onSelect={() => selectTurtle(turtle.turtle_id)}
                                onSetRacer={() => handleToggleRacer(turtle.turtle_id)}
                            />
                        ))
                    )}
                </section>
            </main>
        </div>
    );
}
