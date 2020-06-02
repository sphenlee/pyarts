use ggez::{Context, GameResult};
use std::fmt::Debug;

pub trait Node: Debug {
    fn layout(&mut self, w: u32, h: u32);
    fn render(&mut self, ctx: &mut Context) -> GameResult<()>;
}

#[derive(Default, Debug)]
struct Container {
    pub children: Vec<Box<dyn Node>>,
}

impl Container {
    fn append(&mut self, child: Box<dyn Node>) {
        self.children.push(child);
    }
}


#[derive(Default, Debug)]
pub struct Grid {
    inner: Container,
    rows: u32,
    cols: u32,
    each_width: u32,
    each_height: u32
}

impl Grid {
    pub fn new(rows: u32, cols: u32) -> Box<Grid> {
        Box::new(Grid {
            rows,
            cols,
            ..Default::default()
        })
    }

    fn append(&mut self, child: Box<dyn Node>) {
        self.inner.append(child);
    }
}

impl Node for Grid {
    fn layout(&mut self, w: u32, h: u32) {
        self.each_width = w / self.cols;
        self.each_height = h / self.rows;

        for child in &mut self.inner.children {
            child.layout(self.each_width, self.each_width);
        }
    }

    fn render(&mut self, ctx: &mut Context) -> GameResult<()> {

        // for idx, child in enumerate(self.children):
        //     y, x = divmod(idx, self.cols)
        //
        // with ctx:
        //     ctx.translate(x * self.ew, y * self.eh)
        // ctx.rectangle(0, 0, self.ew, self.eh)
        // ctx.clip()
        // child.render(ctx)
    }
}
