use crate::ui::tk::markup::parse;
use crate::ui::tk::{CommandBuffer, Element, Event, InputState, Rect, TkResult, Widget};
use glyph_brush::{BuiltInLineBreaker, HorizontalAlign, Layout, OwnedVariedSection, VerticalAlign, OwnedSectionText};
use std::sync::mpsc::Sender;

pub struct Text<Msg> {
    sections: Vec<OwnedSectionText>,
    bounds: Rect,
    halign: HorizontalAlign,
    _msg: std::marker::PhantomData<Msg>, // unused type param
}

impl<Msg: 'static> Text<Msg> {
    pub fn new(text: impl Into<String>) -> TkResult<Self> {

        let sections = parse(&text.into())?;

        Ok(Text {
            sections,
            bounds: Rect::zero(),
            halign: HorizontalAlign::Left,
            _msg: std::marker::PhantomData,
        })
    }

    pub fn align(mut self, halign: HorizontalAlign) -> Self {
        self.halign = halign;
        self
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
        let pos = if self.halign == HorizontalAlign::Center {
            (self.bounds.origin.x as f32 + self.bounds.size.width as f32 / 2.0, self.bounds.origin.y as f32)
        } else {
            (self.bounds.origin.x as f32, self.bounds.origin.y as f32)
        };

        let sec = OwnedVariedSection {
            text: self.sections.clone(),
            bounds: (
                self.bounds.size.width as f32,
                self.bounds.size.height as f32,
            ),
            screen_position: pos,
            layout: Layout::Wrap {
                line_breaker: BuiltInLineBreaker::UnicodeLineBreaker,
                h_align: self.halign,
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
