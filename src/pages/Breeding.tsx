import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store'
import { supabase } from '../lib/supabase'
import { breedChild } from '../lib/factory'
import type { DbTurtle } from '../lib/supabase'
import TurtleCard from '../components/TurtleCard'

const COST = 200

export default function Breeding() {
  const nav = useNavigate()
  const { turtles, money, saveMoney, refetch } = useStore()
  const [selA, setSelA] = useState<string | null>(null)
  const [selB, setSelB] = useState<string | null>(null)
  const [result, setResult] = useState<DbTurtle | null>(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')

  const active = turtles.filter(t => !t.is_retired)

  const pick = (id: string) => {
    if (selA === id) { setSelA(null); return }
    if (selB === id) { setSelB(null); return }
    if (!selA) { setSelA(id); return }
    if (!selB) { setSelB(id); return }
    setSelA(id); setSelB(null)
  }

  const breed = async () => {
    if (!selA || !selB || money < COST) return
    setBusy(true); setErr('')
    const pA = turtles.find(t => t.id === selA)!
    const pB = turtles.find(t => t.id === selB)!
    const child = breedChild(pA, pB)
    const { data, error } = await supabase.from('turtles').insert(child).select().single()
    if (error) { setErr(error.message); setBusy(false); return }
    await supabase.from('turtles').update({ is_retired: true }).in('id', [selA, selB])
    await saveMoney(money - COST)
    await refetch()
    setResult(data as DbTurtle)
    setSelA(null); setSelB(null)
    setBusy(false)
  }

  const pAData = turtles.find(t => t.id === selA)
  const pBData = turtles.find(t => t.id === selB)

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => nav('/menu')}>← Back</button>
        <h1>🧬 Breeding Lab</h1>
        <span className="money">${money.toLocaleString()}</span>
      </div>

      <div className="content">
        <p className="label" style={{ textAlign: 'center' }}>
          Select 2 parents → breed a stronger child. Parents retire. Cost: ${COST}
        </p>

        {/* Parent slots */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 12, alignItems: 'center' }}>
          <SlotBox label="Parent A" turtle={pAData} onClear={() => setSelA(null)} />
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 18, color: 'var(--muted)' }}>+</span>
            <button className="primary" disabled={!selA || !selB || money < COST || busy} onClick={breed}>
              {busy ? '…' : '🧬 Breed!'}
            </button>
          </div>
          <SlotBox label="Parent B" turtle={pBData} onClear={() => setSelB(null)} />
        </div>

        {err && <p style={{ color: 'var(--red)', fontSize: 8 }}>{err}</p>}

        {result && (
          <div className="card" style={{ borderColor: 'var(--gold)' }}>
            <p className="gold" style={{ marginBottom: 8, fontSize: 9 }}>🐣 New turtle born!</p>
            <p style={{ marginBottom: 4 }}>{result.name} <span className="label">(Gen {result.generation})</span></p>
            <StatLine label="Speed" val={result.speed} />
            <StatLine label="Energy" val={result.max_energy / 15} />
            <StatLine label="Swim" val={result.swim} />
            <StatLine label="Climb" val={result.climb} />
            <button style={{ marginTop: 8, fontSize: 8 }} onClick={() => setResult(null)}>Dismiss</button>
          </div>
        )}

        {active.length === 0
          ? <div className="empty card"><p>No turtles! <button style={{ display: 'inline' }} onClick={() => nav('/shop')}>Shop →</button></p></div>
          : <div className="grid">{active.map(t => (
              <TurtleCard key={t.id} turtle={t}
                selected={selA === t.id || selB === t.id}
                onSelect={() => pick(t.id)} />
            ))}</div>}
      </div>
    </div>
  )
}

function SlotBox({ label, turtle, onClear }: { label: string; turtle?: DbTurtle; onClear: () => void }) {
  return (
    <div className="card" style={{ minHeight: 80, borderStyle: turtle ? 'solid' : 'dashed', borderColor: turtle ? 'var(--green)' : undefined }}>
      <p className="label" style={{ marginBottom: 6 }}>{label}</p>
      {turtle ? (
        <>
          <p style={{ color: 'var(--gold)', fontSize: 9, marginBottom: 4 }}>{turtle.name}</p>
          <p className="label">SPD {turtle.speed.toFixed(1)} | NRG {turtle.max_energy.toFixed(0)}</p>
          <button style={{ marginTop: 6, fontSize: 7, padding: '3px 6px' }} onClick={onClear}>✕ Clear</button>
        </>
      ) : <p className="label" style={{ marginTop: 8 }}>Click a turtle</p>}
    </div>
  )
}

function StatLine({ label, val }: { label: string; val: number }) {
  const pct = Math.min(100, (val / 10) * 100)
  return (
    <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 4 }}>
      <span className="label" style={{ width: 50 }}>{label}</span>
      <div className="stat-bar-wrap" style={{ flex: 1 }}>
        <div className="stat-bar-fill" style={{ width: `${pct}%`, background: pct > 70 ? 'var(--gold)' : pct > 40 ? 'var(--green)' : '#666' }} />
      </div>
    </div>
  )
}
