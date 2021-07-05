use crate::ui::tk::markup::parse;
use crate::ui::tk::{CommandBuffer, Element, Event, InputState, Rect, TkResult, Widget};
use glyph_brush::{BuiltInLineBreaker, HorizontalAlign, Layout, OwnedSection, VerticalAlign};
use std::sync::mpsc::Sender;

pub struct Text<Msg> {
    section: OwnedSection,
    bounds: Rect,
    halign: HorizontalAlign,
    valign: VerticalAlign,
    _msg: std::marker::PhantomData<Msg>, // unused type param
}

impl<Msg: 'static> Text<Msg> {
    pub fn new(text: impl Into<String>) -> TkResult<Self> {
        let section = parse(&text.into())?;

        Ok(Text {
            section,
            bounds: Rect::zero(),
            halign: HorizontalAlign::Left,
            valign: VerticalAlign::Top,
            _msg: std::marker::PhantomData,
        })
    }

    pub fn halign(mut self, halign: HorizontalAlign) -> Self {
        self.halign = halign;
        self
    }

    pub fn valign(mut self, valign: VerticalAlign) -> Self {
        self.valign = valign;
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
        let posx = if self.halign == HorizontalAlign::Center {
            self.bounds.origin.x as f32 + self.bounds.size.width as f32 / 2.0
        } else {
            self.bounds.origin.x as f32
        };

        let posy = if self.valign == VerticalAlign::Center {
            self.bounds.origin.y as f32 + self.bounds.size.height as f32 / 2.0
        } else {
            self.bounds.origin.y as f32
        };

        let sec = self
            .section
            .clone()
            .with_bounds((
                self.bounds.size.width as f32,
                self.bounds.size.height as f32,
            ))
            .with_screen_position((posx, posy))
            .with_layout(Layout::Wrap {
                line_breaker: BuiltInLineBreaker::UnicodeLineBreaker,
                h_align: self.halign,
                v_align: self.valign,
            });

        buffer.text(sec);
        /*Texture::from_id(0)
        .icon(rect(0, 4 * 64, 3 * 64, 64))
        .nine_square(self.bounds)
        .into_iter()
        .for_each(|s| buffer.sprite(s));*/

        Ok(())
    }

    fn event(&self, _event: &Event, _tx: &Sender<Msg>) -> TkResult<()> {
        Ok(())
    }
}
