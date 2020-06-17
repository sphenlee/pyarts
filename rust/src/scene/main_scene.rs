use crate::scene::game_scene::GameScene;
use crate::scene::{Event, Screen, Transition};
use crate::ui::demo::{Demo, DemoMsg};
use crate::util::YartsResult;
use ggez::graphics::{DrawParam, FilterMode};
use ggez::{event, graphics, Context, GameResult};
use log::info;
use pyo3::prelude::*;

pub struct MainScene {
    text: graphics::Text,
    demo: Demo,
}

impl MainScene {
    pub fn new(ctx: &mut Context) -> GameResult<Box<dyn Screen>> {
        Ok(Box::new(Self {
            text: graphics::Text::new("Press S to Start!"),
            demo: Demo::new(ctx)?,
        }))
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
        self.demo.event(&event);

        if let Event::KeyUp(event::KeyCode::S, _) = event {
            let game_ui = GameScene::new(py, ctx)?;
            Ok(Transition::Next(game_ui))
        } else {
            Ok(Transition::None)
        }
    }

    fn draw(&mut self, _py: Python<'_>, ctx: &mut Context) -> YartsResult<()> {
        graphics::draw(ctx, &self.text, DrawParam::new().dest([100.0, 100.0]))?;

        for msg in self.demo.render(ctx)? {
            match msg {
                DemoMsg::Button1Click => {
                    info!("button 1 clicked!");
                }
                DemoMsg::Button2Click => {
                    info!("button 2 clicked!");
                }
                DemoMsg::AbilityButton(n) => {
                    info!("ability {}", n);
                }
            }
        }
        graphics::draw_queued_text(ctx, DrawParam::default(), None, FilterMode::Nearest)?;

        Ok(())
    }
}
