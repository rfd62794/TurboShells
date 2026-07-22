import { useNavigate } from 'react-router-dom'
import { useStore } from '../store'

export default function Menu() {
  const { money, turtles, loading } = useStore()
  const nav = useNavigate()
  const active = turtles.filter(t => !t.is_retired).length

  return (
    <div className="page" style={{ justifyContent: 'center', alignItems: 'center', gap: 24 }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 8 }}>🐢</div>
        <h1 style={{ fontSize: 16, color: 'var(--green)', marginBottom: 4 }}>TurboShells</h1>
        <p className="label">Turtle Racing Manager</p>
      </div>

      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 24, padding: '10px 20px' }}>
        <span className="label">Cash</span>
        <span className="gold" style={{ fontSize: 13 }}>${money.toLocaleString()}</span>
        <span className="label">Turtles</span>
        <span className="green">{loading ? '…' : active}</span>
      </div>

      <nav style={{ display: 'flex', flexDirection: 'column', gap: 8, width: 240 }}>
        {[
          { path: '/roster', label: '🏠 Roster', hint: `${active} turtles` },
          { path: '/race',   label: '🏁 Race',   hint: 'Start racing' },
          { path: '/breeding', label: '🧬 Breed', hint: 'Create offspring' },
          { path: '/shop',   label: '🛒 Shop',   hint: 'Buy turtles' },
          { path: '/settings', label: '⚙ Settings', hint: 'Options & history' },
        ].map(({ path, label, hint }) => (
          <button key={path} onClick={() => nav(path)}
            style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px' }}>
            <span>{label}</span>
            <span className="label">{hint}</span>
          </button>
        ))}
      </nav>

      <p className="label">TurboShells v1.0 • Web Edition</p>
    </div>
  )
}
