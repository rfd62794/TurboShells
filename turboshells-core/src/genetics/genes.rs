//! Gene definitions - central registry of all genetic traits

use std::collections::HashMap;
use rand::Rng;
use crate::types::{GeneValue, Rgb};

/// Definition of a single gene
#[derive(Clone, Debug)]
pub struct GeneDefinition {
    pub gene_type: String,  // "rgb", "discrete", "continuous"
    pub default: GeneValue,
    pub description: String,
    // Range data
    pub discrete_options: Option<Vec<String>>,
    pub continuous_range: Option<(f32, f32)>,
}

impl GeneDefinition {
    pub fn rgb(default: Rgb, description: &str) -> Self {
        Self {
            gene_type: "rgb".to_string(),
            default: GeneValue::Rgb(default),
            description: description.to_string(),
            discrete_options: None,
            continuous_range: None,
        }
    }
    
    pub fn discrete(options: Vec<&str>, default: &str, description: &str) -> Self {
        Self {
            gene_type: "discrete".to_string(),
            default: GeneValue::Discrete(default.to_string()),
            description: description.to_string(),
            discrete_options: Some(options.iter().map(|s| s.to_string()).collect()),
            continuous_range: None,
        }
    }
    
    pub fn continuous(range: (f32, f32), default: f32, description: &str) -> Self {
        Self {
            gene_type: "continuous".to_string(),
            default: GeneValue::Continuous(default),
            description: description.to_string(),
            discrete_options: None,
            continuous_range: Some(range),
        }
    }
}

/// Central registry of all gene definitions
#[derive(Clone, Debug)]
pub struct GeneDefinitions {
    definitions: HashMap<String, GeneDefinition>,
}

impl GeneDefinitions {
    pub fn new() -> Self {
        let mut definitions = HashMap::new();
        
        // Shell Genetics
        definitions.insert("shell_base_color".to_string(), 
            GeneDefinition::rgb(Rgb::new(34, 139, 34), "Primary shell color"));
        definitions.insert("shell_pattern_type".to_string(),
            GeneDefinition::discrete(vec!["hex", "spots", "stripes", "rings"], "hex", "Shell pattern type"));
        definitions.insert("shell_pattern_color".to_string(),
            GeneDefinition::rgb(Rgb::new(255, 255, 255), "Shell pattern color"));
        definitions.insert("pattern_color".to_string(),
            GeneDefinition::rgb(Rgb::new(255, 255, 255), "Pattern color (renderer alias)"));
        definitions.insert("shell_pattern_density".to_string(),
            GeneDefinition::continuous((0.1, 1.0), 0.5, "Pattern density/intensity"));
        definitions.insert("shell_pattern_opacity".to_string(),
            GeneDefinition::continuous((0.3, 1.0), 0.8, "Pattern transparency"));
        definitions.insert("shell_size_modifier".to_string(),
            GeneDefinition::continuous((0.5, 1.5), 1.0, "Shell size scaling"));
        
        // Body Genetics
        definitions.insert("body_base_color".to_string(),
            GeneDefinition::rgb(Rgb::new(107, 142, 35), "Primary body color"));
        definitions.insert("body_pattern_type".to_string(),
            GeneDefinition::discrete(vec!["solid", "mottled", "speckled", "marbled"], "solid", "Body pattern type"));
        definitions.insert("body_pattern_color".to_string(),
            GeneDefinition::rgb(Rgb::new(85, 107, 47), "Body pattern color"));
        definitions.insert("body_pattern_density".to_string(),
            GeneDefinition::continuous((0.1, 1.0), 0.3, "Body pattern density"));
        
        // Head Genetics
        definitions.insert("head_size_modifier".to_string(),
            GeneDefinition::continuous((0.7, 1.3), 1.0, "Head size scaling"));
        definitions.insert("head_color".to_string(),
            GeneDefinition::rgb(Rgb::new(139, 90, 43), "Head color"));
        
        // Leg Genetics
        definitions.insert("leg_length".to_string(),
            GeneDefinition::continuous((0.5, 1.5), 1.0, "Leg length scaling"));
        definitions.insert("limb_shape".to_string(),
            GeneDefinition::discrete(vec!["flippers", "feet", "fins"], "flippers", "Limb shape type"));
        definitions.insert("leg_thickness_modifier".to_string(),
            GeneDefinition::continuous((0.7, 1.3), 1.0, "Leg thickness"));
        definitions.insert("leg_color".to_string(),
            GeneDefinition::rgb(Rgb::new(101, 67, 33), "Leg color"));
        
        // Eye Genetics
        definitions.insert("eye_color".to_string(),
            GeneDefinition::rgb(Rgb::new(0, 0, 0), "Eye color"));
        definitions.insert("eye_size_modifier".to_string(),
            GeneDefinition::continuous((0.8, 1.2), 1.0, "Eye size scaling"));
        
        Self { definitions }
    }
    
    pub fn get(&self, name: &str) -> Option<&GeneDefinition> {
        self.definitions.get(name)
    }
    
    pub fn names(&self) -> Vec<&String> {
        self.definitions.keys().collect()
    }
    
    pub fn get_defaults(&self) -> HashMap<String, GeneValue> {
        self.definitions.iter()
            .map(|(k, v)| (k.clone(), v.default.clone()))
            .collect()
    }
    
    pub fn generate_random(&self) -> HashMap<String, GeneValue> {
        let mut rng = rand::thread_rng();
        let mut genetics = HashMap::new();
        
        for (name, def) in &self.definitions {
            let value = match def.gene_type.as_str() {
                "rgb" => GeneValue::Rgb(Rgb::new(
                    rng.gen_range(0..=255),
                    rng.gen_range(0..=255),
                    rng.gen_range(0..=255),
                )),
                "discrete" => {
                    if let Some(options) = &def.discrete_options {
                        let idx = rng.gen_range(0..options.len());
                        GeneValue::Discrete(options[idx].clone())
                    } else {
                        def.default.clone()
                    }
                },
                "continuous" => {
                    if let Some((min, max)) = def.continuous_range {
                        GeneValue::Continuous(rng.gen_range(min..=max))
                    } else {
                        def.default.clone()
                    }
                },
                _ => def.default.clone(),
            };
            genetics.insert(name.clone(), value);
        }
        
        genetics
    }
}
