use pyo3::prelude::*;
use pyo3::types::PyDict;
use ggez::{Context, GameResult};
use std::sync::Arc;
use std::collections::HashMap;
use super::sector_renderer::SectorRenderer;
use std::cell::RefCell;

#[pyclass]
pub struct MapRenderer {
    map: PyObject,
    data_src: PyObject,

    active_renderers: Vec<Arc<RefCell<SectorRenderer>>>,
    all_renderers: HashMap<(u32, u32), Arc<RefCell<SectorRenderer>>>,

    #[pyo3(get)]
    looksector: PyObject,
}

#[pymethods]
impl MapRenderer {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["map", "camera", "datasrc", "game"]
    }

    #[new]
    fn new(py: Python) -> Self {
        MapRenderer {
            map: py.None(),
            data_src: py.None(),
            looksector: py.None(),

            active_renderers: Vec::new(),
            all_renderers: HashMap::new(),
        }
    }

    #[args(kwargs = "**")]
    fn inject(slf: &PyCell<Self>, py: Python, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        slf.borrow_mut().map = deps.get_item("map")?.to_object(py);

        let camera = deps.get_item("camera")?;
        //let selfpy: PyObject = self.into_py(py);

        let lookat = slf.getattr("lookat")?;
        camera.getattr("onlookpointchanged")?.call_method1("add", (lookat,))?;

        Ok(())
    }

    fn lookat(&mut self, py: Python, sector: &PyAny) -> PyResult<()> {
        println!("looking at sector: {}", sector);

        self.looksector = sector.into();

        self.setup_sector(py, self.looksector.clone_ref(py), 0, 0)?;

        let neighbors = self.looksector.getattr(py, "neighbour")?;
        let neighbors: &PyDict = neighbors.extract(py)?;
        for (key, sec) in neighbors {
            let (dx, dy): (i16, i16) = key.extract()?;
            if !sec.is_none() {
                self.setup_sector(py, sec.into(), dx, dy)?;
            }
        }

        Ok(())
    }
}

impl MapRenderer {
    fn setup_sector(&mut self, py: Python, sector: PyObject, dx: i16, dy: i16) -> PyResult<()> {
        let sx = sector.getattr(py, "sx")?.extract::<u32>(py)?;
        let sy = sector.getattr(py, "sy")?.extract::<u32>(py)?;

        let sr = if let Some(sr) = self.all_renderers.get(&(sx, sy)) {
            Arc::clone(sr)
        } else {
            let sr = Arc::new(RefCell::new(SectorRenderer::new(py, sector)?));
            self.all_renderers.insert((sx, sy), Arc::clone(&sr));
            sr
        };

        sr.borrow_mut().update_offset(dx, dy);
        self.active_renderers.push(sr);
        Ok(())
    }

    pub fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        for sr in &self.active_renderers {
            sr.borrow_mut().draw(ctx)?;
        }

        Ok(())
    }
}