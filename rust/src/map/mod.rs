use pyo3::prelude::*;
use std::collections::HashMap;

pub mod loader;
pub mod renderer;
pub mod sector;
pub mod sector_renderer;
pub mod space;

#[pyclass(module = "yarts", subclass)]
pub struct Map {
    sectors: HashMap<(i32, i32), PyObject>,
}

#[pymethods]
impl Map {
    #[new]
    pub fn new() -> PyResult<Self> {
        Ok(Map {
            sectors: HashMap::new(),
        })
    }

    fn get_sector(&self, py: Python, sx: i32, sy: i32) -> PyResult<PyObject> {
        self.sectors
            .get(&(sx, sy))
            .map(|obj| obj.clone_ref(py))
            .ok_or_else(|| pyo3::exceptions::KeyError::py_err("sector doesn't exist"))
    }

    fn get_sector_or_none(&self, py: Python, sx: i32, sy: i32) -> PyObject {
        self.sectors
            .get(&(sx, sy))
            .map(|obj| obj.clone_ref(py))
            .or_else(|| py.None().into())
            .unwrap()
    }

    fn store_sector(&mut self, sx: i32, sy: i32, sec: PyObject) -> PyResult<()> {
        self.sectors.insert((sx, sy), sec);
        Ok(())
    }

    fn get_all_sectors(&self, py: Python) -> PyResult<Vec<(i32, i32, PyObject)>> {
        let s = self
            .sectors
            .iter()
            .map(|((sx, sy), sec)| (*sx, *sy, sec.clone_ref(py)))
            .collect::<Vec<_>>();

        Ok(s)
    }
}
