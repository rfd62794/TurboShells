//! TurboShells Core - Rust library for turtle racing game
//! 
//! This library provides high-performance genetics and simulation systems
//! with Python bindings via PyO3.

use pyo3::prelude::*;

pub mod genetics;
pub mod simulation;
pub mod types;

use genetics::PyGenetics;
use simulation::{PyTurtle, PyRace};

/// TurboShells Core Python Module
/// 
/// Provides access to:
/// - Genetics: Gene definitions, inheritance, mutation
/// - Simulation: Turtle physics, race engine
#[pymodule]
fn turboshells_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyGenetics>()?;
    m.add_class::<PyTurtle>()?;
    m.add_class::<PyRace>()?;
    
    // Version info
    m.add("__version__", "0.1.0")?;
    
    Ok(())
}
