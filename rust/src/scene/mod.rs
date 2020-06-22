use crate::util::{YartsError, YartsResult};
use ggez::event::{self, EventHandler, MouseButton};
use ggez::graphics::Drawable;
use ggez::{graphics, Context, ContextBuilder, GameResult};
use log::{error, info};
use pyo3::prelude::*;
use std::time::Duration;

pub mod game_scene;
pub mod main_scene;
//pub mod tree;

pub const WIDTH: f32 = //800;
    1920.0;
pub const HEIGHT: f32 = //600;
    1080.0;

pub const WIDTH_I: i32 = WIDTH as i32;
pub const HEIGHT_I: i32 = HEIGHT as i32;

pub enum Transition {
    None,
    Next(Box<dyn Screen>),
    Prev,
}

#[derive(Clone, Debug)]
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

    fn draw<'p>(&mut self, py: Python<'p>, ctx: &mut Context) -> YartsResult<Transition>;
}

pub fn launch(py: Python<'_>) -> YartsResult<()> {
    let cwd = std::env::current_dir().unwrap();

    let (mut ctx, mut event_loop) = ContextBuilder::new("yarts", "Steve Lee")
        .window_setup(ggez::conf::WindowSetup {
            title: "Pyarts".to_owned(),
            vsync: true,
            ..Default::default()
        })
        .add_resource_path(&cwd)
        .window_mode(ggez::conf::WindowMode {
            width: WIDTH,
            height: HEIGHT,
            //maximized: true,
            //resizable: true,
            fullscreen_type: ggez::conf::FullscreenType::Desktop,
            ..Default::default()
        })
        .with_conf_file(true)
        .build()?;

    //ggez::filesystem::mount(&mut ctx, &cwd, true);

    let mut screens = SceneStack::new(py);

    screens.screens.push(main_scene::MainScene::new(&mut ctx)?);

    match event::run(&mut ctx, &mut event_loop, &mut screens) {
        Ok(_) => info!("Exited cleanly."),
        Err(e) => error!("Error occurred: {}", e),
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
                YartsError::GameError(err) => error!("game error: {}", err),
                YartsError::PyErr(pyerr) => {
                    error!("python error:");
                    pyerr.print(py)
                }
                YartsError::TkError(tkerr) => error!("tk error: {}", tkerr),
                YartsError::Other(err) => error!("other error: {}", err),
            };
            None
        }
    }
}

impl EventHandler for SceneStack<'_> {
    fn update(&mut self, ctx: &mut Context) -> GameResult<()> {
        let screen = self.screens.last_mut().expect("popped last screen?");

        python_protect(self.py, ctx, |py, ctx| {
            while ggez::timer::check_update_time(ctx, 60) {
                screen.update(py, ctx)?;
            }
            Ok(())
        });

        Ok(())
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        graphics::clear(ctx, graphics::BLACK);

        python_protect(self.py, ctx, |py, ctx| {
            let screen = self.screens.last_mut().expect("popped last screen?");
            let transition = screen.draw(py, ctx)?;
            self.transition(transition);
            Ok(())
        });

        graphics::Text::new(format!("fps: {}", ggez::timer::fps(ctx))).draw(
            ctx,
            graphics::DrawParam::new()
                .dest([20.0, 20.0])
                .color(graphics::Color::new(1.0, 0.0, 0.0, 1.0)),
        )?;

        graphics::present(ctx)?;

        ggez::timer::sleep(Duration::from_millis(5));

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
