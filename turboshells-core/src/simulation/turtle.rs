//! Turtle entity with physics

use crate::types::TurtleStats;
use super::terrain::{Terrain, TerrainType};
use uuid::Uuid;

/// Physics constants (matching Python)
const TERRAIN_DIFFICULTY: f32 = 0.8;
const RECOVERY_RATE: f32 = 0.1;
const RECOVERY_THRESHOLD: f32 = 0.5;

/// A racing turtle with stats and physics
#[derive(Clone, Debug)]
pub struct Turtle {
    pub id: String,
    pub name: String,
    pub stats: TurtleStats,
    
    // Race state
    pub current_energy: f32,
    pub race_distance: f32,
    pub is_resting: bool,
    pub finished: bool,
}

impl Turtle {
    pub fn new(name: String, stats: TurtleStats) -> Self {
        let id = Uuid::new_v4().to_string()[..8].to_string();
        let current_energy = stats.max_energy;
        
        Self {
            id,
            name,
            stats,
            current_energy,
            race_distance: 0.0,
            is_resting: false,
            finished: false,
        }
    }
    
    /// Reset for a new race
    pub fn reset_for_race(&mut self) {
        self.current_energy = self.stats.max_energy;
        self.race_distance = 0.0;
        self.is_resting = false;
        self.finished = false;
    }
    
    /// Update physics for one tick
    /// Returns distance moved
    pub fn update_physics(&mut self, terrain: &Terrain) -> f32 {
        if self.finished {
            return 0.0;
        }
        
        // 1. RECOVERY LOGIC
        if self.is_resting {
            let stamina_bonus = self.stats.stamina / 20.0;
            let recovery_rate = RECOVERY_RATE * (1.0 + stamina_bonus);
            self.current_energy += self.stats.recovery * recovery_rate;
            
            if self.current_energy >= self.stats.max_energy * RECOVERY_THRESHOLD {
                self.is_resting = false;
            }
            return 0.0;
        }
        
        // 2. MOVEMENT LOGIC
        let mut move_speed = self.stats.speed;
        
        match terrain.terrain_type {
            TerrainType::Water => {
                let swim_bonus = self.stats.swim / 10.0;
                move_speed *= swim_bonus * terrain.speed_modifier;
            },
            TerrainType::Rocks => {
                let climb_bonus = self.stats.climb / 10.0;
                move_speed *= climb_bonus * terrain.speed_modifier;
            },
            TerrainType::Sand => {
                let recovery_bonus = self.stats.recovery / 15.0;
                move_speed *= (1.0 + recovery_bonus) * terrain.speed_modifier;
            },
            TerrainType::Mud => {
                let energy_factor = self.current_energy / self.stats.max_energy;
                move_speed *= energy_factor * terrain.speed_modifier;
            },
            TerrainType::Boost => {
                move_speed *= terrain.speed_modifier * 1.2;
            },
            TerrainType::Normal => {
                move_speed *= terrain.speed_modifier;
            },
        }
        
        // 3. ENERGY DRAIN
        let base_drain = 0.5 * TERRAIN_DIFFICULTY;
        let actual_drain = base_drain * terrain.energy_drain;
        self.current_energy -= actual_drain;
        
        if self.current_energy <= 0.0 {
            self.current_energy = 0.0;
            self.is_resting = true;
        }
        
        move_speed
    }
}
