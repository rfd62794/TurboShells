import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import confetti from 'canvas-confetti'
import { useStore } from '../store'
import { RaceEngine, makeNpc } from '../lib/raceEngine'
import type { RaceSnapshot, RaceTurtle } from '../lib/raceEngine'
import { supabase } from '../lib/supabase'

const TRACK = 1000

function TurtleRow({ t, track }: { t: RaceTurtle; track: number }) {
  const pct = Math.min(100, (t.distance / track) * 100)
  const ePct = Math.max(0, (t.current_energy / t.max_energy) * 100)
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr 44px', gap: 8, alignItems: 'center', padding: '4px 0' }}>
      <span style={{ fontSize: 8, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        color: t.is_npc ? 'var(--muted)' : t.finished ? 'var(--gold)' : 'var(--green)' }}>
        {t.is_npc ? '🤖' : '🐢'} {t.name} {t.rank ? `#${t.rank}` : ''}
      </span>
      <div>
        <div style={{ height: 16, background: 'var(--bg)', border: '1px solid var(--border)', position: 'relative', overflow: 'visible' }}>
          <div style={{ width: `${pct}%`, height: '100%',
            background: t.finished ? 'var(--gold)' : t.is_npc ? '#444' : 'var(--green)',
            opacity: t.is_resting ? 0.5 : 1, transition: 'width 0.05s linear' }} />
          <span style={{ position: 'absolute', left: `${pct}%`, top: -2, transform: 'translateX(-50%)', fontSize: 13, transition: 'left 0.05s linear' }}>
            {t.finished ? '🏆' : t.is_resting ? '💤' : t.is_npc ? '🟤' : '🐢'}
          </span>
        </div>
        <div style={{ height: 4, background: 'var(--bg)', marginTop: 2 }}>
          <div style={{ width: `${ePct}%`, height: '100%', background: ePct < 30 ? 'var(--red)' : 'var(--green)', transition: 'width 0.1s' }} />
        </div>
      </div>
      <span style={{ fontSize: 8, color: 'var(--muted)', textAlign: 'right' }}>{(pct).toFixed(0)}%</span>
    </div>
  )
}

export default function Race() {
  const nav = useNavigate()
  const { turtles, racerIds, bet, money, speedMult, saveMoney, refetch, setSpeed } = useStore()
  const [snap, setSnap] = useState<RaceSnapshot | null>(null)
  const [status, setStatus] = useState<'racing'|'done'>('racing')
  const engineRef = useRef<RaceEngine | null>(null)
  const rafRef = useRef<number>(0)
  const lastRef = useRef<number>(0)
  const payoutDone = useRef(false)

  const start = useCallback(() => {
    payoutDone.current = false
    const players: RaceTurtle[] = turtles
      .filter(t => racerIds.includes(t.id))
      .map(t => ({ ...t, current_energy: t.max_energy, distance: 0, is_resting: false, finished: false, rank: null, is_npc: false }))
    const npcs = Array.from({ length: Math.max(0, 4 - players.length) }, (_, i) => makeNpc(i))
    engineRef.current = new RaceEngine([...players, ...npcs], TRACK)
    setStatus('racing')
    lastRef.current = performance.now()
    const tick = (now: number) => {
      const dt = Math.min(now - lastRef.current, 50)
      lastRef.current = now
      const s = engineRef.current!.step(dt, useStore.getState().speedMult)
      void 0
      setSnap({ ...s })
      if (!s.finished) { rafRef.current = requestAnimationFrame(tick) }
      else setStatus('done')
    }
    rafRef.current = requestAnimationFrame(tick)
  }, [turtles, racerIds])

  useEffect(() => {
    start()
    return () => cancelAnimationFrame(rafRef.current)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Payout once on finish
  useEffect(() => {
    if (status !== 'done' || !snap || payoutDone.current) return
    payoutDone.current = true
    const playerWon = !!snap.winner_id && racerIds.includes(snap.winner_id)
    const winnings = playerWon && bet > 0 ? bet * 3 : 0
    saveMoney(money + winnings - bet)
    if (playerWon) confetti({ particleCount: 120, spread: 70, origin: { y: 0.6 } })
    const raceId = `race-${Date.now()}`
    const results = snap.turtles.filter(t => !t.is_npc && t.rank !== null).map(t => ({
      race_id: raceId, turtle_id: t.id, turtle_name: t.name, rank: t.rank!,
      final_distance: t.distance, final_time_ms: snap.elapsed_ms,
      bet_amount: racerIds.includes(t.id) ? bet : 0,
      won_bet: playerWon && t.id === snap.winner_id,
    }));
    (async () => {
      if (results.length) await supabase.from('race_results').insert(results)
      for (const t of snap.turtles.filter(t => !t.is_npc)) {
        const orig = turtles.find(r => r.id === t.id)
        if (!orig) continue
        await supabase.from('turtles').update({
          total_races: orig.total_races + 1,
          total_wins: orig.total_wins + (t.rank === 1 ? 1 : 0),
        }).eq('id', t.id)
      }
      await refetch()
    })()
  }, [status, snap]) // eslint-disable-line react-hooks/exhaustive-deps

  const winner = snap?.winner_id ? snap.turtles.find(t => t.id === snap.winner_id) : null
  const playerWon = !!winner && racerIds.includes(winner.id)
  const curMoney = useStore(s => s.money)

  return (
    <div className="page">
      <div className="topbar">
        <button className="back" onClick={() => { cancelAnimationFrame(rafRef.current); nav('/roster') }}>← Back</button>
        <h1>🏁 Race</h1>
        <span className="money">${curMoney.toLocaleString()}</span>
      </div>

      <div className="content">
        {status === 'done' && snap && (
          <div className="card" style={{ borderColor: playerWon ? 'var(--gold)' : 'var(--border)', textAlign: 'center', padding: 12 }}>
            {playerWon
              ? <span className="gold">🏆 {winner?.name} WINS!{bet > 0 ? ` +$${bet * 3}` : ''}</span>
              : <span style={{ color: 'var(--muted)' }}>💔 {winner?.name || 'Someone'} wins. {bet > 0 ? `-$${bet}` : ''}</span>}
          </div>
        )}

        <div className="card" style={{ padding: '12px 16px' }}>
          {snap ? snap.turtles.map(t => <TurtleRow key={t.id} t={t} track={TRACK} />)
               : <p className="empty">Starting…</p>}
        </div>

        <div style={{ display: 'flex', gap: 8, alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <span className="label">Speed:</span>
            {([1, 2, 4] as const).map(n => (
              <button key={n} onClick={() => setSpeed(n)} style={{
                padding: '4px 8px', fontSize: 8,
                borderColor: speedMult === n ? 'var(--green)' : undefined,
                color: speedMult === n ? 'var(--green)' : undefined,
              }}>{n}×</button>
            ))}
          </div>
          {status === 'done' ? (
            <div style={{ display: 'flex', gap: 8 }}>
              <button onClick={() => { cancelAnimationFrame(rafRef.current); setSnap(null); start() }}>🔄 Again</button>
              <button onClick={() => nav('/menu')}>Menu</button>
            </div>
          ) : (
            <button onClick={() => { cancelAnimationFrame(rafRef.current); setStatus('done') }}>⏩ Skip</button>
          )}
        </div>
      </div>
    </div>
  )
}
