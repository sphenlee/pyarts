use crate::ui::tk::{CommandBuffer, Element, Event, InputState, Rect, Size, TkResult, Widget};
use std::sync::mpsc::Sender;

pub enum Direction {
    Horizontal,
    Vertical,
}

impl Direction {
    fn major_minor(&self, sz: Size) -> Size {
        match self {
            Direction::Horizontal => sz,
            Direction::Vertical => Size::new(sz.height, sz.width),
        }
    }
}

pub struct Panel<Msg> {
    direction: Direction,
    children: Vec<Element<Msg>>,
    flex: Vec<i32>,
}

impl<Msg: 'static> Panel<Msg> {
    pub fn new(direction: Direction) -> Self {
        Panel {
            direction,
            children: vec![],
            flex: vec![],
        }
    }

    pub fn hbox() -> Self {
        Panel {
            direction: Direction::Horizontal,
            children: vec![],
            flex: vec![],
        }
    }

    pub fn vbox() -> Self {
        Panel {
            direction: Direction::Vertical,
            children: vec![],
            flex: vec![],
        }
    }

    pub fn add(mut self, child: impl Widget<Msg> + 'static) -> Self {
        self.children.push(Box::new(child));
        self.flex.push(1);
        self
    }

    pub fn add_flex(mut self, flex: i32, child: impl Widget<Msg> + 'static) -> Self {
        self.children.push(Box::new(child));
        self.flex.push(flex);
        self
    }

    pub fn push(&mut self, flex: i32, child: impl Widget<Msg> + 'static) {
        self.children.push(Box::new(child));
        self.flex.push(flex);
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg> Widget<Msg> for Panel<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        let total: i32 = self.flex.iter().sum();

        let mut origin = bounds.origin;

        let (major, minor) = self.direction.major_minor(bounds.size).to_tuple();

        for (child, &flex) in self.children.iter_mut().zip(&self.flex) {
            let computed = major * flex / total;

            let size = self.direction.major_minor(Size::new(computed, minor));

            child.layout(Rect::new(origin, size))?;

            origin = origin + self.direction.major_minor(Size::new(computed, 0));
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
