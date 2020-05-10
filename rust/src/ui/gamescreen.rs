use crate::ui::{Screen, Transition, Event};
use ggez::{graphics, Context, GameResult, event};
use ggez::graphics::DrawParam;
use pyo3::{Python, PyObject, PyResult};
use std::sync::Arc;
use crate::ui::camera::Camera;

pub struct GameScreen {
    text: graphics::Text,
    root: PyObject,
    camera: Camera,
}

fn construct_root(py: Python<'_>) -> PyResult<PyObject> {
    let pyarts = py.import("pyarts")?;
    let construct: PyObject = pyarts.get("construct")?.into();

    let root = construct.call1(py, ("root",))?;

    root.call_method1(py, "load", ())
        .map_err(|e| {
            e.print(py);
        }).expect("error in load");

    Ok(root)
}

impl GameScreen {
    pub fn new(py: Python<'_>) -> Box<dyn Screen> {
        let root = construct_root(py).expect("failed to construct root");

        Box::new(Self {
            text: graphics::Text::new("In Game!"),
            root,
            camera: Camera::new(),
        })
    }
}


impl Screen for GameScreen {
    fn update(&mut self, py: Python<'_>, _ctx: &mut Context) {
        self.root.call_method1(py, "update", ())
            .map_err(|e| {
                e.print(py);
            }).expect("error in update");
    }

    fn event(&mut self, py: Python<'_>, ctx: &mut Context, event: Event) -> Transition {
        Transition::None
    }

    fn draw(&mut self, py: Python<'_>, ctx: &mut Context) -> GameResult<()> {
        graphics::draw(ctx, &self.text, DrawParam::new().dest([100.0, 100.0]))?;
        Ok(())
    }
}