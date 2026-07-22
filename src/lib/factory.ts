import type { DbTurtle } from './supabase'
import { supabase } from './supabase'

const NAMES = ['Shellsworth','Turbo','Blaze','Pebbles','Rocky','Mossy','Speedy','Ironback','Swift','Drifter','Flint','Tide','Ember','Nova','Comet']

function rng(lo: number, hi: number) { return lo + Math.random() * (hi - lo) }

function randomGenome() {
  const c = Math.floor(Math.random()*0xFFFFFF).toString(16).padStart(6,'0')
  return `B${Math.floor(Math.random()*4)}-S${Math.floor(Math.random()*4)}-P${Math.floor(Math.random()*3)}-C${c}`
}

export function randomName() { return NAMES[Math.floor(Math.random()*NAMES.length)] }

export async function seedStarterTurtle(): Promise<DbTurtle | null> {
  const { data, error } = await supabase.from('turtles').insert({
    name: randomName(), speed: rng(3,6), max_energy: rng(80,120),
    recovery: rng(0.7,1.3), swim: rng(3,7), climb: rng(3,7),
    stamina: rng(3,7), luck: rng(2,6), genome: randomGenome(), generation: 0,
  }).select().single()
  if (error) { console.error(error); return null }
  return data as DbTurtle
}

type Tier = 'basic' | 'advanced' | 'champion'
const RANGES: Record<Tier,[number,number]> = { basic:[2,5], advanced:[4,7], champion:[6,10] }

export function previewTurtle(tier: Tier): Omit<DbTurtle,'id'|'created_at'|'total_races'|'total_wins'|'parent_a_id'|'parent_b_id'|'is_retired'> {
  const [lo,hi] = RANGES[tier]
  return {
    name: randomName(), speed: rng(lo,hi), max_energy: rng(60+lo*8,90+hi*8),
    recovery: rng(0.5+lo*0.05, 1.0+hi*0.05), swim: rng(lo,hi), climb: rng(lo,hi),
    stamina: rng(lo,hi), luck: rng(lo/2,hi/2), genome: randomGenome(), generation: 0,
  }
}

export async function buyTurtle(preview: ReturnType<typeof previewTurtle>): Promise<DbTurtle | null> {
  const { data, error } = await supabase.from('turtles').insert(preview).select().single()
  if (error) { console.error(error); return null }
  return data as DbTurtle
}

export function turtlePrice(t: ReturnType<typeof previewTurtle>): number {
  const avg = (t.speed + t.max_energy/10 + t.recovery*10 + t.swim + t.climb) / 5
  return Math.round(avg * 60 + 50)
}

export function breedChild(a: DbTurtle, b: DbTurtle) {
  const m = (va: number, vb: number) => Math.max(va,vb) + (Math.random()-0.4)*0.6
  return {
    name: randomName(),
    speed: m(a.speed,b.speed), max_energy: m(a.max_energy,b.max_energy),
    recovery: m(a.recovery,b.recovery), swim: m(a.swim,b.swim),
    climb: m(a.climb,b.climb), stamina: m(a.stamina,b.stamina), luck: m(a.luck,b.luck),
    genome: blendGenomes(a.genome,b.genome),
    generation: Math.max(a.generation,b.generation)+1,
    parent_a_id: a.id, parent_b_id: b.id,
  }
}

function blendGenomes(a: string, b: string) {
  const parse = (g: string) => {
    const p: Record<string,string> = {}
    g.split('-').forEach(s => { if(s) p[s[0]] = s.slice(1) })
    return p
  }
  const ga = parse(a), gb = parse(b)
  const pick = (k: string) => Math.random()<0.5 ? (ga[k]??gb[k]) : (gb[k]??ga[k])
  return `B${pick('B')}-S${pick('S')}-P${pick('P')}-C${pick('C')}`
}
