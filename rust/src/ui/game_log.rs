use crate::util::YartsResult;
use ggez::Context;
use glyph_brush::HorizontalAlign;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::time::Instant;

struct Line {
    msg: String,
    created: Instant,
}

#[pyclass]
pub struct GameLog {
    lines: Vec<Line>,
}

#[pymethods]
impl GameLog {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec![]
    }

    #[new]
    fn new(py: Python) -> GameLog {
        GameLog {
            lines: vec![]
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, kwargs: Option<&PyDict>) -> PyResult<()> {
        Ok(())
    }

    fn log(&mut self, msg: String) -> PyResult<()> {
        self.lines.push(Line {msg, created: Instant::now()});
        Ok(())
    }
}

impl GameLog {

}
