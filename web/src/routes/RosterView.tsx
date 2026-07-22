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
        isLoading,
        errorMessage,
    } = useGameStore();

    useEffect(() => { fetchRoster(); }, [fetchRoster]);

    const displayTurtles = showRetired ? turtles : turtles.filter(t => !t.is_retired);

    const handleStartRace = () => {
        if (selectedRacers.length === 0) return;
        navigate('/race');
    };

    return (
        <div className="roster-view">
            <header className="roster-header pygame-panel">
                <button className="back-btn pygame-btn" onClick={() => navigate('/menu')}>← Back</button>
                <h1 className="retro-text">Turtle Roster</h1>
                <div className="money-badge">${money.toLocaleString()}</div>
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
                        <div className="retro-label">Selected Racer:</div>
                        {selectedRacers.length === 0 ? (
                            <span className="hint">Select 1 turtle to race</span>
                        ) : (
                            <ul className="racer-names">
                                {selectedRacers.map(id => {
                                    const turtle = turtles.find(t => t.id === id);
                                    return <li key={id}>🐢 {turtle?.name}</li>;
                                })}
                            </ul>
                        )}
                    </div>

                    <button
                        className="pygame-btn start-btn"
                        onClick={handleStartRace}
                        disabled={selectedRacers.length === 0 || isLoading}
                    >
                        {isLoading ? 'Loading...' : '🏁 Start Race'}
                    </button>

                    {errorMessage && <div className="error-message blink">{errorMessage}</div>}
                </section>

                {/* View Toggle */}
                <div className="view-toggle">
                    <label>
                        <input type="checkbox" checked={showRetired} onChange={toggleShowRetired} />
                        {' '}Show Retired Turtles
                    </label>
                </div>

                {/* Turtle Grid */}
                <section className="turtle-grid">
                    {isLoading ? (
                        <div className="empty-state pygame-panel"><p>Loading roster...</p></div>
                    ) : displayTurtles.length === 0 ? (
                        <div className="empty-state pygame-panel">
                            <p>No turtles in roster!</p>
                            <button className="pygame-btn" onClick={() => navigate('/shop')}>Visit Shop →</button>
                        </div>
                    ) : (
                        displayTurtles.map(turtle => (
                            <TurtleCard
                                key={turtle.id}
                                turtle={turtle}
                                isSelected={selectedTurtleId === turtle.id}
                                isActiveRacer={selectedRacers.includes(turtle.id)}
                                onSelect={() => selectTurtle(turtle.id)}
                                onSetRacer={() => toggleRacer(turtle.id)}
                            />
                        ))
                    )}
                </section>
            </main>
        </div>
    );
}
