#![feature(specialization, const_fn)]

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod map;
mod pathfinder;
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

#[pyfunction]
fn emit_log(_py: Python, target: String, level: String, msg: String) -> PyResult<()> {
    let level = level.parse::<log::Level>().unwrap();

    log::log!(target: &target, level, "{}", msg);

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
    m.add_wrapped(wrap_pyfunction!(emit_log))?;
    m.add_class::<root::Root>()?;
    m.add_class::<map::sector::Sector>()?;
    m.add_class::<map::renderer::MapRenderer>()?;
    m.add_class::<sprites::SpriteManager>()?;
    m.add_class::<ui::game_ui::GameUi>()?;
    m.add_class::<pathfinder::Pathfinder>()?;

    m.add_class::<Rust>()?;

    Ok(())
}
