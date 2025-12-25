//! Simulation module for TurboShells
//! 
//! Provides turtle physics, terrain, and race simulation.

mod turtle;
mod terrain;
mod race;

pub use turtle::Turtle;
pub use terrain::{Terrain, TerrainType};
pub use race::Race;

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use crate::types::TurtleStats;

/// Python-exposed Turtle class
#[pyclass]
pub struct PyTurtle {
    inner: Turtle,
}

#[pymethods]
impl PyTurtle {
    #[new]
    #[pyo3(signature = (name, speed, energy, recovery, swim, climb, stamina=3.0, luck=3.0))]
    pub fn new(
        name: String,
        speed: f32,
        energy: f32,
        recovery: f32,
        swim: f32,
        climb: f32,
        stamina: f32,
        luck: f32,
    ) -> Self {
        Self {
            inner: Turtle::new(
                name,
                TurtleStats {
                    speed,
                    max_energy: energy,
                    recovery,
                    swim,
                    climb,
                    stamina,
                    luck,
                },
            ),
        }
    }
    
    #[getter]
    pub fn name(&self) -> &str {
        &self.inner.name
    }
    
    #[getter]
    pub fn id(&self) -> &str {
        &self.inner.id
    }
    
    #[getter]
    pub fn current_energy(&self) -> f32 {
        self.inner.current_energy
    }
    
    #[getter]
    pub fn race_distance(&self) -> f32 {
        self.inner.race_distance
    }
    
    #[getter]
    pub fn is_resting(&self) -> bool {
        self.inner.is_resting
    }
    
    #[getter]
    pub fn finished(&self) -> bool {
        self.inner.finished
    }
    
    /// Reset turtle for a new race
    pub fn reset_for_race(&mut self) {
        self.inner.reset_for_race();
    }
    
    /// Update physics for one tick
    /// Returns distance moved
    pub fn update_physics(&mut self, terrain_type: &str, speed_mod: f32, energy_drain: f32) -> f32 {
        let terrain = Terrain::from_str(terrain_type, speed_mod, energy_drain);
        self.inner.update_physics(&terrain)
    }
    
    /// Get stats as dict
    pub fn get_stats(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("speed", self.inner.stats.speed)?;
        dict.set_item("max_energy", self.inner.stats.max_energy)?;
        dict.set_item("recovery", self.inner.stats.recovery)?;
        dict.set_item("swim", self.inner.stats.swim)?;
        dict.set_item("climb", self.inner.stats.climb)?;
        dict.set_item("stamina", self.inner.stats.stamina)?;
        dict.set_item("luck", self.inner.stats.luck)?;
        Ok(dict.into())
    }
}

/// Python-exposed Race class
#[pyclass]
pub struct PyRace {
    inner: Race,
}

#[pymethods]
impl PyRace {
    #[new]
    pub fn new(track_length: f32) -> Self {
        Self {
            inner: Race::new(track_length),
        }
    }
    
    /// Add a turtle to the race
    pub fn add_turtle(&mut self, turtle: &PyTurtle) {
        self.inner.add_turtle(turtle.inner.clone());
    }
    
    /// Run the full race
    /// Returns winner name
    pub fn run(&mut self) -> String {
        self.inner.run()
    }
    
    /// Run a single tick
    /// Returns true if race is finished
    pub fn tick(&mut self) -> bool {
        self.inner.tick()
    }
    
    /// Get current positions as list of (name, distance)
    pub fn get_positions(&self, py: Python) -> PyResult<PyObject> {
        let positions: Vec<(String, f32)> = self.inner.get_positions();
        Ok(positions.into_py(py))
    }
}
