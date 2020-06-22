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

const NINE_SQ: i32 = 16;

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

    pub fn nine_square(self, pos: Rect) -> impl IntoIterator<Item = Sprite> {
        let nine_sq_size = Size::new(NINE_SQ, NINE_SQ);
        vec![
            Sprite {
                texture: self.0,
                pos: Rect::new(pos.origin, nine_sq_size),
                uv: Rect::new(self.1.origin, nine_sq_size),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + NINE_SQ,
                    pos.origin.y,
                    pos.size.width - 2 * NINE_SQ,
                    NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x + NINE_SQ,
                    self.1.origin.y,
                    self.1.size.width - 2 * NINE_SQ,
                    NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + pos.size.width - NINE_SQ,
                    pos.origin.y,
                    NINE_SQ,
                    NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x + self.1.size.width - NINE_SQ,
                    self.1.origin.y,
                    NINE_SQ,
                    NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x,
                    pos.origin.y + NINE_SQ,
                    NINE_SQ,
                    pos.size.height - 2 * NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x,
                    self.1.origin.y + NINE_SQ,
                    NINE_SQ,
                    self.1.size.height - 2 * NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + NINE_SQ,
                    pos.origin.y + NINE_SQ,
                    pos.size.width - 2 * NINE_SQ,
                    pos.size.height - 2 * NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x + NINE_SQ,
                    self.1.origin.y + NINE_SQ,
                    self.1.size.width - 2 * NINE_SQ,
                    self.1.size.height - 2 * NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + pos.size.width - NINE_SQ,
                    pos.origin.y + NINE_SQ,
                    NINE_SQ,
                    pos.size.height - 2 * NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x + self.1.size.width - NINE_SQ,
                    self.1.origin.y + NINE_SQ,
                    NINE_SQ,
                    self.1.size.height - 2 * NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x,
                    pos.origin.y + pos.size.height - NINE_SQ,
                    NINE_SQ,
                    NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x,
                    self.1.origin.y + self.1.size.height - NINE_SQ,
                    NINE_SQ,
                    NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + NINE_SQ,
                    pos.origin.y + pos.size.height - NINE_SQ,
                    pos.size.width - 2 * NINE_SQ,
                    NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x + NINE_SQ,
                    self.1.origin.y + self.1.size.height - NINE_SQ,
                    self.1.size.width - 2 * NINE_SQ,
                    NINE_SQ,
                ),
            },
            Sprite {
                texture: self.0,
                pos: rect(
                    pos.origin.x + pos.size.width - NINE_SQ,
                    pos.origin.y + pos.size.height - NINE_SQ,
                    NINE_SQ,
                    NINE_SQ,
                ),
                uv: rect(
                    self.1.origin.x + self.1.size.width - NINE_SQ,
                    self.1.origin.y + self.1.size.height - NINE_SQ,
                    NINE_SQ,
                    NINE_SQ,
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
