use crate::ui::tk::{CommandBuffer, Element, Event, InputState, Rect, TkResult, Widget};
use std::sync::mpsc::Sender;

pub struct Stack<Msg> {
    children: Vec<Element<Msg>>,
}

impl<Msg: 'static> Stack<Msg> {
    pub fn new() -> Self {
        Stack {
            children: vec![],
        }
    }

    pub fn add(mut self, child: impl Widget<Msg> + 'static) -> Self {
        self.children.push(Box::new(child));
        self
    }

    pub fn push(&mut self, child: impl Widget<Msg> + 'static) {
        self.children.push(Box::new(child));
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg> Widget<Msg> for Stack<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        for child in &mut self.children {
            child.layout(bounds)?;
        }

        Ok(())
    }

    fn render(&self, input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        for child in &self.children {
            child.render(input, buffer)?;
        }

        Ok(())
    }

    fn event(&self, event: &Event, tx: &Sender<Msg>) -> TkResult<()> {
        // TODO - filter click events to relevant children
        for child in &self.children {
            child.event(event, tx)?;
        }
        Ok(())
    }
}
