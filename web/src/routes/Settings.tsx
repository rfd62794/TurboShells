import { useNavigate } from 'react-router-dom';
import { useGameStore } from '../stores';
import { supabase } from '../lib/supabase';
import '../styles/retro.css';
import './Settings.css';

export default function Settings() {
    const navigate = useNavigate();
    const { raceSpeedMultiplier, setSpeedMultiplier, money, raceHistory, turtles } = useGameStore();

    const handleSpeedChange = async (speed: 1 | 2 | 4) => {
        setSpeedMultiplier(speed);
        await supabase
            .from('game_state')
            .update({ race_speed: speed, updated_at: new Date().toISOString() })
            .eq('id', 'default');
    };

    const totalRaces = raceHistory.length;
    const wins = raceHistory.filter(r => r.won_bet).length;
    const totalWinnings = raceHistory.filter(r => r.won_bet).reduce((s, r) => s + r.bet_amount * 3, 0);
    const totalLosses = raceHistory.filter(r => !r.won_bet && r.bet_amount > 0).reduce((s, r) => s + r.bet_amount, 0);
    const activeTurtles = turtles.filter(t => !t.is_retired).length;

    return (
        <div className="settings-view">
            <header className="settings-header pygame-panel">
                <button className="pygame-btn" onClick={() => navigate('/menu')}>← Back</button>
                <h1 className="retro-text">Settings</h1>
                <div className="money-badge">${money.toLocaleString()}</div>
            </header>

            <main className="settings-main">
                {/* Race Speed */}
                <section className="settings-section pygame-panel">
                    <h2 className="retro-text section-title">Race Speed</h2>
                    <p className="section-desc">Controls how fast the race simulation runs.</p>
                    <div className="speed-options">
                        {([1, 2, 4] as const).map(s => (
                            <button
                                key={s}
                                className={`pygame-btn speed-opt ${raceSpeedMultiplier === s ? 'active' : ''}`}
                                onClick={() => handleSpeedChange(s)}
                            >
                                {s}x {s === 1 ? 'Normal' : s === 2 ? 'Fast' : 'Ultra'}
                            </button>
                        ))}
                    </div>
                </section>

                {/* Career Stats */}
                <section className="settings-section pygame-panel">
                    <h2 className="retro-text section-title">Career Stats</h2>
                    <div className="stats-list">
                        <div className="stats-row">
                            <span className="stat-key">Cash on Hand</span>
                            <span className="stat-val gold">${money.toLocaleString()}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stat-key">Active Turtles</span>
                            <span className="stat-val">{activeTurtles}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stat-key">Total Races</span>
                            <span className="stat-val">{totalRaces}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stat-key">Bets Won</span>
                            <span className="stat-val green">{wins}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stat-key">Total Winnings</span>
                            <span className="stat-val green">+${totalWinnings.toLocaleString()}</span>
                        </div>
                        <div className="stats-row">
                            <span className="stat-key">Total Losses</span>
                            <span className="stat-val red">-${totalLosses.toLocaleString()}</span>
                        </div>
                    </div>
                </section>

                {/* Race History */}
                <section className="settings-section pygame-panel">
                    <h2 className="retro-text section-title">Race History</h2>
                    {raceHistory.length === 0 ? (
                        <p className="section-desc">No races yet. Hit the track!</p>
                    ) : (
                        <div className="history-table">
                            <div className="history-header">
                                <span>Turtle</span>
                                <span>Rank</span>
                                <span>Bet</span>
                                <span>Result</span>
                                <span>Date</span>
                            </div>
                            {raceHistory.slice(0, 15).map(entry => (
                                <div key={entry.id} className={`history-row ${entry.won_bet ? 'win' : entry.bet_amount > 0 ? 'lose' : ''}`}>
                                    <span>{entry.turtle_name}</span>
                                    <span>#{entry.rank}</span>
                                    <span>{entry.bet_amount > 0 ? `$${entry.bet_amount}` : '—'}</span>
                                    <span>{entry.won_bet ? `+$${entry.bet_amount * 3}` : entry.bet_amount > 0 ? `-$${entry.bet_amount}` : '—'}</span>
                                    <span>{new Date(entry.raced_at).toLocaleDateString()}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
}
