use crate::util::{YartsError, YartsResult};
use ggez::event::{self, EventHandler, MouseButton};
use ggez::{graphics, Context, ContextBuilder, GameResult};
use pyo3::prelude::*;

pub mod game_scene;
pub mod main_scene;
//pub mod tree;

pub const WIDTH: f32 = 800.0; //1920.0;
pub const HEIGHT: f32 = 600.0; //1080.0;

pub enum Transition {
    None,
    Next(Box<dyn Screen>),
    Prev,
}

pub enum Event {
    KeyUp(event::KeyCode, event::KeyMods),
    KeyDown(event::KeyCode, event::KeyMods),
    TextInput(char),
    MouseMotion { x: f32, y: f32, dx: f32, dy: f32 },
    MouseDown { x: f32, y: f32, button: MouseButton },
    MouseUp { x: f32, y: f32, button: MouseButton },
}

pub trait Screen {
    fn update<'p>(&mut self, py: Python<'p>, ctx: &mut Context) -> YartsResult<()>;

    fn event<'p>(
        &mut self,
        py: Python<'p>,
        ctx: &mut Context,
        event: Event,
    ) -> YartsResult<Transition>;

    fn draw<'p>(&mut self, py: Python<'p>, ctx: &mut Context) -> YartsResult<()>;
}

pub fn launch(py: Python<'_>) -> YartsResult<()> {
    let cwd = std::env::current_dir().unwrap();

    let (mut ctx, mut event_loop) = ContextBuilder::new("yarts", "Steve Lee")
        .window_setup(ggez::conf::WindowSetup {
            title: "Pyarts".to_owned(),
            ..Default::default()
        })
        .add_resource_path(&cwd)
        .window_mode(ggez::conf::WindowMode {
            width: WIDTH,
            height: HEIGHT,
            //maximized: true,
            //resizable: true,
            //fullscreen_type: ggez::conf::FullscreenType::Desktop,
            ..Default::default()
        })
        .with_conf_file(true)
        .build()?;

    //ggez::filesystem::mount(&mut ctx, &cwd, true);

    let mut screens = SceneStack::new(py);

    screens.screens.push(main_scene::MainScene::new());

    match event::run(&mut ctx, &mut event_loop, &mut screens) {
        Ok(_) => println!("Exited cleanly."),
        Err(e) => println!("Error occurred: {}", e),
    }

    Ok(())
}

struct SceneStack<'p> {
    py: Python<'p>,
    screens: Vec<Box<dyn Screen>>,
}

impl<'p> SceneStack<'p> {
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
            }
            Transition::Prev => {
                self.screens.pop();
            }
        };
    }

    fn do_event(&mut self, ctx: &mut Context, event: Event) {
        python_protect(self.py, ctx, |py, ctx| {
            let screen = self.screens.last_mut().expect("popped last screen?");
            let transition = screen.event(py, ctx, event)?;
            self.transition(transition);
            Ok(())
        });
    }
}

fn python_protect<F, R>(py: Python, ctx: &mut Context, f: F) -> Option<R>
where
    F: FnOnce(Python, &mut Context) -> YartsResult<R>,
{
    match f(py, ctx) {
        Ok(r) => Some(r),
        Err(err) => {
            event::quit(ctx);
            match err {
                YartsError::GameError(err) => println!("game error: {}", err),
                YartsError::PyErr(pyerr) => {
                    println!("python error:");
                    pyerr.print(py)
                },
                YartsError::Other(err) => println!("other error: {}", err),
            };
            None
        }
    }
}

impl EventHandler for SceneStack<'_> {
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

    fn mouse_button_down_event(&mut self, ctx: &mut Context, button: MouseButton, x: f32, y: f32) {
        self.do_event(ctx, Event::MouseDown { x, y, button });
    }

    fn mouse_button_up_event(&mut self, ctx: &mut Context, button: MouseButton, x: f32, y: f32) {
        self.do_event(ctx, Event::MouseUp { x, y, button });
    }

    fn mouse_motion_event(&mut self, ctx: &mut Context, x: f32, y: f32, dx: f32, dy: f32) {
        self.do_event(ctx, Event::MouseMotion { x, y, dx, dy });
    }

    fn key_down_event(
        &mut self,
        ctx: &mut Context,
        keycode: event::KeyCode,
        keymods: event::KeyMods,
        repeat: bool,
    ) {
        if keycode == event::KeyCode::Escape {
            event::quit(ctx);
        }

        if !repeat {
            self.do_event(ctx, Event::KeyDown(keycode, keymods));
        }
    }

    fn key_up_event(
        &mut self,
        ctx: &mut Context,
        keycode: event::KeyCode,
        keymods: event::KeyMods,
    ) {
        self.do_event(ctx, Event::KeyUp(keycode, keymods));
    }

    fn text_input_event(&mut self, ctx: &mut Context, character: char) {
        self.do_event(ctx, Event::TextInput(character));
    }
}
