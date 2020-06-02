#![feature(specialization, const_fn)]

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod map;
mod root;
mod scene;
mod sprites;
mod ui;
mod util;

#[pyfunction]
fn launch(py: Python) -> PyResult<()> {
    scene::launch(py)?;
    Ok(())
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
    pretty_env_logger::init_timed();

    m.add_wrapped(wrap_pyfunction!(launch))?;
    m.add_class::<root::Root>()?;
    m.add_class::<map::sector::Sector>()?;
    m.add_class::<map::renderer::MapRenderer>()?;
    m.add_class::<sprites::SpriteManager>()?;
    m.add_class::<ui::game_ui::GameUi>()?;

    m.add_class::<Rust>()?;

    Ok(())
}
