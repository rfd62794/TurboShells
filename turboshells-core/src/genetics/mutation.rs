//! Mutation system - genetic variations

use std::collections::HashMap;
use rand::Rng;
use rand::distributions::{Distribution, Standard};
use crate::types::{GeneValue, Rgb};
use super::genes::GeneDefinitions;

/// Implements genetic mutations
pub struct Mutation {
    definitions: GeneDefinitions,
}

impl Mutation {
    pub fn new(definitions: GeneDefinitions) -> Self {
        Self { definitions }
    }
    
    /// Apply mutations with specified rate (0.0 to 1.0)
    pub fn mutate(
        &self,
        genetics: &HashMap<String, GeneValue>,
        rate: f32,
    ) -> HashMap<String, GeneValue> {
        let mut rng = rand::thread_rng();
        let mut mutated = genetics.clone();
        
        for (name, value) in genetics {
            if rng.gen::<f32>() < rate {
                if let Some(def) = self.definitions.get(name) {
                    let new_value = self.mutate_gene(value, def);
                    mutated.insert(name.clone(), new_value);
                }
            }
        }
        
        mutated
    }
    
    /// Mutate a single gene value
    fn mutate_gene(&self, value: &GeneValue, def: &super::genes::GeneDefinition) -> GeneValue {
        match (value, def.gene_type.as_str()) {
            (GeneValue::Rgb(rgb), "rgb") => {
                GeneValue::Rgb(self.mutate_rgb(rgb))
            },
            (GeneValue::Discrete(s), "discrete") => {
                if let Some(options) = &def.discrete_options {
                    GeneValue::Discrete(self.mutate_discrete(s, options))
                } else {
                    value.clone()
                }
            },
            (GeneValue::Continuous(f), "continuous") => {
                if let Some(range) = def.continuous_range {
                    GeneValue::Continuous(self.mutate_continuous(*f, range))
                } else {
                    value.clone()
                }
            },
            _ => value.clone(),
        }
    }
    
    /// Mutate RGB color with slight variations
    fn mutate_rgb(&self, color: &Rgb) -> Rgb {
        let mut rng = rand::thread_rng();
        Rgb {
            r: (color.r as i16 + rng.gen_range(-30..=30)).clamp(0, 255) as u8,
            g: (color.g as i16 + rng.gen_range(-30..=30)).clamp(0, 255) as u8,
            b: (color.b as i16 + rng.gen_range(-30..=30)).clamp(0, 255) as u8,
        }
    }
    
    /// Mutate discrete value by selecting a different option
    fn mutate_discrete(&self, current: &str, options: &[String]) -> String {
        let mut rng = rand::thread_rng();
        let available: Vec<_> = options.iter().filter(|o| *o != current).collect();
        if available.is_empty() {
            current.to_string()
        } else {
            available[rng.gen_range(0..available.len())].clone()
        }
    }
    
    /// Mutate continuous value with gaussian noise
    fn mutate_continuous(&self, value: f32, range: (f32, f32)) -> f32 {
        let mut rng = rand::thread_rng();
        let range_size = range.1 - range.0;
        let mutation_strength = range_size * 0.1;  // 10% of range
        
        // Gaussian mutation using Box-Muller transform
        let u1: f32 = rng.gen();
        let u2: f32 = rng.gen();
        let normal = (-2.0 * u1.ln()).sqrt() * (2.0 * std::f32::consts::PI * u2).cos();
        
        let mutation = normal * mutation_strength;
        (value + mutation).clamp(range.0, range.1)
    }
    
    /// Adaptive mutation based on parent similarity
    pub fn adaptive_mutate(
        &self,
        genetics: &HashMap<String, GeneValue>,
        similarity: f32,
    ) -> HashMap<String, GeneValue> {
        // Higher similarity = higher mutation rate
        let rate = if similarity > 0.9 {
            0.3
        } else if similarity > 0.7 {
            0.2
        } else if similarity > 0.5 {
            0.1
        } else {
            0.05
        };
        
        self.mutate(genetics, rate)
    }
}
