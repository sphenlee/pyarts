use super::sector_renderer::SectorRenderer;
use antidote::Mutex;
use ggez::{Context, GameResult};
use log::{debug, info};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashMap;
use std::sync::Arc;

#[pyclass]
pub struct MapRenderer {
    map: PyObject,
    _data_src: PyObject,

    active_renderers: Vec<Arc<Mutex<SectorRenderer>>>,
    all_renderers: HashMap<(u32, u32), Arc<Mutex<SectorRenderer>>>,
    //image_cache: HashMap<String, Image>,
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
            _data_src: py.None(),
            looksector: py.None(),

            active_renderers: Vec::new(),
            all_renderers: HashMap::new(),
            //image_cache: HashMap::new(),
        }
    }

    #[args(kwargs = "**")]
    fn inject(slf: &PyCell<Self>, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        let map = deps.get_item("map")?;
        let update_fog = slf.getattr("update_fog")?;
        map.getattr("onfogupdated")?
            .call_method1("add", (update_fog,))?;
        slf.borrow_mut().map = map.into();

        let camera = deps.get_item("camera")?;
        let look_at = slf.getattr("look_at")?;
        camera
            .getattr("onlookpointchanged")?
            .call_method1("add", (look_at,))?;

        Ok(())
    }

    fn look_at(&mut self, py: Python, sector: &PyAny) -> PyResult<()> {
        info!("looking at sector: {}", sector);

        self.active_renderers.clear();

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

    fn update_fog(&mut self, _py: Python) -> PyResult<()> {
        /*for sr in &self.active_renderers {
            sr.borrow_mut().update_fog()?;
        }*/

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
            let sr = Arc::new(Mutex::new(SectorRenderer::new(py, sector)?));
            self.all_renderers.insert((sx, sy), Arc::clone(&sr));
            sr
        };

        sr.lock().update_offset(dx, dy);
        self.active_renderers.push(sr);
        debug!("{} renderers active", self.active_renderers.len());
        Ok(())
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context, offset: (f32, f32)) -> GameResult<()> {
        for sr in &self.active_renderers {
            sr.lock().draw(py, ctx, offset)?;
        }

        Ok(())
    }
}
