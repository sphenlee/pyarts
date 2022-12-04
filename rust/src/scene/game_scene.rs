use crate::root::Root;
use crate::scene::{Event, Screen, Transition, HEIGHT, WIDTH};
use crate::ui::ggez_renderer::GgezRenderer;
use crate::util::YartsResult;
use ggez::Context;
use pyo3::prelude::*;
use pyo3::{PyObject, PyResult, Python};
use std::collections::HashMap;
use ggez::graphics::Canvas;

pub struct GameScene {
    root: PyObject,
    ggez_rend: GgezRenderer,
}

fn construct_root(py: Python, _ctx: &mut Context) -> PyResult<PyObject> {
    let pyarts = py.import("pyarts")?;
    let construct: PyObject = pyarts.getattr("construct")?.into();

    let mut settings = HashMap::<String, String>::new();

    settings.insert("width".to_owned(), WIDTH.to_string());
    settings.insert("height".to_owned(), HEIGHT.to_string());

    let pyroot = construct.call1(py, ("root",))?;

    {
        let mut root = pyroot.as_ref(py).extract::<PyRefMut<Root>>()?;
        root.load(py, settings)?;
    }

    Ok(pyroot)
}

impl GameScene {
    pub fn new(py: Python, ctx: &mut Context) -> YartsResult<Box<dyn Screen>> {
        let root = construct_root(py, ctx)?;
        let ggez_rend = GgezRenderer::new(ctx)?;

        Ok(Box::new(Self { root, ggez_rend }))
    }
}

impl Screen for GameScene {
    fn update(&mut self, py: Python<'_>, _ctx: &mut Context) -> YartsResult<()> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;
        root.update(py)?;
        Ok(())
    }

    fn event(
        &mut self,
        py: Python<'_>,
        ctx: &mut Context,
        event: Event,
    ) -> YartsResult<Transition> {
        self.ggez_rend.event(event.clone());

        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;
        root.event(py, ctx, event)
    }

    fn draw(&mut self, py: Python<'_>, ctx: &mut Context, canvas: &mut Canvas) -> YartsResult<Transition> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        root.draw(py, ctx, canvas, &mut self.ggez_rend)?;

        Ok(Transition::None)
    }
}
