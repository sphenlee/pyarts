use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::conversion::ToPyObject;

use crate::map::renderer::MapRenderer;
use ggez::Context;
use ggez::nalgebra::{Matrix4, Vector3};
use crate::ui::{WIDTH, HEIGHT, Event, Transition};
use crate::util::PyGgezError;

#[pyclass]
pub struct Root {
    map_renderer: PyObject,
    camera: PyObject,
    game_state: PyObject,
    deps: PyObject,

    // for tracking camera movement - move somewhere else?
    dx: i32,
    dy: i32,
}

#[pymethods]
impl Root {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["settings", "datasrc", "map", "game", "gamestate", "maprenderer", "camera"]
    }

    #[new]
    fn new(py: Python<'_>) -> Self {
        Root {
            map_renderer: py.None(),
            camera: py.None(),
            game_state: py.None(),
            deps: py.None(),

            dx: 0,
            dy: 0,
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, py: Python, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps = kwargs.expect("inject must be called with kwargs").as_ref();

        self.map_renderer = deps.get_item("maprenderer")?.to_object(py);
        self.camera = deps.get_item("camera")?.to_object(py);
        self.game_state = deps.get_item("gamestate")?.to_object(py);
        self.deps = deps.to_object(py);

        Ok(())
    }
}

impl Root {
    pub fn load(&mut self, py: Python) -> PyResult<()> {
        self.deps.as_ref(py).get_item("settings")?.call_method0("load")?;

        Ok(())
    }

    pub fn update(&mut self, py: Python) -> PyResult<()> {
        if self.dx != 0 || self.dy != 0 {
            self.camera.call_method1(py, "move", (self.dx, self.dy))?;
        }

        self.game_state.call_method0(py, "step")?;
        Ok(())
    }

    pub fn event(&mut self, _py: Python, _ctx: &mut Context, event: Event) -> PyResult<Transition> {
        if let Event::MouseMotion{x, y, ..} = event {
            self.dx = if x < 10.0 { -5 } else if x > WIDTH - 10.0 { 5 } else { 0 };
            self.dy = if y < 10.0 { -5 } else if y > HEIGHT - 10.0 { 5 } else { 0 };
        }

        Ok(Transition::None)
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context) -> PyResult<()> {
        let (x, y): (f32, f32) = dbg!(self.camera.call_method0(py, "get_transform")?.extract(py)?);
        let transform = Matrix4::new_translation(&Vector3::<f32>::new(x, y, 0.0));

        ggez::graphics::set_transform(ctx, transform);
        ggez::graphics::apply_transformations(ctx).map_err(PyGgezError::from)?;

        let mut map_renderer = self.map_renderer.extract::<PyRefMut<MapRenderer>>(py)?;

        map_renderer.draw(ctx).map_err(PyGgezError::from)?;

        Ok(())
    }
}