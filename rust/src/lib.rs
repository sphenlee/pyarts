#![feature(specialization, const_fn)]

use pyo3::prelude::*;
use pyo3::wrap_pyfunction;

mod ui;

#[pyfunction]
fn launch(py: Python) -> PyResult<()> {
    ui::launch(py)
}

#[pymodule]
fn yarts(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_wrapped(wrap_pyfunction!(launch))?;

    Ok(())
}
