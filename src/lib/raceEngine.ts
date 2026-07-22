export type TerrainType = 'grass' | 'water' | 'rocks' | 'sand' | 'mud' | 'boost'

export interface TerrainSegment {
  start: number
  end: number
  type: TerrainType
}

export interface RaceTurtle {
  id: string
  name: string
  speed: number
  max_energy: number
  recovery: number
  swim: number
  climb: number
  stamina: number
  luck: number
  genome: string
  current_energy: number
  distance: number
  is_resting: boolean
  finished: boolean
  rank: number | null
  is_npc: boolean
}

export interface RaceSnapshot {
  tick: number
  elapsed_ms: number
  track_length: number
  turtles: RaceTurtle[]
  terrain: TerrainSegment[]
  finished: boolean
  winner_id: string | null
  finishers: string[]
}

function rng() { return Math.random() }

function generateTerrain(len: number): TerrainSegment[] {
  const types: TerrainType[] = ['grass','water','rocks','sand','mud','boost']
  const segs: TerrainSegment[] = [{ start: 0, end: len * 0.08, type: 'grass' }]
  let pos = len * 0.08
  while (pos < len * 0.95) {
    const t = types[Math.floor(rng() * types.length)]
    const segLen = len * (0.05 + rng() * 0.12)
    segs.push({ start: pos, end: Math.min(pos + segLen, len * 0.95), type: t })
    pos += segLen
  }
  segs.push({ start: pos, end: len, type: 'grass' })
  return segs
}

function terrainMult(type: TerrainType, t: RaceTurtle): number {
  switch (type) {
    case 'water': return (t.swim / 10) * 0.85
    case 'rocks': return (t.climb / 10) * 0.85
    case 'sand':  return 0.7
    case 'mud':   return (t.current_energy / t.max_energy) * 0.8
    case 'boost': return 1.5
    default:      return 1.0
  }
}

function getTerrainAt(dist: number, terrain: TerrainSegment[]): TerrainType {
  for (const s of terrain) if (dist >= s.start && dist < s.end) return s.type
  return 'grass'
}

const NPC_NAMES = ['Blaze','Rocket','Zoom','Flash','Dash','Swift','Bolt']

export function makeNpc(i: number): RaceTurtle {
  const s = 3 + rng() * 5
  return {
    id: `npc-${i}-${Date.now()}`,
    name: `NPC ${NPC_NAMES[i % NPC_NAMES.length]}`,
    speed: s, max_energy: 80 + rng() * 40, recovery: 0.7 + rng() * 0.6,
    swim: s + rng()*2, climb: s + rng()*2, stamina: s, luck: rng()*5,
    genome: `B${Math.floor(rng()*4)}-S${Math.floor(rng()*4)}-P${Math.floor(rng()*3)}-C${Math.floor(rng()*0xFFFFFF).toString(16).padStart(6,'0')}`,
    current_energy: 100 + rng()*40, distance: 0,
    is_resting: false, finished: false, rank: null, is_npc: true,
  }
}

export class RaceEngine {
  private turtles: RaceTurtle[]
  private terrain: TerrainSegment[]
  private trackLength: number
  private tick = 0
  private elapsed = 0
  private finishers: string[] = []
  private winner: string | null = null
  private done = false

  constructor(turtles: RaceTurtle[], trackLength = 1000) {
    this.trackLength = trackLength
    this.terrain = generateTerrain(trackLength)
    this.turtles = turtles.map(t => ({ ...t, current_energy: t.max_energy, distance: 0, finished: false, rank: null }))
  }

  step(dtMs: number, mult: 1|2|4 = 1): RaceSnapshot {
    if (this.done) return this.snap()
    const steps = mult
    const dt = dtMs / steps
    for (let s = 0; s < steps; s++) {
      this.tick++
      this.elapsed += dt
      for (const t of this.turtles) {
        if (t.finished) continue
        if (t.is_resting) {
          t.current_energy = Math.min(t.max_energy, t.current_energy + t.recovery * (dt / 16.67))
          if (t.current_energy >= t.max_energy * 0.5) t.is_resting = false
          continue
        }
        t.current_energy = Math.max(0, t.current_energy - 0.45 * (dt / 16.67))
        if (t.current_energy <= 0) { t.is_resting = true; continue }
        const terrain = getTerrainAt(t.distance, this.terrain)
        const luck = 1 + (t.luck / 100) * (rng() - 0.5) * 0.3
        t.distance += t.speed * terrainMult(terrain, t) * luck * (dt / 16.67) * 0.9
        if (t.distance >= this.trackLength) {
          t.distance = this.trackLength
          t.finished = true
          t.rank = this.finishers.length + 1
          this.finishers.push(t.id)
          if (!this.winner) this.winner = t.id
        }
      }
      if (this.turtles.every(t => t.finished)) { this.done = true; break }
    }
    return this.snap()
  }

  private snap(): RaceSnapshot {
    return {
      tick: this.tick, elapsed_ms: this.elapsed,
      track_length: this.trackLength,
      turtles: this.turtles.map(t => ({ ...t })),
      terrain: this.terrain, finished: this.done,
      winner_id: this.winner, finishers: [...this.finishers],
    }
  }
}
