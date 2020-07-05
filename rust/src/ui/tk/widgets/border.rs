use crate::ui::tk::{
    rect, CommandBuffer, Element, Event, Icon, InputState, Rect, Texture, TkResult, Widget,
};
use std::sync::mpsc::Sender;

const BORDER_OFFSET_X: i32 = 0;
const BORDER_OFFSET_Y: i32 = 2 * 64;
const BORDER_WIDTH: i32 = 3 * 64;
const BORDER_HEIGHT: i32 = 64;

pub struct Border<Msg> {
    icon: Icon,
    bounds: Rect,
    child: Element<Msg>,
}

impl<Msg: 'static> Border<Msg> {
    pub fn with_icon(icon: Icon, child: impl Widget<Msg> + 'static) -> Self {
        Border {
            icon,
            bounds: Rect::zero(),
            child: Box::new(child),
        }
    }

    pub fn new(child: impl Widget<Msg> + 'static) -> Self {
        let icon = Texture::from_id(0).icon(rect(
            BORDER_OFFSET_X,
            BORDER_OFFSET_Y,
            BORDER_WIDTH,
            BORDER_HEIGHT,
        ));
        Self::with_icon(icon, child)
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
        let sprites = self.icon.nine_square(self.bounds, 16);

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
