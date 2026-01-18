/**
 * Race View Page
 * 
 * Contains the RaceStage (PixiJS) and RaceHUD overlay.
 */

import { useNavigate } from 'react-router-dom';
import { RaceStage } from '../components';
import { RaceHUD } from '../components/hud/RaceHUD';
import { useRaceSocket } from '../hooks';
import { useGameStore } from '../stores';
import '../styles/retro.css';

export default function RaceView() {
    const navigate = useNavigate();
    const { money, currentBet, raceSpeedMultiplier, setSpeedMultiplier } = useGameStore();

    const {
        status,
        snapshot,
        snapshotBuffer,
        trackLength,
        error,
        startRace,
        stopRace,
        setSpeed,
    } = useRaceSocket({
        url: 'ws://localhost:8765/ws/race',
        autoReconnect: true,
    });

    const handleBack = () => {
        stopRace();
        navigate('/roster');
    };

    // Wrapper that updates both local state and sends to server
    const handleSpeedChange = (speed: 1 | 2 | 4) => {
        setSpeedMultiplier(speed);  // Update local Zustand state
        setSpeed(speed);             // Send to server via WebSocket
    };

    return (
        <div className="race-view">
            {/* Race HUD Overlay */}
            <RaceHUD
                snapshot={snapshot}
                bet={currentBet}
                money={money}
                speedMultiplier={raceSpeedMultiplier}
                onSpeedChange={handleSpeedChange}
                onBack={handleBack}
                connectionStatus={status}
            />

            {/* PixiJS Race Stage */}
            <main className="race-stage-container">
                <RaceStage
                    snapshotBuffer={snapshotBuffer}
                    trackLength={trackLength}
                    width={800}
                    height={400}
                />
            </main>

            {/* Race Controls */}
            <footer className="race-controls pygame-panel">
                <button
                    className="pygame-btn"
                    onClick={startRace}
                    disabled={status !== 'connected' || snapshot?.finished === false}
                >
                    🏁 Start Race
                </button>
                <button
                    className="pygame-btn"
                    onClick={stopRace}
                    disabled={status !== 'connected'}
                >
                    ⏹️ Stop
                </button>
                {error && <span className="error">{error}</span>}
            </footer>
        </div>
    );
}
