/**
 * Settings Page (Placeholder)
 */

import { useNavigate } from 'react-router-dom';
import '../styles/retro.css';

export default function Settings() {
    const navigate = useNavigate();

    return (
        <div className="settings-view">
            <header className="pygame-panel">
                <button className="pygame-btn" onClick={() => navigate('/menu')}>
                    ← Back
                </button>
                <h1 className="retro-text">⚙️ Settings</h1>
            </header>
            <main className="pygame-panel">
                <p className="coming-soon">Coming soon...</p>
                <p>Configure game options and preferences.</p>
            </main>
        </div>
    );
}
