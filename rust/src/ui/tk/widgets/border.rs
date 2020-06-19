use crate::ui::tk::{
    rect, CommandBuffer, Element, Event, InputState, Rect, Texture, TkResult, Widget
};
use std::sync::mpsc::Sender;

pub struct Border<Msg> {
    bounds: Rect,
    child: Element<Msg>,
}

impl<Msg: 'static> Border<Msg> {
    pub fn new(child: impl Widget<Msg> + 'static) -> Self {
        Border {
            bounds: Rect::zero(),
            child: Box::new(child),
        }
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg> Widget<Msg> for Border<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        self.bounds = bounds;
        let inner = self.bounds.inflate(-8, -8);
        self.child.layout(inner)?;
        Ok(())
    }

    fn render(&self, input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        let sprites = Texture::from_id(0)
            .icon(rect(0, 128, 3 * 64, 64))
            .nine_square(self.bounds);

        for sprite in sprites {
            buffer.sprite(sprite);
        }

        self.child.render(input, buffer)?;
        Ok(())
    }

    fn event(&self, event: &Event, tx: &Sender<Msg>) -> TkResult<()> {
        self.child.event(event, tx)
    }
}
