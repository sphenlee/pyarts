use crate::ui::tk::markup::parse;
use crate::ui::tk::{CommandBuffer, Element, Event, InputState, Rect, TkResult, Widget};
//use glyph_brush::{BuiltInLineBreaker, HorizontalAlign, Layout, OwnedSection, VerticalAlign};
use std::sync::mpsc::Sender;
use ggez::graphics::{DrawParam, Text as GgezText, TextAlign, TextLayout};

pub struct Text<Msg> {
    text: GgezText,
    bounds: Rect,
    halign: TextAlign,
    valign: TextAlign,
    _msg: std::marker::PhantomData<Msg>, // unused type param
}

impl<Msg: 'static> Text<Msg> {
    pub fn new(text: impl Into<String>) -> TkResult<Self> {
        let mut parsed = parse(&text.into())?;

        parsed.set_font("Accanthis");

        Ok(Text {
            text: parsed,
            bounds: Rect::zero(),
            halign: TextAlign::Begin,
            valign: TextAlign::Begin,
            _msg: std::marker::PhantomData,
        })
    }

    pub fn halign(mut self, halign: TextAlign) -> Self {
        self.halign = halign;
        self
    }

    pub fn valign(mut self, valign: TextAlign) -> Self {
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
        let posx = if self.halign == TextAlign::Middle {
            self.bounds.origin.x as f32 + self.bounds.size.width as f32 / 2.0
        } else {
            self.bounds.origin.x as f32
        };

        let posy = if self.valign == TextAlign::Middle {
            self.bounds.origin.y as f32 + self.bounds.size.height as f32 / 2.0
        } else {
            self.bounds.origin.y as f32
        };

        let mut text = self.text.clone();

        text.set_bounds([
                self.bounds.size.width as f32,
                self.bounds.size.height as f32,
            ])
            .set_layout(TextLayout {
                h_align: self.halign,
                v_align: self.valign,
            })
            .set_wrap(true);

        buffer.text(text, DrawParam::new().dest([posx, posy]));

        Ok(())
    }

    fn event(&self, _event: &Event, _tx: &Sender<Msg>) -> TkResult<()> {
        Ok(())
    }
}
