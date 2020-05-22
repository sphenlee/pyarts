use ggez::{graphics, Context, ContextBuilder, GameResult};
use ggez::event::{self, EventHandler};
use pyo3::prelude::*;
use crate::util::PyGgezError;

pub mod mainmenu;
pub mod gamescreen;

pub const WIDTH: f32 = 800.0;
pub const HEIGHT: f32 = 600.0;

pub enum Transition {
    None,
    Next(Box<dyn Screen>),
    Prev,
}

pub enum Event {
    KeyUp(event::KeyCode, event::KeyMods),
    MouseMotion {
        x: f32,
        y: f32,
        dx: f32,
        dy: f32,
    },
}

pub trait Screen {
    fn update<'p>(&mut self, py: Python<'p>, ctx: &mut Context) -> PyResult<()>;

    fn event<'p>(&mut self, py: Python<'p>, ctx: &mut Context, event: Event) -> PyResult<Transition>;

    fn draw<'p>(&mut self, py: Python<'p>, ctx: &mut Context) -> PyResult<()>;
}

pub fn launch(py: Python<'_>) -> PyResult<()> {
    let cwd = std::env::current_dir().unwrap();

    let (mut ctx, mut event_loop) = ContextBuilder::new("yarts", "Steve Lee")
        .window_setup(ggez::conf::WindowSetup {
            title: "Pyarts".to_owned(),
            ..Default::default()
        })
        .add_resource_path(&cwd)
        /*.window_mode(WindowMode {
            maximized: true,
            resizable: true,
            fullscreen_type: FullscreenType::Desktop,
            ..Default::default()
        })*/
        .with_conf_file(true)
        .build()
        .map_err(PyGgezError::from)?;

    //ggez::filesystem::mount(&mut ctx, &cwd, true);

    let mut screens = ScreenStack::new(py);

    screens.screens.push(mainmenu::MainMenu::new());

    match event::run(&mut ctx, &mut event_loop, &mut screens) {
        Ok(_) => println!("Exited cleanly."),
        Err(e) => println!("Error occurred: {}", e)
    }

    Ok(())
}

struct ScreenStack<'p> {
    py: Python<'p>,
    screens: Vec<Box<dyn Screen>>,
}

impl<'p> ScreenStack<'p> {
    fn new(py: Python<'p>) -> Self {
        Self {
            py,
            screens: Vec::new(),
        }
    }

    fn transition(&mut self, transition: Transition) {
        match transition {
            Transition::None => (),
            Transition::Next(next) => {
                self.screens.push(next);
            },
            Transition::Prev => {
                self.screens.pop();
            }
        };
    }
}

fn python_protect<F, R>(py: Python, ctx: &mut Context, mut f: F) -> Option<R>
    where F: FnMut(Python, &mut Context) -> PyResult<R>
{
    match f(py, ctx) {
        Ok(r) => Some(r),
        Err(err) => {
            event::quit(ctx);
            err.print(py);
            None
        }
    }
}

impl EventHandler for ScreenStack<'_> {
    fn update(&mut self, ctx: &mut Context) -> GameResult<()> {
        let screen = self.screens.last_mut().expect("popped last screen?");

        python_protect(self.py, ctx, |py, ctx| {
            screen.update(py, ctx)?;
            Ok(())
        });

        Ok(())
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        graphics::clear(ctx, graphics::BLACK);

        python_protect(self.py, ctx, |py, ctx| {
            let screen = self.screens.last_mut().expect("popped last screen?");
            screen.draw(py, ctx)?;
            Ok(())
        });

        graphics::present(ctx)?;

        Ok(())
    }

    fn mouse_motion_event(&mut self, ctx: &mut Context, x: f32, y: f32, dx: f32, dy: f32) {
        python_protect(self.py, ctx, |py, ctx| {
            let screen = self.screens.last_mut().expect("popped last screen?");
            let transition = screen.event(py, ctx, Event::MouseMotion{x, y, dx, dy})?;
            self.transition(transition);
            Ok(())
        });
    }

    fn key_up_event(&mut self, ctx: &mut Context, keycode: event::KeyCode, keymods: event::KeyMods) {
        if keycode == event::KeyCode::Escape {
            event::quit(ctx);
        }

        python_protect(self.py, ctx, |py, ctx| {
            let screen = self.screens.last_mut().expect("popped last screen?");
            let transition = screen.event(py, ctx, Event::KeyUp(keycode, keymods))?;
            self.transition(transition);
            Ok(())
        });
    }
}