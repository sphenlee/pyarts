use crate::ui::tk::{
    rect, CommandBuffer, Element, Event, Icon, InputState, MouseButton, Rect, Texture, TkError,
    TkResult, Widget,
};
use glyph_brush::rusttype::Scale;
use glyph_brush::{
    BuiltInLineBreaker, FontId, HorizontalAlign, Layout, OwnedSectionText, OwnedVariedSection,
    VerticalAlign,
};
use std::sync::mpsc::Sender;

const BUTTON_OFFSET_X: i32 = 0;
const BUTTON_OFFSET_Y: i32 = 0;
const BUTTON_WIDTH: i32 = 64;
const BUTTON_HEIGHT: i32 = 64;

pub struct Button<Msg: Clone> {
    text: String,
    onclick: Option<Msg>,
    bounds: Rect,
    icon: Option<Icon>,
    popup: Option<Element<Msg>>,
    enabled: bool,
}

impl<Msg: Clone + 'static> Button<Msg> {
    pub fn new() -> Self {
        Button {
            text: String::new(),
            onclick: None,
            bounds: Rect::default(),
            icon: None,
            popup: None,
            enabled: true,
        }
    }

    pub fn text(mut self, text: &str) -> Self {
        self.text = text.to_owned();
        self
    }

    pub fn icon(mut self, icon: Icon) -> Self {
        self.icon = Some(icon);
        self
    }

    pub fn popup(mut self, popup: impl Widget<Msg> + 'static) -> Self {
        self.popup = Some(Box::new(popup));
        self
    }

    pub fn onclick(mut self, msg: Msg) -> Self {
        self.onclick = Some(msg);
        self
    }

    pub fn enabled(mut self, enabled: bool) -> Self {
        self.enabled = enabled;
        self
    }


    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg: Clone + 'static> Widget<Msg> for Button<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        self.bounds = bounds;
        if let Some(popup) = &mut self.popup {
            popup.layout(bounds)?;
        }
        Ok(())
    }

    fn render(&self, input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        let uv = if self.enabled {
            if self.bounds.contains(input.mouse_pos) {
                if input.mouse_button == MouseButton::Left {
                    rect(
                        BUTTON_OFFSET_X + BUTTON_WIDTH * 2,
                        BUTTON_OFFSET_Y,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT,
                    )
                } else {
                    rect(
                        BUTTON_OFFSET_X + BUTTON_WIDTH,
                        BUTTON_OFFSET_Y,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT,
                    )
                }
            } else {
                rect(
                    BUTTON_OFFSET_X,
                    BUTTON_OFFSET_Y,
                    BUTTON_WIDTH,
                    BUTTON_HEIGHT,
                )
            }
        } else {
            rect(
                BUTTON_OFFSET_X + BUTTON_WIDTH * 3,
                BUTTON_OFFSET_Y,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
            )
        };

        for s in Texture::from_id(0).icon(uv).nine_square(self.bounds) {
            buffer.sprite(s);
        }

        if let Some(icon) = self.icon {
            let sprite = icon.at(self.bounds.inflate(-8, -8));
            buffer.sprite(sprite);
        }

        if !self.text.is_empty() {
            //self.bounds.origin.x as f32, self.bounds.origin.y as f32
            let pos = self.bounds.center().to_tuple();

            let sec = OwnedVariedSection {
                text: vec![OwnedSectionText {
                    text: self.text.clone(),
                    color: [1.0, 1.0, 1.0, 1.0],
                    font_id: FontId(1),
                    scale: Scale::uniform(24.0),
                    ..OwnedSectionText::default()
                }],
                bounds: (
                    self.bounds.size.width as f32,
                    self.bounds.size.height as f32,
                ),
                screen_position: (pos.0 as f32, pos.1 as f32),
                layout: Layout::SingleLine {
                    line_breaker: BuiltInLineBreaker::AnyCharLineBreaker,
                    h_align: HorizontalAlign::Center,
                    v_align: VerticalAlign::Center,
                },
                ..OwnedVariedSection::default()
            };

            buffer.text(sec);
        }

        if let Some(popup) = &self.popup {
            if self.bounds.contains(input.mouse_pos) {
                popup.render(input, buffer)?;
            }
        }

        Ok(())
    }

    fn event(&self, event: &Event, tx: &Sender<Msg>) -> TkResult<()> {
        if let &Event::Click(pos, button) = event {
            if button == MouseButton::Left && self.bounds.contains(pos) {
                if let Some(onclick) = self.onclick.clone() {
                    log::trace!("mouse button event {:?} {:?}", pos, button);
                    tx.send(onclick).map_err(|_| TkError::SendError)?;
                }
            }
        }
        Ok(())
    }
}
