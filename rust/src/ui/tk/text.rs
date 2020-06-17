use crate::ui::tk::markup::parse;
use crate::ui::tk::{CommandBuffer, Element, Event, InputState, Rect, TkResult, Widget};
use glyph_brush::{BuiltInLineBreaker, HorizontalAlign, Layout, OwnedVariedSection, VerticalAlign};
use std::sync::mpsc::Sender;

pub struct Text<Msg> {
    text: String,
    bounds: Rect,
    _msg: std::marker::PhantomData<Msg>, // unused type param
}

impl<Msg: 'static> Text<Msg> {
    pub fn new(text: &str) -> Self {
        Text {
            text: text.to_owned(),
            bounds: Rect::zero(),
            _msg: std::marker::PhantomData,
        }
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg> Widget<Msg> for Text<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        self.bounds = bounds;
        Ok(())
    }

    fn render(&self, _input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        let section = parse(&self.text)?;

        let sec = OwnedVariedSection {
            text: section,
            bounds: (
                self.bounds.size.width as f32,
                self.bounds.size.height as f32,
            ),
            screen_position: (self.bounds.origin.x as f32, self.bounds.origin.y as f32),
            layout: Layout::Wrap {
                line_breaker: BuiltInLineBreaker::UnicodeLineBreaker,
                h_align: HorizontalAlign::Left,
                v_align: VerticalAlign::Top,
            },
            ..OwnedVariedSection::default()
        };

        buffer.text(sec);

        Ok(())
    }

    fn event(&self, _event: &Event, _tx: &Sender<Msg>) -> TkResult<()> {
        Ok(())
    }
}
