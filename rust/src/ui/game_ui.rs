use crate::scene::{WIDTH, HEIGHT};
use crate::util::YartsResult;
use ggez::graphics::DrawParam;
use ggez::{graphics, Context};
use pyo3::prelude::*;
use pyo3::types::{PyBytes, PyDict};

#[pyclass]
pub struct GameUi {
    panels: Vec<PyObject>,
}

#[pymethods]
impl GameUi {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["infopanel", "abilitypanel", "townspanel"]
    }

    #[new]
    fn new(_py: Python) -> GameUi {
        GameUi {
            panels: vec![],
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        self.panels.push(deps.get_item("infopanel")?.into());
        self.panels.push(deps.get_item("abilitypanel")?.into());
        self.panels.push(deps.get_item("townspanel")?.into());

        Ok(())
    }
}

impl GameUi {
    pub fn step(&mut self, py: Python) -> YartsResult<()> {
        for panel in &self.panels {
            panel.call_method1(py, "step", ())?;
        }

        Ok(())
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context) -> YartsResult<()> {
        for panel in &self.panels {
            GameUi::draw_one(py, ctx, panel)?;
        }
        Ok(())
    }

    fn draw_one(py: Python, ctx: &mut Context, panel: &PyObject) -> YartsResult<()> {
         let rendered = panel.call_method0(py, "render")?;

        if rendered.is_none() {
            return Ok(());
        }

        let (bytes, w, h): (&PyBytes, u16, u16) = rendered.extract(py)?;

        let mut rgba = bytes.as_bytes().to_vec();
        rgba.chunks_exact_mut(4).for_each(|pixel| {
            // pixels are stored BGRA but ggez wants RGBA
            // swap red and blue
            let b = pixel[0];
            let r = pixel[2];
            pixel[0] = r;
            pixel[2] = b;
        });

        // TODO - cache the image
        let img = graphics::Image::from_rgba8(ctx, w, h, &rgba)?;

        let dest: [f32; 2] = panel.call_method1(py, "destination", (WIDTH, HEIGHT))?.extract(py)?;

        graphics::draw(ctx, &img, DrawParam::new().dest(dest))?;

        Ok(())
    }
}
