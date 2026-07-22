import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useStore } from '../store'
import { previewTurtle, turtlePrice, buyTurtle } from '../lib/factory'
import type { DbTurtle } from '../lib/supabase'

type Tier = 'basic' | 'advanced' | 'champion'

interface Listing { turtle: ReturnType<typeof previewTurtle>; price: number; tier: Tier }

const TIER_COLORS: Record<Tier, string> = { basic: '#888', advanced: 'var(--green)', champion: 'var(--gold)' }

function StatRow({ label, val, max }: { label: string; val: number; max: number }) {
  const pct = Math.min(100, (val / max) * 100)
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '50px 1fr 36px', gap: 4, alignItems: 'center', marginBottom: 3 }}>
      <span className="label">{label}</span>
      <div className="stat-bar-wrap"><div className="stat-bar-fill" style={{ width: `${pct}%`, background: pct > 70 ? 'var(--gold)' : pct > 40 ? 'var(--green)' : '#555' }} /></div>
      <span style={{ fontSize: 7, textAlign: 'right', color: 'var(--muted)' }}>{val.toFixed(1)}</span>
    </div>
  )
}

export default function Shop() {
  const nav = useNavigate()
  const { money, saveMoney, refetch } = useStore()
  const [listings, setListings] = useState<Listing[]>([])
  const [bought, setBought] = useState('')
  const [err, setErr] = useState('')

  const refresh = () => {
    const tiers: Tier[] = ['basic','basic','advanced','advanced','champion']
    setListings(tiers.map(tier => {
      const turtle = previewTurtle(tier)
      return { turtle, price: turtlePrice(turtle), tier }
    }))
  }

  useEffect(() => { refresh() }, [])

  const buy = async (l: Listing, idx: number) => {
    if (money < l.price) { setErr('Not enough money!'); return }
    setErr('')
    const data = await buyTurtle(l.turtle)
    if (!data) { setErr('Purchase failed'); return }
    await saveMoney(money - l.price)
    await refetch()
    setBought(data.name)
    setListings(prev => prev.filter((_, i) => i !== idx))
    setTimeout(() => setBought(''), 3000)
  }

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => nav('/menu')}>← Back</button>
        <h1>🛒 Shop</h1>
        <span className="money">${money.toLocaleString()}</span>
      </div>

      <div className="content">
        {bought && <div className="card" style={{ borderColor: 'var(--green)', textAlign: 'center', padding: 8 }}>
          <span className="green">🐢 {bought} added to roster!</span>
        </div>}
        {err && <p style={{ color: 'var(--red)', fontSize: 8 }}>{err}</p>}

        <button onClick={refresh} style={{ alignSelf: 'flex-start', fontSize: 8 }}>🔄 Refresh stock</button>

        <div className="grid">
          {listings.map((l, i) => (
            <div key={i} className="card" style={{ width: 200, display: 'flex', flexDirection: 'column', gap: 8 }}>
              <span style={{ fontSize: 7, color: TIER_COLORS[l.tier], textTransform: 'uppercase' }}>{l.tier}</span>
              <p style={{ color: 'var(--gold)', fontSize: 10 }}>{l.turtle.name}</p>
              <div>
                <StatRow label="Speed" val={l.turtle.speed} max={10} />
                <StatRow label="Energy" val={l.turtle.max_energy / 15} max={10} />
                <StatRow label="Recovery" val={l.turtle.recovery * 5} max={10} />
                <StatRow label="Swim" val={l.turtle.swim} max={10} />
                <StatRow label="Climb" val={l.turtle.climb} max={10} />
              </div>
              <button className={money >= l.price ? 'primary' : ''} style={{ marginTop: 'auto' }}
                disabled={money < l.price} onClick={() => buy(l, i)}>
                Buy — ${l.price}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
