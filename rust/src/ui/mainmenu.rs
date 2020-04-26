use crate::ui::{Screen, Transition};
use ggez::{graphics, Context, GameResult, GameError, event};
use ggez::graphics::DrawParam;
use pyo3::Python;
use std::sync::Arc;

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
    fn update(&mut self, py: Python<'_>) -> GameResult<Transition> {
        /*py.run(r"print('in mainmenu update')", None, None)
            .map_err(|e| {
                //e.print(py);
                GameError::IOError(Arc::new(std::io::Error::from(e)))
            })?;
*/
        Ok(Transition::None)
    }

    fn key_up_event(&mut self,
                    py: Python<'_>,
                    keycode: event::KeyCode,
                    keymods: event::KeyMods
    ) -> GameResult<Transition> {
        if keycode == event::KeyCode::S {
            let game_ui =

            Ok(Transition::Next())
        }
    }

    fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        graphics::draw(ctx, &self.text, DrawParam::new().dest([100.0, 100.0]))?;
        Ok(())
    }
}