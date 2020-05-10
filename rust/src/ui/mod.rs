use ggez::{graphics, Context, ContextBuilder, GameResult};
use ggez::event::{self, EventHandler};
use pyo3::prelude::*;

pub mod camera;
pub mod mainmenu;
pub mod gamescreen;

pub enum Transition {
    None,
    Next(Box<dyn Screen>),
    Prev,
}

pub enum Event {
    KeyUp(event::KeyCode, event::KeyMods),
}

pub trait Screen<'p> {
    fn update(&mut self, py: Python<'p>, ctx: &mut Context);

    fn event(&mut self, py: Python<'p>, ctx: &mut Context, event: Event) -> Transition;

    fn draw(&mut self, py: Python<'p>, ctx: &mut Context) -> GameResult<()>;
}

pub fn launch(py: Python<'_>) -> PyResult<()> {
    let (mut ctx, mut event_loop) = ContextBuilder::new("yarts", "Steve Lee")
        .build()
        .expect("could not create ggez context");

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

impl EventHandler for ScreenStack<'_> {
    fn update(&mut self, ctx: &mut Context) -> GameResult<()> {
        let screen = self.screens.last_mut().expect("popped last screen?");

        screen.update(self.py, ctx);

        Ok(())
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        graphics::clear(ctx, graphics::BLACK);

        let screen = self.screens.last_mut().expect("popped last screen?");
        screen.draw(self.py, ctx)?;

        graphics::present(ctx)
    }

    fn key_up_event(&mut self, ctx: &mut Context, keycode: event::KeyCode, keymods: event::KeyMods) {
        if keycode == event::KeyCode::Escape {
            event::quit(ctx);
        }

        let screen = self.screens.last_mut().expect("popped last screen?");
        let transition = screen.event(self.py, Event::KeyUp(keycode, keymods));
        self.transition(transition);
    }
}