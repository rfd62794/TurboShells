//! Race simulation

use super::turtle::Turtle;
use super::terrain::Terrain;

const SEGMENT_SIZE: f32 = 50.0;
const MAX_TICKS: u32 = 5000;

/// Race manager
pub struct Race {
    pub track: Vec<Terrain>,
    pub turtles: Vec<Turtle>,
    pub track_length: f32,
    pub tick_count: u32,
}

impl Race {
    pub fn new(track_length: f32) -> Self {
        let track = Terrain::generate_track(track_length, SEGMENT_SIZE);
        Self {
            track,
            turtles: Vec::new(),
            track_length,
            tick_count: 0,
        }
    }
    
    pub fn add_turtle(&mut self, turtle: Turtle) {
        self.turtles.push(turtle);
    }
    
    /// Get terrain at a given distance
    fn get_terrain_at(&self, distance: f32) -> Terrain {
        let segment_idx = (distance / SEGMENT_SIZE) as usize;
        self.track[segment_idx.min(self.track.len() - 1)].clone()
    }
    
    /// Run a single simulation tick
    /// Returns true if race is finished
    pub fn tick(&mut self) -> bool {
        self.tick_count += 1;
        
        // Collect terrain for each turtle first to avoid borrow issues
        let terrains: Vec<Terrain> = self.turtles
            .iter()
            .map(|t| self.get_terrain_at(t.race_distance))
            .collect();
        
        for (turtle, terrain) in self.turtles.iter_mut().zip(terrains.iter()) {
            if turtle.finished {
                continue;
            }
            
            let distance = turtle.update_physics(terrain);
            turtle.race_distance += distance;
            
            if turtle.race_distance >= self.track_length {
                turtle.finished = true;
            }
        }
        
        // Check if any turtle finished or max ticks reached
        self.turtles.iter().any(|t| t.finished) || self.tick_count >= MAX_TICKS
    }
    
    /// Run the full race
    /// Returns winner name
    pub fn run(&mut self) -> String {
        // Reset all turtles
        for turtle in &mut self.turtles {
            turtle.reset_for_race();
        }
        
        self.tick_count = 0;
        
        while !self.tick() {}
        
        // Find winner (furthest distance)
        self.turtles
            .iter()
            .max_by(|a, b| a.race_distance.partial_cmp(&b.race_distance).unwrap())
            .map(|t| t.name.clone())
            .unwrap_or_else(|| "DRAW".to_string())
    }
    
    /// Get current positions sorted by distance
    pub fn get_positions(&self) -> Vec<(String, f32)> {
        let mut positions: Vec<_> = self.turtles
            .iter()
            .map(|t| (t.name.clone(), t.race_distance))
            .collect();
        
        positions.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap());
        positions
    }
}
