use crate::root::Root;
use crate::scene::{Event, Screen, Transition, WIDTH, HEIGHT};
use crate::util::YartsResult;
use ggez::{timer, Context};
use pyo3::prelude::*;
use pyo3::{PyObject, PyResult, Python};
use std::collections::HashMap;

pub struct GameScene {
    root: PyObject,
}

fn construct_root(py: Python, ctx: &mut Context) -> PyResult<PyObject> {
    let pyarts = py.import("pyarts")?;
    let construct: PyObject = pyarts.get("construct")?.into();

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
    pub fn new(py: Python, ctx: &mut Context) -> PyResult<Box<dyn Screen>> {
        let root = construct_root(py, ctx)?;

        Ok(Box::new(Self { root }))
    }
}

impl Screen for GameScene {
    fn update(&mut self, py: Python<'_>, ctx: &mut Context) -> YartsResult<()> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        while timer::check_update_time(ctx, 60) {
            root.update(py)?;
        }

        timer::yield_now();

        Ok(())
    }

    fn event(
        &mut self,
        py: Python<'_>,
        ctx: &mut Context,
        event: Event,
    ) -> YartsResult<Transition> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        root.event(py, ctx, event)
    }

    fn draw(&mut self, py: Python<'_>, ctx: &mut Context) -> YartsResult<()> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        root.draw(py, ctx)?;

        Ok(())
    }
}
