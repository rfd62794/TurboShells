//! Terrain types and effects

/// Types of terrain
#[derive(Clone, Debug, PartialEq)]
pub enum TerrainType {
    Normal,
    Water,
    Rocks,
    Sand,
    Mud,
    Boost,
}

impl TerrainType {
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "water" => TerrainType::Water,
            "rocks" => TerrainType::Rocks,
            "sand" => TerrainType::Sand,
            "mud" => TerrainType::Mud,
            "boost" => TerrainType::Boost,
            _ => TerrainType::Normal,
        }
    }
}

/// Terrain segment with modifiers
#[derive(Clone, Debug)]
pub struct Terrain {
    pub terrain_type: TerrainType,
    pub speed_modifier: f32,
    pub energy_drain: f32,
}

impl Terrain {
    pub fn new(terrain_type: TerrainType, speed_modifier: f32, energy_drain: f32) -> Self {
        Self {
            terrain_type,
            speed_modifier,
            energy_drain,
        }
    }
    
    pub fn from_str(type_str: &str, speed_modifier: f32, energy_drain: f32) -> Self {
        Self {
            terrain_type: TerrainType::from_str(type_str),
            speed_modifier,
            energy_drain,
        }
    }
    
    /// Generate a random track of terrain segments
    pub fn generate_track(length: f32, segment_size: f32) -> Vec<Terrain> {
        use rand::Rng;
        let mut rng = rand::thread_rng();
        let num_segments = (length / segment_size).ceil() as usize;
        
        (0..num_segments).map(|_| {
            let roll: f32 = rng.gen();
            if roll < 0.6 {
                Terrain::normal()
            } else if roll < 0.75 {
                Terrain::water()
            } else if roll < 0.85 {
                Terrain::rocks()
            } else if roll < 0.93 {
                Terrain::sand()
            } else if roll < 0.97 {
                Terrain::mud()
            } else {
                Terrain::boost()
            }
        }).collect()
    }
    
    pub fn normal() -> Self {
        Self::new(TerrainType::Normal, 1.0, 1.0)
    }
    
    pub fn water() -> Self {
        Self::new(TerrainType::Water, 0.7, 1.2)
    }
    
    pub fn rocks() -> Self {
        Self::new(TerrainType::Rocks, 0.6, 1.3)
    }
    
    pub fn sand() -> Self {
        Self::new(TerrainType::Sand, 0.8, 1.1)
    }
    
    pub fn mud() -> Self {
        Self::new(TerrainType::Mud, 0.5, 1.5)
    }
    
    pub fn boost() -> Self {
        Self::new(TerrainType::Boost, 1.5, 0.8)
    }
}
