use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::map::renderer::MapRenderer;
use crate::scene::{Event, Transition, HEIGHT, WIDTH};
use crate::sprites::SpriteManager;
use crate::ui::game_log::GameLog;
use crate::ui::game_ui::{GameMsg, GameUi};
use crate::ui::ggez_renderer::GgezRenderer;
use crate::util::YartsResult;
use ggez::event::MouseButton;
use ggez::graphics::{self, Color, DrawMode, DrawParam, Rect};
use ggez::Context;
use std::collections::HashMap;

#[pyclass]
pub struct Root {
    map_renderer: PyObject,
    camera: PyObject,
    game_state: PyObject,
    sprite_manager: PyObject,
    control: PyObject,
    game_ui: PyObject,
    game_log: PyObject,
    deps: PyObject,

    // for tracking camera movement - move somewhere else?
    dx: i32,
    dy: i32,

    // for tracking the dragbox - move somewhere else
    click: Option<(f32, f32)>,
    drag: Option<(f32, f32)>,
}

#[pymethods]
impl Root {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec![
            "settings",
            "datasrc",
            "map",
            "game",
            "gamestate",
            "maprenderer",
            "camera",
            "spritemanager",
            "control",
            "gameui",
            "gamelog",
        ]
    }

    #[new]
    fn new(py: Python<'_>) -> Self {
        Root {
            map_renderer: py.None(),
            camera: py.None(),
            game_state: py.None(),
            sprite_manager: py.None(),
            control: py.None(),
            game_ui: py.None(),
            game_log: py.None(),
            deps: py.None(),

            dx: 0,
            dy: 0,

            click: None,
            drag: None,
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        self.map_renderer = deps.get_item("maprenderer")?.into();
        self.camera = deps.get_item("camera")?.into();
        self.game_state = deps.get_item("gamestate")?.into();
        self.sprite_manager = deps.get_item("spritemanager")?.into();
        self.control = deps.get_item("control")?.into();
        self.game_ui = deps.get_item("gameui")?.into();
        self.game_log = deps.get_item("gamelog")?.into();
        self.deps = deps.into();

        Ok(())
    }
}

impl Root {
    pub fn load(&mut self, py: Python, settings: HashMap<String, String>) -> PyResult<()> {
        self.deps
            .as_ref(py)
            .get_item("settings")?
            .call_method1("load", (settings,))?;

        Ok(())
    }

    pub fn update(&mut self, py: Python) -> YartsResult<()> {
        if self.dx != 0 || self.dy != 0 {
            self.camera.call_method1(py, "move", (self.dx, self.dy))?;
        }

        self.game_state.call_method0(py, "step")?;

        let mut game_ui = self.game_ui.extract::<PyRefMut<GameUi>>(py)?;
        game_ui.step(py)?;

        for msg in game_ui.messages() {
            log::debug!("game message: {:?}", msg);
            match msg {
                GameMsg::AbilityButton(num) => self.ability_button(py, num)?,
            }
        }

        Ok(())
    }

    fn ability_button(&self, py: Python, num: usize) -> YartsResult<()> {
        self.control
            .call_method1(py, "ability_button", (num, false))?;
        Ok(())
    }

    pub fn event(
        &mut self,
        py: Python,
        _ctx: &mut Context,
        event: Event,
    ) -> YartsResult<Transition> {
        match event {
            Event::MouseMotion { x, y, .. } => {
                self.dx = 5 * if x < 10.0 {
                    -1
                } else if x > WIDTH - 10.0 {
                    1
                } else {
                    0
                };
                self.dy = 5 * if y < 10.0 {
                    -1
                } else if y > HEIGHT - 10.0 {
                    1
                } else {
                    0
                };

                if let Some(ref mut drag) = self.drag {
                    drag.0 = x;
                    drag.1 = y;
                }

                self.control.call_method1(py, "mouse_move", (x, y))?;
            }
            Event::KeyUp(..) => {}
            Event::KeyDown(..) => {}
            Event::TextInput(c) => {
                if c >= '1' && c < '9' {
                    let num = c as usize - '1' as usize;
                    self.ability_button(py, num)?;
                }
            }
            Event::MouseDown { x, y, button } => match button {
                MouseButton::Left => {
                    self.click = Some((x, y));
                    self.drag = Some((x, y));
                }
                _ => {}
            },
            Event::MouseUp { x, y, button } => match button {
                MouseButton::Left => {
                    if let (Some((x1, y1)), Some((x2, y2))) = (self.click, self.drag) {
                        if x1 == x2 && y1 == y2 {
                            self.control.call_method1(py, "left_click", (x, y, false))?;
                        } else {
                            self.control.call_method1(
                                py,
                                "left_click_box",
                                (x1, y1, x2, y2, false),
                            )?;
                        }

                        self.click = None;
                        self.drag = None;
                    }
                }
                MouseButton::Right => {
                    self.control
                        .call_method1(py, "right_click", (x, y, false))?;
                }
                _ => {}
            },
        }

        Ok(Transition::None)
    }

    pub fn draw(
        &mut self,
        py: Python,
        ctx: &mut Context,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<()> {
        let offset: (f32, f32) = self.camera.call_method0(py, "get_transform")?.extract(py)?;

        let mut map_renderer = self.map_renderer.extract::<PyRefMut<MapRenderer>>(py)?;
        map_renderer.draw(py, ctx, offset)?;

        let mut sprite_manager = self.sprite_manager.extract::<PyRefMut<SpriteManager>>(py)?;
        sprite_manager.draw(py, ctx, offset)?;

        if let (Some((x1, y1)), Some((x2, y2))) = (self.click, self.drag) {
            let rect = graphics::Mesh::new_rectangle(
                ctx,
                DrawMode::stroke(2.0),
                Rect::new(x1, y1, x2 - x1, y2 - y1),
                Color::from_rgb(0xFF, 0xFF, 0x00),
            )?;

            graphics::draw(ctx, &rect, DrawParam::new())?;
        }

        let mut game_ui = self.game_ui.extract::<PyRefMut<GameUi>>(py)?;
        game_ui.draw(py, ctx, ggez_rend, offset)?;

        let mut game_log = self.game_log.extract::<PyRefMut<GameLog>>(py)?;
        game_log.draw(ctx, ggez_rend)?;

        graphics::draw_queued_text(
            ctx,
            DrawParam::default(),
            None,
            graphics::FilterMode::Nearest,
        )?;
        Ok(())
    }
}
