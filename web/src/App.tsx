/**
 * TurboShells Race Frontend
 * 
 * Main application component that connects to the WebSocket server
 * and renders the race stage.
 */

import { RaceStage } from './components';
import { useRaceSocket } from './hooks';
import './App.css';

function App() {
  const {
    status,
    snapshot,
    prevSnapshot,
    trackLength,
    error,
    startRace,
    stopRace,
  } = useRaceSocket({
    url: 'ws://localhost:8765/ws/race',
    autoReconnect: true,
    reconnectDelay: 3000,
  });

  return (
    <div className="app">
      <header className="app-header">
        <h1>🐢 TurboShells</h1>
        <div className="status">
          <span className={`status-indicator status-${status}`} />
          <span>{status}</span>
          {error && <span className="error">{error}</span>}
        </div>
      </header>

      <main className="race-container">
        <RaceStage
          snapshot={snapshot}
          prevSnapshot={prevSnapshot}
          trackLength={trackLength}
          width={800}
          height={400}
        />

        {snapshot && (
          <div className="race-info">
            <div className="tick">Tick: {snapshot.tick}</div>
            <div className="elapsed">
              Time: {(snapshot.elapsed_ms / 1000).toFixed(1)}s
            </div>
            {snapshot.finished && snapshot.winner_id && (
              <div className="winner">
                🏆 Winner:{' '}
                {snapshot.turtles.find((t) => t.id === snapshot.winner_id)?.name}
              </div>
            )}
          </div>
        )}

        <div className="standings">
          <h3>Standings</h3>
          <ol>
            {snapshot?.turtles
              .slice()
              .sort((a, b) => b.x - a.x)
              .map((turtle) => (
                <li key={turtle.id} className={turtle.finished ? 'finished' : ''}>
                  <span className="name">{turtle.name}</span>
                  <span className="distance">{Math.floor(turtle.x)}m</span>
                  <span className="energy">
                    ⚡ {Math.floor(turtle.current_energy)}
                  </span>
                  {turtle.is_resting && <span className="resting">💤</span>}
                  {turtle.finished && <span className="flag">🏁</span>}
                </li>
              ))}
          </ol>
        </div>
      </main>

      <footer className="controls">
        <button
          onClick={startRace}
          disabled={status !== 'connected' || (snapshot?.finished === false)}
        >
          🏁 Start Race
        </button>
        <button onClick={stopRace} disabled={status !== 'connected'}>
          ⏹️ Stop
        </button>
      </footer>
    </div>
  );
}

export default App;
