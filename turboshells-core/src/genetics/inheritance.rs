//! Inheritance system - Mendelian genetics

use std::collections::HashMap;
use rand::Rng;
use crate::types::{GeneValue, Rgb};
use super::genes::GeneDefinitions;

/// Implements Mendelian inheritance patterns
pub struct Inheritance {
    definitions: GeneDefinitions,
}

impl Inheritance {
    pub fn new(definitions: GeneDefinitions) -> Self {
        Self { definitions }
    }
    
    /// Basic Mendelian inheritance (50/50 chance from each parent)
    pub fn inherit(
        &self,
        parent1: &HashMap<String, GeneValue>,
        parent2: &HashMap<String, GeneValue>,
    ) -> HashMap<String, GeneValue> {
        let mut rng = rand::thread_rng();
        let mut child = HashMap::new();
        
        for name in self.definitions.names() {
            let p1_value = parent1.get(name);
            let p2_value = parent2.get(name);
            
            let value = match (p1_value, p2_value) {
                (Some(v1), Some(v2)) => {
                    if rng.gen_bool(0.5) { v1.clone() } else { v2.clone() }
                },
                (Some(v), None) | (None, Some(v)) => v.clone(),
                (None, None) => {
                    if let Some(def) = self.definitions.get(name) {
                        def.default.clone()
                    } else {
                        continue;
                    }
                },
            };
            
            child.insert(name.clone(), value);
        }
        
        child
    }
    
    /// Blended inheritance (average continuous values, mix colors)
    pub fn inherit_blended(
        &self,
        parent1: &HashMap<String, GeneValue>,
        parent2: &HashMap<String, GeneValue>,
    ) -> HashMap<String, GeneValue> {
        let mut rng = rand::thread_rng();
        let mut child = HashMap::new();
        
        for name in self.definitions.names() {
            let def = match self.definitions.get(name) {
                Some(d) => d,
                None => continue,
            };
            
            let p1_value = parent1.get(name);
            let p2_value = parent2.get(name);
            
            let value = match (p1_value, p2_value, def.gene_type.as_str()) {
                // Blend RGB colors
                (Some(GeneValue::Rgb(c1)), Some(GeneValue::Rgb(c2)), "rgb") => {
                    let bias = rng.gen_range(0.3..0.7);
                    GeneValue::Rgb(c1.blend(c2, bias))
                },
                // Average continuous values
                (Some(GeneValue::Continuous(f1)), Some(GeneValue::Continuous(f2)), "continuous") => {
                    GeneValue::Continuous((f1 + f2) / 2.0)
                },
                // Discrete: random from parent
                (Some(v1), Some(v2), "discrete") => {
                    if rng.gen_bool(0.5) { v1.clone() } else { v2.clone() }
                },
                // Fallback
                (Some(v), None, _) | (None, Some(v), _) => v.clone(),
                _ => def.default.clone(),
            };
            
            child.insert(name.clone(), value);
        }
        
        child
    }
    
    /// Calculate genetic similarity (0.0 to 1.0)
    pub fn calculate_similarity(
        &self,
        genetics1: &HashMap<String, GeneValue>,
        genetics2: &HashMap<String, GeneValue>,
    ) -> f32 {
        let mut similar = 0.0;
        let mut total = 0.0;
        
        for name in self.definitions.names() {
            let v1 = genetics1.get(name);
            let v2 = genetics2.get(name);
            
            let def = match self.definitions.get(name) {
                Some(d) => d,
                None => continue,
            };
            
            total += 1.0;
            
            match (v1, v2, def.gene_type.as_str()) {
                (Some(GeneValue::Rgb(c1)), Some(GeneValue::Rgb(c2)), "rgb") => {
                    // Color similarity based on Euclidean distance
                    let max_dist = (255.0_f32.powi(2) * 3.0).sqrt();
                    let dist = c1.distance(c2);
                    similar += 1.0 - (dist / max_dist);
                },
                (Some(GeneValue::Continuous(f1)), Some(GeneValue::Continuous(f2)), "continuous") => {
                    if let Some((min, max)) = def.continuous_range {
                        let range = max - min;
                        let diff = (f1 - f2).abs() / range;
                        similar += 1.0 - diff;
                    }
                },
                (Some(GeneValue::Discrete(s1)), Some(GeneValue::Discrete(s2)), "discrete") => {
                    if s1 == s2 {
                        similar += 1.0;
                    }
                },
                _ => {},
            }
        }
        
        if total > 0.0 { similar / total } else { 0.0 }
    }
}
