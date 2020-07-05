use crate::scene::HEIGHT;
use crate::ui::ggez_renderer::GgezRenderer;
use ggez::{graphics, Context, GameResult};
use glyph_brush::rusttype::Scale;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::time::{Duration, Instant};

const LOG_Y_POS: f32 = HEIGHT / 4.0 * 3.0 - 24.0; // fudge factor - approx the height of one line

struct Line {
    msg: String,
    created: Instant,
}

#[pyclass]
pub struct GameLog {
    lines: Vec<Line>,
}

#[pymethods]
impl GameLog {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec![]
    }

    #[new]
    fn new(_py: Python) -> GameLog {
        GameLog { lines: vec![] }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, _kwargs: Option<&PyDict>) -> PyResult<()> {
        Ok(())
    }

    fn log(&mut self, msg: String) -> PyResult<()> {
        self.lines.push(Line {
            msg,
            created: Instant::now(),
        });
        Ok(())
    }
}

impl GameLog {
    pub fn draw(&mut self, ctx: &mut Context, ggez_rend: &GgezRenderer) -> GameResult<()> {
        let now = Instant::now();
        let timeout = now - Duration::from_secs(15);

        self.lines.retain(|line| line.created > timeout);

        let mut y = LOG_Y_POS;
        for line in self.lines.iter().rev() {
            let age = now.duration_since(line.created);
            let fade = if age < Duration::from_secs(10) {
                1.0
            } else {
                1.0 - (age.as_secs_f32() - 10.0) / 5.0
            };

            let mut text = graphics::Text::new(line.msg.as_ref());
            text.set_font(ggez_rend.font, Scale::uniform(18.0));

            graphics::queue_text(
                ctx,
                &text,
                [0.0, y],
                Some(graphics::Color::new(1.0, 1.0, 0.0, fade)),
            );

            y -= text.height(ctx) as f32;
        }

        Ok(())
    }
}
