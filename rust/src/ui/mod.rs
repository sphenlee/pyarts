use ggez::{graphics, Context, ContextBuilder, GameResult};
use ggez::event::{self, EventHandler};
use pyo3::prelude::*;

pub mod mainmenu;
pub mod gamescreen;

enum Transition {
    None,
    Next(Box<dyn Screen>),
    Prev,
}

pub trait Screen {
    fn update(&mut self, py: Python<'_>) -> GameResult<Transition>;

    fn key_up_event(&mut self,
                    py: Python<'_>,
                    keycode: event::KeyCode,
                    keymods: event::KeyMods
    ) -> GameResult<Transition> {
        Ok(Transition::None)
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()>;
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
    fn update(&mut self, _ctx: &mut Context) -> GameResult<()> {
        let screen = self.screens.last_mut().expect("popped last screen?");

        let transition = screen.update(self.py)?;
        self.transition(transition);

        Ok(())
    }

    fn key_up_event(&mut self, ctx: &mut Context, keycode: event::KeyCode, keymods: event::KeyMods) {
        if keycode == event::KeyCode::Escape {
            event::quit(ctx);
        }

        let screen = self.screens.last_mut().expect("popped last screen?");
        let transition = screen.key_up_event(self.py, keycode, keymods).expect("error in key_up_event");
        self.transition(transition);
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        graphics::clear(ctx, graphics::BLACK);

        let screen = self.screens.last_mut().expect("popped last screen?");
        screen.draw(ctx)?;

        graphics::present(ctx)
    }
}