use crate::ui::tk::{
    CommandBuffer, Element, Event, InputState, Rect, Size, TkResult, Vector, Widget,
};
use num_integer::div_rem;
use std::sync::mpsc::Sender;

pub struct Grid<Msg> {
    rows: i32,
    cols: i32,
    children: Vec<Element<Msg>>,
}

impl<Msg: 'static> Grid<Msg> {
    pub fn new(rows: i32, cols: i32) -> Self {
        Grid {
            rows,
            cols,
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

impl<Msg> Widget<Msg> for Grid<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        let size = Size::new(
            bounds.size.width / self.cols,
            bounds.size.height / self.rows,
        );

        for (idx, child) in self.children.iter_mut().enumerate() {
            let (row, col) = div_rem(idx as i32, self.cols);
            let origin = bounds.origin + Vector::new(size.width * col, size.height * row);
            child.layout(Rect::new(origin, size))?;
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
