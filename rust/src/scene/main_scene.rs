use crate::scene::game_scene::GameScene;
use crate::scene::{Event, Screen, Transition};
use crate::util::YartsResult;
use ggez::graphics::DrawParam;
use ggez::{event, graphics, Context};
use pyo3::prelude::*;

pub struct MainScene {
    text: graphics::Text,
}

impl MainScene {
    pub fn new() -> Box<dyn Screen> {
        Box::new(Self {
            text: graphics::Text::new("Press S to Start!"),
        })
    }
}

impl Screen for MainScene {
    fn update(&mut self, _py: Python<'_>, _ctx: &mut Context) -> YartsResult<()> {
        Ok(())
    }

    fn event(
        &mut self,
        py: Python<'_>,
        ctx: &mut Context,
        event: Event,
    ) -> YartsResult<Transition> {
        if let Event::KeyUp(event::KeyCode::S, _) = event {
            let game_ui = GameScene::new(py, ctx)?;
            Ok(Transition::Next(game_ui))
        } else {
            Ok(Transition::None)
        }
    }

    fn draw(&mut self, _py: Python<'_>, ctx: &mut Context) -> YartsResult<()> {
        graphics::draw(ctx, &self.text, DrawParam::new().dest([100.0, 100.0]))?;
        Ok(())
    }
}