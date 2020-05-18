#![feature(specialization, const_fn)]

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod ui;
mod map;
mod root;
mod util;

#[pyfunction]
fn launch(py: Python) -> PyResult<()> {
    ui::launch(py)
}

#[pymodule]
fn yarts(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(launch))?;
    m.add_class::<root::Root>()?;
    m.add_class::<map::sector::Sector>()?;
    m.add_class::<map::renderer::MapRenderer>()?;

    Ok(())
}
