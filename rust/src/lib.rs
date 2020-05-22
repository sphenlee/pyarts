#![feature(specialization, const_fn)]

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod map;
mod root;
mod sprites;
mod ui;
mod util;

#[pyfunction]
fn launch(py: Python) -> PyResult<()> {
    ui::launch(py)
}

#[pyclass(subclass, dict)]
struct Rust {}

#[pymethods]
impl Rust {
    #[new]
    fn new() -> Rust {
        Rust {}
    }
}

#[pymodule]
fn yarts(_py: Python, m: &PyModule) -> PyResult<()> {
    //pretty_env_logger::init_timed();
    tracing_subscriber::fmt::init();

    m.add_wrapped(wrap_pyfunction!(launch))?;
    m.add_class::<root::Root>()?;
    m.add_class::<map::sector::Sector>()?;
    m.add_class::<map::renderer::MapRenderer>()?;
    m.add_class::<sprites::SpriteManager>()?;

    m.add_class::<Rust>()?;

    Ok(())
}
