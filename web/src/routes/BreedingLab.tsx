/**
 * Breeding Lab Page (Placeholder)
 */

import { useNavigate } from 'react-router-dom';
import '../styles/retro.css';

export default function BreedingLab() {
    const navigate = useNavigate();

    return (
        <div className="breeding-lab">
            <header className="pygame-panel">
                <button className="pygame-btn" onClick={() => navigate('/menu')}>
                    ← Back
                </button>
                <h1 className="retro-text">🧬 Breeding Lab</h1>
            </header>
            <main className="pygame-panel">
                <p className="coming-soon">Coming soon...</p>
                <p>Select two parent turtles to create offspring with combined genetics.</p>
            </main>
        </div>
    );
}
