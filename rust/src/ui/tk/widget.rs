use std::sync::mpsc::Sender;

use super::{CommandBuffer, Event, InputState, Rect, TkResult};

pub type Element<Msg> = Box<dyn Widget<Msg>>;

pub trait Widget<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()>;
    fn render(&self, input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()>;
    fn event(&self, event: &Event, tx: &Sender<Msg>) -> TkResult<()>;
}
