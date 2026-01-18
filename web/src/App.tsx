/**
 * TurboShells Race Frontend
 * 
 * Main application component that connects to the WebSocket server
 * and renders the race stage. Loads saved roster from database on mount.
 */

import { RaceStage } from './components';
import { useRaceSocket, useRoster } from './hooks';
import './App.css';

function App() {
  // Fetch saved roster from database
  const { turtles: savedTurtles, history, loading, refresh } = useRoster();

  // WebSocket connection for live racing
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

        {/* Saved Roster Panel */}
        <div className="roster-panel">
          <h3>
            🗄️ Saved Roster
            <button onClick={refresh} className="refresh-btn" title="Refresh">
              🔄
            </button>
          </h3>
          {loading ? (
            <div className="loading">Loading...</div>
          ) : savedTurtles.length === 0 ? (
            <div className="empty">No turtles saved yet. Complete a race!</div>
          ) : (
            <ul className="roster-list">
              {savedTurtles.map((turtle) => (
                <li key={turtle.turtle_id}>
                  <span className="name">{turtle.name}</span>
                  <span className="stats">
                    🏃 {turtle.speed.toFixed(0)} | ⚡ {turtle.max_energy.toFixed(0)}
                  </span>
                  <span className="record">
                    {turtle.total_wins}/{turtle.total_races} wins
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Live Standings */}
        <div className="standings">
          <h3>Live Standings</h3>
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

        {/* Race History */}
        {history.length > 0 && (
          <div className="history-panel">
            <h3>📊 Recent History</h3>
            <ul>
              {history.slice(0, 5).map((entry) => (
                <li key={entry.id}>
                  <span className="rank">#{entry.rank}</span>
                  <span className="name">{entry.turtle_name}</span>
                  <span className="time">
                    {(entry.final_time_ms / 1000).toFixed(1)}s
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}
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
