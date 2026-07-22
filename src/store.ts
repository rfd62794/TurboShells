import { create } from 'zustand'
import { supabase } from './lib/supabase'
import { seedStarterTurtle } from './lib/factory'
import type { DbTurtle, DbRaceResult } from './lib/supabase'

interface Store {
  money: number
  turtles: DbTurtle[]
  history: DbRaceResult[]
  racerIds: string[]
  bet: number
  speedMult: 1|2|4
  loading: boolean

  init: () => Promise<void>
  refetch: () => Promise<void>
  saveMoney: (n: number) => Promise<void>
  setRacers: (ids: string[]) => void
  setBet: (n: number) => void
  setSpeed: (s: 1|2|4) => void
}

export const useStore = create<Store>((set, get) => ({
  money: 1000,
  turtles: [],
  history: [],
  racerIds: [],
  bet: 0,
  speedMult: 1,
  loading: true,

  init: async () => {
    set({ loading: true })
    const [{ data: gs }, { data: turtles }, { data: hist }] = await Promise.all([
      supabase.from('game_state').select('*').eq('id','default').maybeSingle(),
      supabase.from('turtles').select('*').order('created_at'),
      supabase.from('race_results').select('*').order('raced_at',{ascending:false}).limit(30),
    ])
    let roster = (turtles ?? []) as DbTurtle[]
    if (roster.length === 0) {
      const starter = await seedStarterTurtle()
      if (starter) roster = [starter]
    }
    set({
      money: gs?.money ?? 1000,
      speedMult: (gs?.race_speed ?? 1) as 1|2|4,
      turtles: roster,
      history: (hist ?? []) as DbRaceResult[],
      loading: false,
    })
  },

  refetch: async () => {
    const [{ data: turtles }, { data: hist }] = await Promise.all([
      supabase.from('turtles').select('*').order('created_at'),
      supabase.from('race_results').select('*').order('raced_at',{ascending:false}).limit(30),
    ])
    set({ turtles: (turtles ?? []) as DbTurtle[], history: (hist ?? []) as DbRaceResult[] })
  },

  saveMoney: async (n: number) => {
    set({ money: n })
    await supabase.from('game_state').update({ money: n, updated_at: new Date().toISOString() }).eq('id','default')
  },

  setRacers: (ids) => set({ racerIds: ids }),
  setBet: (n) => set({ bet: n }),
  setSpeed: (s) => set({ speedMult: s }),
}))
