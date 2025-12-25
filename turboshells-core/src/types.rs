//! Shared types for TurboShells Core

use pyo3::prelude::*;
use serde::{Deserialize, Serialize};

/// RGB color representation
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub struct Rgb {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

impl Rgb {
    pub fn new(r: u8, g: u8, b: u8) -> Self {
        Self { r, g, b }
    }
    
    /// Create from Python tuple (r, g, b)
    pub fn from_tuple(tuple: (u8, u8, u8)) -> Self {
        Self { r: tuple.0, g: tuple.1, b: tuple.2 }
    }
    
    /// Convert to Python tuple
    pub fn to_tuple(&self) -> (u8, u8, u8) {
        (self.r, self.g, self.b)
    }
    
    /// Calculate Euclidean distance between two colors
    pub fn distance(&self, other: &Rgb) -> f32 {
        let dr = (self.r as f32) - (other.r as f32);
        let dg = (self.g as f32) - (other.g as f32);
        let db = (self.b as f32) - (other.b as f32);
        (dr * dr + dg * dg + db * db).sqrt()
    }
    
    /// Blend two colors with a bias (0.0 = self, 1.0 = other)
    pub fn blend(&self, other: &Rgb, bias: f32) -> Rgb {
        let bias = bias.clamp(0.0, 1.0);
        Rgb {
            r: ((self.r as f32) * (1.0 - bias) + (other.r as f32) * bias) as u8,
            g: ((self.g as f32) * (1.0 - bias) + (other.g as f32) * bias) as u8,
            b: ((self.b as f32) * (1.0 - bias) + (other.b as f32) * bias) as u8,
        }
    }
}

impl Default for Rgb {
    fn default() -> Self {
        Self { r: 128, g: 128, b: 128 }
    }
}

/// Turtle stats structure
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TurtleStats {
    pub speed: f32,
    pub max_energy: f32,
    pub recovery: f32,
    pub swim: f32,
    pub climb: f32,
    pub stamina: f32,
    pub luck: f32,
}

impl Default for TurtleStats {
    fn default() -> Self {
        Self {
            speed: 5.0,
            max_energy: 100.0,
            recovery: 5.0,
            swim: 5.0,
            climb: 5.0,
            stamina: 3.0,
            luck: 3.0,
        }
    }
}

/// Gene value types
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum GeneValue {
    Rgb(Rgb),
    Discrete(String),
    Continuous(f32),
}

impl GeneValue {
    pub fn as_rgb(&self) -> Option<&Rgb> {
        match self {
            GeneValue::Rgb(rgb) => Some(rgb),
            _ => None,
        }
    }
    
    pub fn as_discrete(&self) -> Option<&str> {
        match self {
            GeneValue::Discrete(s) => Some(s),
            _ => None,
        }
    }
    
    pub fn as_continuous(&self) -> Option<f32> {
        match self {
            GeneValue::Continuous(f) => Some(*f),
            _ => None,
        }
    }
}
