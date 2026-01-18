/**
 * Shop Page (Placeholder)
 */

import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../stores';
import '../styles/retro.css';

export default function Shop() {
    const navigate = useNavigate();
    const { money } = useGameStore();

    return (
        <div className="shop-view">
            <header className="pygame-panel">
                <button className="pygame-btn" onClick={() => navigate('/menu')}>
                    ← Back
                </button>
                <h1 className="retro-text">🛒 Turtle Shop</h1>
                <div className="money-badge">${money.toLocaleString()}</div>
            </header>
            <main className="pygame-panel">
                <p className="coming-soon">Coming soon...</p>
                <p>Purchase new turtles to add to your roster.</p>
            </main>
        </div>
    );
}
