use crate::scene::game_scene::GameScene;
use crate::scene::{Event, Screen, Transition, HEIGHT, WIDTH};
use crate::ui::ggez_renderer::GgezRenderer;
use crate::ui::tk::*;
use crate::util::YartsResult;
use ggez::graphics::{Canvas};
use ggez::{Context, GameResult, input};
use log::warn;
use pyo3::prelude::*;

#[derive(Clone)]
enum Msg {
    StartGame,
}

pub struct MainScene {
    ggez_rend: GgezRenderer,
}

const WELCOME_MSG: &str = r##"\
# Welcome to Pyarts #

Click on *"Start Game"* to begin a new game.

This is just a test for the popup component ;)
"##;

impl MainScene {
    pub fn new(ctx: &mut Context) -> GameResult<Box<dyn Screen>> {
        Ok(Box::new(Self {
            ggez_rend: GgezRenderer::new(ctx)?,
        }))
    }

    fn build(&self) -> TkResult<Element<Msg>> {
        let panel = Panel::vbox()
            .add(
                Button::new()
                    .text("Start Game")
                    .onclick(Msg::StartGame)
                    .popup(
                        Popup::new()
                            .anchor(Point::new(WIDTH as i32 - 300, HEIGHT as i32 - 400))
                            .size(Size::new(300, 400))
                            .add(Border::new(Text::new("Start a new game")?)),
                    ),
            )
            .add(Button::new().text("Join Game"))
            .add(Button::new().text("Exit"))
            .add_flex(
                0,
                Popup::new()
                    .anchor(Point::new(1000, 100))
                    .size(Size::new(300, 300))
                    .add(Border::new(Text::new(WELCOME_MSG)?)),
            );

        Ok(panel.build())
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
        self.ggez_rend.event(event.clone());

        // TODO - add hotkeys to buttons to reduce duplication
        if let Event::KeyUp(input::keyboard::KeyCode::S, _) = event {
            let game_ui = GameScene::new(py, ctx)?;
            Ok(Transition::Next(game_ui))
        } else {
            Ok(Transition::None)
        }
    }

    fn draw(&mut self, py: Python<'_>, ctx: &mut Context, canvas: &mut Canvas) -> YartsResult<Transition> {
        let mut transition = Transition::None;

        let root = self.build()?;

        let bounds = rect(860, 508, 200, 64 * 3);
        for msg in self.ggez_rend.render(ctx, canvas, root, bounds)? {
            match msg {
                Msg::StartGame => {
                    warn!("START GAME!");
                    let game_ui = GameScene::new(py, ctx)?;
                    transition = Transition::Next(game_ui);
                }
            }
        }

        Ok(transition)
    }
}
