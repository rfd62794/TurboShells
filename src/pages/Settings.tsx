import { useNavigate } from 'react-router-dom'
import { useStore } from '../store'
import { supabase } from '../lib/supabase'

export default function Settings() {
  const nav = useNavigate()
  const { money, speedMult, setSpeed, history, turtles } = useStore()

  const changeSpeed = async (s: 1 | 2 | 4) => {
    setSpeed(s)
    await supabase.from('game_state').update({ race_speed: s }).eq('id', 'default')
  }

  const totalRaces = history.length
  const wins = history.filter(h => h.won_bet).length
  const totalWon = history.filter(h => h.won_bet).reduce((s, h) => s + h.bet_amount * 3, 0)
  const totalLost = history.filter(h => !h.won_bet && h.bet_amount > 0).reduce((s, h) => s + h.bet_amount, 0)

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => nav('/menu')}>← Back</button>
        <h1>⚙ Settings</h1>
        <span className="money">${money.toLocaleString()}</span>
      </div>

      <div className="content" style={{ maxWidth: 600 }}>
        {/* Race speed */}
        <div className="card">
          <p style={{ marginBottom: 10, fontSize: 9 }}>Race Speed</p>
          <div style={{ display: 'flex', gap: 8 }}>
            {([1, 2, 4] as const).map(s => (
              <button key={s} onClick={() => changeSpeed(s)} style={{
                borderColor: speedMult === s ? 'var(--green)' : undefined,
                color: speedMult === s ? 'var(--green)' : undefined,
              }}>
                {s}× {s === 1 ? 'Normal' : s === 2 ? 'Fast' : 'Ultra'}
              </button>
            ))}
          </div>
        </div>

        {/* Career stats */}
        <div className="card">
          <p style={{ marginBottom: 10, fontSize: 9 }}>Career Stats</p>
          {[
            ['Cash', `$${money.toLocaleString()}`, 'gold'],
            ['Active Turtles', turtles.filter(t => !t.is_retired).length, ''],
            ['Total Races', totalRaces, ''],
            ['Bets Won', wins, 'green'],
            ['Total Winnings', `+$${totalWon.toLocaleString()}`, 'green'],
            ['Total Losses', `-$${totalLost.toLocaleString()}`, 'red'],
          ].map(([k, v, c]) => (
            <div key={String(k)} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', borderBottom: '1px solid var(--border)' }}>
              <span className="label">{k}</span>
              <span style={{ fontSize: 9, color: c ? `var(--${c})` : 'var(--text)' }}>{v}</span>
            </div>
          ))}
        </div>

        {/* Race history */}
        <div className="card">
          <p style={{ marginBottom: 10, fontSize: 9 }}>Recent Races</p>
          {history.length === 0 ? <p className="empty">No races yet.</p> : (
            <div style={{ overflowX: 'auto' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1.5fr', gap: 4, marginBottom: 6, fontSize: 7, color: 'var(--muted)' }}>
                <span>Turtle</span><span>Rank</span><span>Bet</span><span>Result</span>
              </div>
              {history.slice(0, 15).map(h => (
                <div key={h.id} style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1.5fr', gap: 4, fontSize: 7, padding: '3px 0', borderTop: '1px solid var(--border)',
                  color: h.won_bet ? 'var(--green)' : h.bet_amount > 0 ? 'var(--red)' : 'var(--muted)' }}>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{h.turtle_name}</span>
                  <span>#{h.rank}</span>
                  <span>{h.bet_amount > 0 ? `$${h.bet_amount}` : '—'}</span>
                  <span>{h.won_bet ? `+$${h.bet_amount * 3}` : h.bet_amount > 0 ? `-$${h.bet_amount}` : '—'}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
