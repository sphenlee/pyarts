use crate::ui::{Screen, Transition, Event};
use ggez::Context;
use pyo3::prelude::*;
use pyo3::{Python, PyObject, PyResult};
use crate::root::Root;

pub struct GameScreen {
    root: PyObject,
}

fn construct_root(py: Python<'_>) -> PyResult<PyObject> {
    let pyarts = py.import("pyarts")?;
    let construct: PyObject = pyarts.get("construct")?.into();

    let pyroot = construct.call1(py, ("root",))?;

    {
        let mut root = pyroot.as_ref(py).extract::<PyRefMut<Root>>()?;
        root.load(py)?;
    }

    Ok(pyroot)
}

impl GameScreen {
    pub fn new(py: Python<'_>) -> PyResult<Box<dyn Screen>> {
        let root = construct_root(py)?;

        Ok(Box::new(Self {
            root,
        }))
    }
}


impl Screen for GameScreen {
    fn update(&mut self, py: Python<'_>, _ctx: &mut Context) -> PyResult<()> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        root.update(py)
    }

    fn event(&mut self, py: Python<'_>, ctx: &mut Context, event: Event) -> PyResult<Transition> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        root.event(py, ctx, event)
    }

    fn draw(&mut self, py: Python<'_>, ctx: &mut Context) -> PyResult<()> {
        let mut root = self.root.as_ref(py).extract::<PyRefMut<Root>>()?;

        root.draw(py, ctx)?;

        Ok(())
    }
}