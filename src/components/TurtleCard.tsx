import type { DbTurtle } from '../lib/supabase'

interface Props {
  turtle: DbTurtle
  selected?: boolean
  onSelect?: () => void
  onRace?: () => void
}

export default function TurtleCard({ turtle, selected, onSelect, onRace }: Props) {
  const wr = turtle.total_races > 0 ? ((turtle.total_wins / turtle.total_races) * 100).toFixed(0) : '—'
  const genColor = turtle.genome.match(/C([0-9a-fA-F]{6})/)?.[1] ?? '22c55e'

  return (
    <div onClick={onSelect} style={{
      width: 160, background: 'var(--bg-card)', border: `2px solid ${selected ? 'var(--gold)' : 'var(--border)'}`,
      padding: 12, cursor: onSelect ? 'pointer' : 'default',
      boxShadow: selected ? '0 0 8px rgba(234,179,8,0.3)' : 'none',
      transition: 'border-color 0.1s, box-shadow 0.1s',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 9, color: 'var(--gold)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 110 }}>
          {turtle.name}
        </span>
        {turtle.generation > 0 && <span style={{ fontSize: 7, color: 'var(--green)' }}>G{turtle.generation}</span>}
      </div>

      <div style={{ fontSize: 28, textAlign: 'center', padding: '6px 0',
        background: `#${genColor}18`, border: `1px solid #${genColor}44`, marginBottom: 8 }}>
        🐢
      </div>

      {[
        ['SPD', turtle.speed, 10],
        ['NRG', turtle.max_energy / 15, 10],
        ['SWM', turtle.swim, 10],
        ['CLB', turtle.climb, 10],
      ].map(([label, val, max]) => (
        <div key={String(label)} style={{ display: 'grid', gridTemplateColumns: '30px 1fr', gap: 4, alignItems: 'center', marginBottom: 3 }}>
          <span style={{ fontSize: 7, color: 'var(--muted)' }}>{label}</span>
          <div style={{ height: 5, background: 'var(--bg)', border: '1px solid var(--border)' }}>
            <div style={{ width: `${Math.min(100, (Number(val) / Number(max)) * 100)}%`, height: '100%',
              background: Number(val)/Number(max) > 0.7 ? 'var(--gold)' : Number(val)/Number(max) > 0.4 ? 'var(--green)' : '#555' }} />
          </div>
        </div>
      ))}

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, fontSize: 7, color: 'var(--muted)' }}>
        <span>{turtle.total_wins}W/{turtle.total_races}R</span>
        <span style={{ color: 'var(--gold)' }}>{wr}%</span>
      </div>

      {onRace && (
        <button onClick={e => { e.stopPropagation(); onRace() }}
          style={{ width: '100%', marginTop: 8, fontSize: 7, padding: '4px',
            borderColor: selected ? 'var(--green)' : undefined, color: selected ? 'var(--green)' : undefined }}>
          {selected ? '✓ Selected' : 'Select'}
        </button>
      )}
    </div>
  )
}
