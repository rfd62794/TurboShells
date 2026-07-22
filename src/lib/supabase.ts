import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL as string,
  import.meta.env.VITE_SUPABASE_ANON_KEY as string,
)

export interface DbTurtle {
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
  total_races: number
  total_wins: number
  generation: number
  parent_a_id: string | null
  parent_b_id: string | null
  is_retired: boolean
  created_at: string
}

export interface DbRaceResult {
  id: string
  race_id: string
  turtle_id: string | null
  turtle_name: string
  rank: number
  final_distance: number
  final_time_ms: number
  bet_amount: number
  won_bet: boolean
  raced_at: string
}
