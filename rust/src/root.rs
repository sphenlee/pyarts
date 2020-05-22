use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::map::renderer::MapRenderer;
use ggez::Context;
use crate::ui::{WIDTH, HEIGHT, Event, Transition};
use crate::util::PyGgezError;
use crate::sprites::SpriteManager;
use ggez::graphics::DrawParam;

#[pyclass]
pub struct Root {
    map_renderer: PyObject,
    camera: PyObject,
    game_state: PyObject,
    sprite_manager: PyObject,
    deps: PyObject,

    // for tracking camera movement - move somewhere else?
    dx: i32,
    dy: i32,
}

#[pymethods]
impl Root {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["settings", "datasrc", "map", "game", "gamestate", "maprenderer", "camera", "spritemanager"]
    }

    #[new]
    fn new(py: Python<'_>) -> Self {
        Root {
            map_renderer: py.None(),
            camera: py.None(),
            game_state: py.None(),
            sprite_manager: py.None(),
            deps: py.None(),

            dx: 0,
            dy: 0,
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        self.map_renderer = deps.get_item("maprenderer")?.into();
        self.camera = deps.get_item("camera")?.into();
        self.game_state = deps.get_item("gamestate")?.into();
        self.sprite_manager = deps.get_item("spritemanager")?.into();
        self.deps = deps.into();

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
            self.dx = if x < 10.0 { -1 } else if x > WIDTH - 10.0 { 1 } else { 0 };
            self.dy = if y < 10.0 { -1 } else if y > HEIGHT - 10.0 { 1 } else { 0 };
        }

        Ok(Transition::None)
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context) -> PyResult<()> {
        let (x, y): (f32, f32) = self.camera.call_method0(py, "get_transform")?.extract(py)?;

        let transform = DrawParam::new()
            .dest([x, y])
            .to_matrix();

        ggez::graphics::set_transform(ctx, transform);
        ggez::graphics::apply_transformations(ctx).map_err(PyGgezError::from)?;

        let mut map_renderer = self.map_renderer.extract::<PyRefMut<MapRenderer>>(py)?;
        map_renderer.draw(py, ctx).map_err(PyGgezError::from)?;

        let mut sprite_manager = self.sprite_manager.extract::<PyRefMut<SpriteManager>>(py)?;
        sprite_manager.draw(py, ctx).map_err(PyGgezError::from)?;


        Ok(())
    }
}