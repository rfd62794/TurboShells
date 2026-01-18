/**
 * Main Menu Page
 * 
 * Replicates PyGame's MainMenuPanel with navigation buttons and money display.
 */

import { useNavigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useGameStore } from '../stores';
import '../styles/retro.css';

export default function MainMenu() {
    const navigate = useNavigate();
    const { money, fetchRoster, turtles } = useGameStore();

    // Fetch roster on mount
    useEffect(() => {
        fetchRoster();
    }, [fetchRoster]);

    return (
        <div className="main-menu">
            <header className="menu-header">
                <h1 className="title retro-text">🐢 TurboShells</h1>
                <div className="money-badge pygame-panel">
                    <span className="label">Cash</span>
                    <span className="amount">${money.toLocaleString()}</span>
                </div>
            </header>

            <main className="menu-content">
                <div className="pygame-panel menu-panel">
                    <h2 className="retro-text">Main Menu</h2>

                    <nav className="menu-buttons">
                        <button
                            className="menu-btn pygame-btn"
                            onClick={() => navigate('/roster')}
                        >
                            🏠 Roster
                            <span className="hint">{turtles.length} turtles</span>
                        </button>

                        <button
                            className="menu-btn pygame-btn"
                            onClick={() => navigate('/race')}
                        >
                            🏁 Race
                            <span className="hint">Start racing</span>
                        </button>

                        <button
                            className="menu-btn pygame-btn"
                            onClick={() => navigate('/breeding')}
                        >
                            🧬 Breeding Lab
                            <span className="hint">Create offspring</span>
                        </button>

                        <button
                            className="menu-btn pygame-btn"
                            onClick={() => navigate('/shop')}
                        >
                            🛒 Shop
                            <span className="hint">Buy turtles</span>
                        </button>

                        <button
                            className="menu-btn pygame-btn"
                            onClick={() => navigate('/settings')}
                        >
                            ⚙️ Settings
                            <span className="hint">Game options</span>
                        </button>
                    </nav>
                </div>
            </main>

            <footer className="menu-footer retro-text">
                <span>TurboShells v1.0</span>
                <span>•</span>
                <span>Web Edition</span>
            </footer>
        </div>
    );
}
