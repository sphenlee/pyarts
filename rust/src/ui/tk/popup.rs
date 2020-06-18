use crate::ui::tk::{
    CommandBuffer, Element, Event, InputState, Point, Rect, Size, TkResult, Widget,
};
use std::sync::mpsc::Sender;

pub struct Popup<Msg> {
    bounds: Rect,
    child: Element<Msg>,
}

pub struct PopupBuilder<Msg> {
    bounds: Rect,
    phantom: std::marker::PhantomData<Msg>,
}

impl<Msg: 'static> Popup<Msg> {
    pub fn new() -> PopupBuilder<Msg> {
        PopupBuilder::<Msg> {
            bounds: Rect::zero(),
            phantom: std::marker::PhantomData,
        }
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg: 'static> PopupBuilder<Msg> {
    pub fn anchor(mut self, point: Point) -> Self {
        self.bounds.origin = point;
        self
    }

    pub fn size(mut self, size: Size) -> Self {
        self.bounds.size = size;
        self
    }

    pub fn add(self, child: impl Widget<Msg> + 'static) -> Popup<Msg> {
        Popup {
            child: Box::new(child),
            bounds: self.bounds,
        }
    }
}

impl<Msg> Widget<Msg> for Popup<Msg> {
    fn layout(&mut self, _bounds: Rect) -> TkResult<()> {
        // popup ignores the parent's bounds ;)
        self.child.layout(self.bounds)?;
        Ok(())
    }

    fn render(&self, input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        self.child.render(input, buffer)?;
        Ok(())
    }

    fn event(&self, event: &Event, tx: &Sender<Msg>) -> TkResult<()> {
        self.child.event(event, tx)?;
        Ok(())
    }
}
