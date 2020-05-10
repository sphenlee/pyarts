use crate::ui::{Screen, Transition, Event};
use ggez::{graphics, Context, GameResult, event};
use ggez::graphics::DrawParam;
use pyo3::Python;
use crate::ui::gamescreen::GameScreen;

pub struct MainMenu {
    text: graphics::Text,
}

impl MainMenu {
    pub fn new() -> Box<dyn Screen> {
        Box::new(Self {
            text: graphics::Text::new("Press S to Start!"),
        })
    }
}


impl Screen for MainMenu {
    fn update(&mut self, py: Python<'_>, _ctx: &mut Context) {
    }

    fn event(&mut self, py: Python<'_>, ctx: &mut Context, event: Event) -> Transition {
        if keycode == event::KeyCode::S {
            let game_ui = GameScreen::new(py);
            Transition::Next(game_ui)
        } else {
            Transition::None
        }
    }

    fn draw(&mut self, py: Python<'_>, ctx: &mut Context) -> GameResult<()> {
        graphics::draw(ctx, &self.text, DrawParam::new().dest([100.0, 100.0]))?;
        Ok(())
    }
}