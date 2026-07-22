import { useNavigate } from 'react-router-dom'
import { useStore } from '../store'
import TurtleCard from '../components/TurtleCard'

export default function Roster() {
  const nav = useNavigate()
  const { turtles, money, racerIds, bet, loading, setRacers, setBet } = useStore()
  const active = turtles.filter(t => !t.is_retired)

  const toggle = (id: string) => {
    setRacers(racerIds.includes(id) ? [] : [id])
  }

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => nav('/menu')}>← Back</button>
        <h1>Roster</h1>
        <span className="money">${money.toLocaleString()}</span>
      </div>

      <div className="content">
        {/* Race setup bar */}
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 16, flexWrap: 'wrap' }}>
          <span className="label">Racer:</span>
          {racerIds.length > 0
            ? <span className="green">{turtles.find(t=>t.id===racerIds[0])?.name}</span>
            : <span className="muted" style={{ color:'var(--muted)' }}>— select one —</span>}
          <span className="label" style={{ marginLeft: 'auto' }}>Bet: <span className="gold">${bet}</span></span>
          <input type="range" min={0} max={Math.min(500, money)} step={10} value={bet}
            onChange={e => setBet(Number(e.target.value))}
            style={{ accentColor: 'var(--green)', width: 120 }} />
          <button className="primary" disabled={racerIds.length === 0 || loading}
            onClick={() => nav('/race')}>
            🏁 Race
          </button>
        </div>

        {loading ? (
          <p className="empty">Loading…</p>
        ) : active.length === 0 ? (
          <div className="empty card">
            <p style={{ marginBottom: 12 }}>No turtles yet!</p>
            <button onClick={() => nav('/shop')}>Visit Shop →</button>
          </div>
        ) : (
          <div className="grid">
            {active.map(t => (
              <TurtleCard key={t.id} turtle={t}
                selected={racerIds.includes(t.id)}
                onSelect={() => toggle(t.id)} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
