use super::{rect, Rect};
use crate::ui::tk::Size;

#[derive(Copy, Clone, Debug)]
pub struct Texture {
    pub id: usize,
    pub size: Size,
}

impl Texture {
    pub fn from_id(id: usize) -> Self {
        Self {
            id,
            size: Size::default(),
        }
    }

    pub fn whole(self) -> Icon {
        Icon(self, Rect::zero())
    }

    pub fn icon(self, rect: Rect) -> Icon {
        Icon(self, rect)
    }
}

#[derive(Copy, Clone)]
pub struct Icon(Texture, Rect);

impl Icon {
    pub fn at(self, rect: Rect) -> Sprite {
        Sprite {
            texture: self.0,
            pos: rect,
            uv: self.1,
        }
    }

    pub fn texture(&self) -> Texture {
        self.0
    }

    pub fn uv(&self) -> Rect {
        self.1
    }

    pub fn nine_square(self, pos: Rect, offset: i32) -> impl IntoIterator<Item = Sprite> {
        let nine_sq_size = Size::new(offset, offset);
        vec![
            Sprite {
                texture: self.0,
                pos: Rect::new(pos.origin, nine_sq_size),
                uv: Rect::new(self.1.origin, nine_sq_size),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + offset,
                    pos.origin.y,
                    pos.size.width - 2 * offset,
                    offset,
                ),
                uv: rect(
                    self.1.origin.x + offset,
                    self.1.origin.y,
                    self.1.size.width - 2 * offset,
                    offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + pos.size.width - offset,
                    pos.origin.y,
                    offset,
                    offset,
                ),
                uv: rect(
                    self.1.origin.x + self.1.size.width - offset,
                    self.1.origin.y,
                    offset,
                    offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x,
                    pos.origin.y + offset,
                    offset,
                    pos.size.height - 2 * offset,
                ),
                uv: rect(
                    self.1.origin.x,
                    self.1.origin.y + offset,
                    offset,
                    self.1.size.height - 2 * offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + offset,
                    pos.origin.y + offset,
                    pos.size.width - 2 * offset,
                    pos.size.height - 2 * offset,
                ),
                uv: rect(
                    self.1.origin.x + offset,
                    self.1.origin.y + offset,
                    self.1.size.width - 2 * offset,
                    self.1.size.height - 2 * offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + pos.size.width - offset,
                    pos.origin.y + offset,
                    offset,
                    pos.size.height - 2 * offset,
                ),
                uv: rect(
                    self.1.origin.x + self.1.size.width - offset,
                    self.1.origin.y + offset,
                    offset,
                    self.1.size.height - 2 * offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x,
                    pos.origin.y + pos.size.height - offset,
                    offset,
                    offset,
                ),
                uv: rect(
                    self.1.origin.x,
                    self.1.origin.y + self.1.size.height - offset,
                    offset,
                    offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + offset,
                    pos.origin.y + pos.size.height - offset,
                    pos.size.width - 2 * offset,
                    offset,
                ),
                uv: rect(
                    self.1.origin.x + offset,
                    self.1.origin.y + self.1.size.height - offset,
                    self.1.size.width - 2 * offset,
                    offset,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + pos.size.width - offset,
                    pos.origin.y + pos.size.height - offset,
                    offset,
                    offset,
                ),
                uv: rect(
                    self.1.origin.x + self.1.size.width - offset,
                    self.1.origin.y + self.1.size.height - offset,
                    offset,
                    offset,
                ),
            },
        ]
    }
}

#[derive(Debug)]
pub struct Sprite {
    pub texture: Texture,
    pub pos: Rect,
    pub uv: Rect,
}

impl From<(Rect, Rect, Texture)> for Sprite {
    fn from((pos, uv, texture): (Rect, Rect, Texture)) -> Self {
        Sprite { pos, uv, texture }
    }
}
