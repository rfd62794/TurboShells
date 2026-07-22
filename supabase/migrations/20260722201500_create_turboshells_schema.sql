/*
# TurboShells Web Game Schema

## Overview
Single-tenant game database for TurboShells — a turtle breeding and racing management game.
No user authentication required. All data is shared/public via anon key.

## Tables

### `game_state`
Stores the player's persistent game state (money, settings, etc).
A single row with id='default' is used as the singleton player record.
- `id` (text, primary key) — always 'default'
- `money` (integer) — player's current cash balance
- `race_speed` (integer) — preferred race speed multiplier (1/2/4)
- `updated_at` (timestamptz) — last save time

### `turtles`
The player's turtle roster. Each turtle has stats, a genome string, and race records.
- `id` (uuid, primary key)
- `name` (text)
- `speed` (numeric) — base speed stat (1–10 scale)
- `max_energy` (numeric) — max energy before resting
- `recovery` (numeric) — energy recovery rate
- `swim` (numeric) — water terrain multiplier
- `climb` (numeric) — rock terrain multiplier
- `stamina` (numeric) — endurance stat
- `luck` (numeric) — RNG bonus stat
- `genome` (text) — compact visual encoding e.g. "B1-S2-P0-CFF0000"
- `total_races` (integer)
- `total_wins` (integer)
- `generation` (integer) — 0 for purchased/starter, increments on breed
- `parent_a_id` (uuid, nullable) — FK to turtles
- `parent_b_id` (uuid, nullable) — FK to turtles
- `is_retired` (boolean) — retired turtles stay in history but can't race
- `created_at` (timestamptz)

### `race_results`
Historical race result for each turtle in each race.
- `id` (uuid, primary key)
- `race_id` (text) — groups results from the same race
- `turtle_id` (uuid, FK turtles)
- `turtle_name` (text) — denormalized for history queries
- `rank` (integer) — finishing position (1 = winner)
- `final_distance` (numeric)
- `final_time_ms` (numeric)
- `bet_amount` (integer) — how much the player bet on this race (0 if none)
- `won_bet` (boolean)
- `raced_at` (timestamptz)

## Security
RLS enabled on all tables. No auth — anon + authenticated both get full CRUD.
Data is intentionally public/single-tenant.
*/

-- Game State singleton
CREATE TABLE IF NOT EXISTS game_state (
  id text PRIMARY KEY DEFAULT 'default',
  money integer NOT NULL DEFAULT 1000,
  race_speed integer NOT NULL DEFAULT 1,
  updated_at timestamptz DEFAULT now()
);

-- Insert default row if missing
INSERT INTO game_state (id, money, race_speed)
VALUES ('default', 1000, 1)
ON CONFLICT (id) DO NOTHING;

ALTER TABLE game_state ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "anon_select_game_state" ON game_state;
CREATE POLICY "anon_select_game_state" ON game_state FOR SELECT
  TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_game_state" ON game_state;
CREATE POLICY "anon_insert_game_state" ON game_state FOR INSERT
  TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_game_state" ON game_state;
CREATE POLICY "anon_update_game_state" ON game_state FOR UPDATE
  TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_game_state" ON game_state;
CREATE POLICY "anon_delete_game_state" ON game_state FOR DELETE
  TO anon, authenticated USING (true);

-- Turtles
CREATE TABLE IF NOT EXISTS turtles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  speed numeric NOT NULL DEFAULT 5,
  max_energy numeric NOT NULL DEFAULT 100,
  recovery numeric NOT NULL DEFAULT 1,
  swim numeric NOT NULL DEFAULT 5,
  climb numeric NOT NULL DEFAULT 5,
  stamina numeric NOT NULL DEFAULT 5,
  luck numeric NOT NULL DEFAULT 5,
  genome text NOT NULL DEFAULT 'B0-S0-P0-C228B22',
  total_races integer NOT NULL DEFAULT 0,
  total_wins integer NOT NULL DEFAULT 0,
  generation integer NOT NULL DEFAULT 0,
  parent_a_id uuid REFERENCES turtles(id) ON DELETE SET NULL,
  parent_b_id uuid REFERENCES turtles(id) ON DELETE SET NULL,
  is_retired boolean NOT NULL DEFAULT false,
  created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_turtles_is_retired ON turtles(is_retired);

ALTER TABLE turtles ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "anon_select_turtles" ON turtles;
CREATE POLICY "anon_select_turtles" ON turtles FOR SELECT
  TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_turtles" ON turtles;
CREATE POLICY "anon_insert_turtles" ON turtles FOR INSERT
  TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_turtles" ON turtles;
CREATE POLICY "anon_update_turtles" ON turtles FOR UPDATE
  TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_turtles" ON turtles;
CREATE POLICY "anon_delete_turtles" ON turtles FOR DELETE
  TO anon, authenticated USING (true);

-- Race Results
CREATE TABLE IF NOT EXISTS race_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  race_id text NOT NULL,
  turtle_id uuid REFERENCES turtles(id) ON DELETE SET NULL,
  turtle_name text NOT NULL,
  rank integer NOT NULL,
  final_distance numeric NOT NULL DEFAULT 0,
  final_time_ms numeric NOT NULL DEFAULT 0,
  bet_amount integer NOT NULL DEFAULT 0,
  won_bet boolean NOT NULL DEFAULT false,
  raced_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_race_results_race_id ON race_results(race_id);
CREATE INDEX IF NOT EXISTS idx_race_results_turtle_id ON race_results(turtle_id);
CREATE INDEX IF NOT EXISTS idx_race_results_raced_at ON race_results(raced_at DESC);

ALTER TABLE race_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "anon_select_race_results" ON race_results;
CREATE POLICY "anon_select_race_results" ON race_results FOR SELECT
  TO anon, authenticated USING (true);

DROP POLICY IF EXISTS "anon_insert_race_results" ON race_results;
CREATE POLICY "anon_insert_race_results" ON race_results FOR INSERT
  TO anon, authenticated WITH CHECK (true);

DROP POLICY IF EXISTS "anon_update_race_results" ON race_results;
CREATE POLICY "anon_update_race_results" ON race_results FOR UPDATE
  TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "anon_delete_race_results" ON race_results;
CREATE POLICY "anon_delete_race_results" ON race_results FOR DELETE
  TO anon, authenticated USING (true);
