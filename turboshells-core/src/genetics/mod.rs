//! Genetics module for TurboShells
//! 
//! Provides gene definitions, inheritance, and mutation systems.

mod genes;
mod inheritance;
mod mutation;

pub use genes::{GeneDefinition, GeneDefinitions};
pub use inheritance::Inheritance;
pub use mutation::Mutation;

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use crate::types::{GeneValue, Rgb};

/// Python-exposed Genetics class
#[pyclass]
pub struct PyGenetics {
    definitions: GeneDefinitions,
    inheritance: Inheritance,
    mutation: Mutation,
}

#[pymethods]
impl PyGenetics {
    #[new]
    pub fn new() -> Self {
        let definitions = GeneDefinitions::new();
        Self {
            inheritance: Inheritance::new(definitions.clone()),
            mutation: Mutation::new(definitions.clone()),
            definitions,
        }
    }
    
    /// Generate random genetics
    pub fn generate_random<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let genetics = self.definitions.generate_random();
        self.genetics_to_pydict(py, &genetics)
    }
    
    /// Get default genetics
    pub fn get_defaults<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyDict>> {
        let genetics = self.definitions.get_defaults();
        self.genetics_to_pydict(py, &genetics)
    }
    
    /// Inherit genetics from two parents (Mendelian 50/50)
    pub fn inherit<'py>(&self, py: Python<'py>, parent1: &Bound<'py, PyDict>, parent2: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyDict>> {
        let p1 = self.pydict_to_genetics(parent1)?;
        let p2 = self.pydict_to_genetics(parent2)?;
        let child = self.inheritance.inherit(&p1, &p2);
        self.genetics_to_pydict(py, &child)
    }
    
    /// Inherit with blending for continuous traits
    pub fn inherit_blended<'py>(&self, py: Python<'py>, parent1: &Bound<'py, PyDict>, parent2: &Bound<'py, PyDict>) -> PyResult<Bound<'py, PyDict>> {
        let p1 = self.pydict_to_genetics(parent1)?;
        let p2 = self.pydict_to_genetics(parent2)?;
        let child = self.inheritance.inherit_blended(&p1, &p2);
        self.genetics_to_pydict(py, &child)
    }
    
    /// Apply mutations with specified rate
    pub fn mutate<'py>(&self, py: Python<'py>, genetics: &Bound<'py, PyDict>, rate: f32) -> PyResult<Bound<'py, PyDict>> {
        let genes = self.pydict_to_genetics(genetics)?;
        let mutated = self.mutation.mutate(&genes, rate);
        self.genetics_to_pydict(py, &mutated)
    }
    
    /// Calculate genetic similarity (0.0 to 1.0)
    pub fn similarity(&self, genetics1: &Bound<'_, PyDict>, genetics2: &Bound<'_, PyDict>) -> PyResult<f32> {
        let g1 = self.pydict_to_genetics(genetics1)?;
        let g2 = self.pydict_to_genetics(genetics2)?;
        Ok(self.inheritance.calculate_similarity(&g1, &g2))
    }
}

impl PyGenetics {
    /// Convert Python dict to Rust HashMap
    fn pydict_to_genetics(&self, dict: &Bound<'_, PyDict>) -> PyResult<HashMap<String, GeneValue>> {
        let mut genetics = HashMap::new();
        
        for (key, value) in dict.iter() {
            let key_str: String = key.extract()?;
            let gene_def = self.definitions.get(&key_str);
            
            if let Some(def) = gene_def {
                let gene_value = match def.gene_type.as_str() {
                    "rgb" => {
                        let tuple: (u8, u8, u8) = value.extract()?;
                        GeneValue::Rgb(Rgb::from_tuple(tuple))
                    },
                    "discrete" => {
                        let s: String = value.extract()?;
                        GeneValue::Discrete(s)
                    },
                    "continuous" => {
                        let f: f32 = value.extract()?;
                        GeneValue::Continuous(f)
                    },
                    _ => continue,
                };
                genetics.insert(key_str, gene_value);
            }
        }
        
        Ok(genetics)
    }
    
    /// Convert Rust HashMap to Python dict
    fn genetics_to_pydict<'py>(&self, py: Python<'py>, genetics: &HashMap<String, GeneValue>) -> PyResult<Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        
        for (key, value) in genetics {
            match value {
                GeneValue::Rgb(rgb) => {
                    dict.set_item(key, rgb.to_tuple())?;
                },
                GeneValue::Discrete(s) => {
                    dict.set_item(key, s)?;
                },
                GeneValue::Continuous(f) => {
                    dict.set_item(key, f)?;
                },
            }
        }
        
        Ok(dict)
    }
}
