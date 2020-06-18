use crate::ui::tk::{
    rect, CommandBuffer, Element, Event, InputState, Rect, TextureId, TkResult, Widget,
};
use glyph_brush::rusttype::Scale;
use glyph_brush::{
    BuiltInLineBreaker, FontId, HorizontalAlign, Layout, OwnedSectionText, OwnedVariedSection,
    VerticalAlign,
};
use std::sync::mpsc::Sender;

const PROGRESS_OFFSET_X: i32 = 0;
const PROGRESS_OFFSET_Y: i32 = 192;
const PROGRESS_WIDTH: i32 = 192;
const PROGRESS_HEIGHT: i32 = 32;

pub struct Progress<Msg> {
    text: String,
    percentage: f32,
    bounds: Rect,
    phantom: std::marker::PhantomData<Msg>,
}

impl<Msg: 'static> Progress<Msg> {
    pub fn new() -> Self {
        Progress {
            text: String::new(),
            percentage: 0.0,
            bounds: Rect::default(),
            phantom: std::marker::PhantomData,
        }
    }

    pub fn text(mut self, text: impl Into<String>) -> Self {
        self.text = text.into();
        self
    }

    pub fn percentage(mut self, percentage: f32) -> Self {
        // TODO - better name? it's not out of 100
        self.percentage = percentage;
        self
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg: 'static> Widget<Msg> for Progress<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        self.bounds = bounds;
        Ok(())
    }

    fn render(&self, _input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        let uv_bar = rect(
            PROGRESS_OFFSET_X,
            PROGRESS_OFFSET_Y + PROGRESS_HEIGHT,
            PROGRESS_WIDTH,
            PROGRESS_HEIGHT,
        );
        let uv_fill = rect(
            PROGRESS_OFFSET_X,
            PROGRESS_OFFSET_Y,
            PROGRESS_WIDTH,
            PROGRESS_HEIGHT,
        );

        let offset_y = (self.bounds.size.height - PROGRESS_HEIGHT) / 2;

        let bar = rect(
            self.bounds.origin.x,
            self.bounds.origin.y + offset_y,
            self.bounds.size.width,
            PROGRESS_HEIGHT,
        );
        let fill = rect(
            self.bounds.origin.x,
            self.bounds.origin.y + offset_y,
            (self.bounds.size.width as f32 * self.percentage) as i32,
            PROGRESS_HEIGHT,
        );

        for s in TextureId(0).icon(uv_bar).nine_square(bar) {
            buffer.sprite(s);
        }
        for s in TextureId(0).icon(uv_fill).nine_square(fill) {
            buffer.sprite(s);
        }

        if !self.text.is_empty() {
            let pos = self.bounds.center().to_tuple();

            let sec = OwnedVariedSection {
                text: vec![OwnedSectionText {
                    text: self.text.clone(),
                    color: [1.0, 1.0, 1.0, 1.0],
                    font_id: FontId(1),
                    scale: Scale::uniform(18.0),
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

        Ok(())
    }

    fn event(&self, _event: &Event, _tx: &Sender<Msg>) -> TkResult<()> {
        Ok(())
    }
}
