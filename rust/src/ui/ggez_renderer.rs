use crate::ui::tk::*;
use ggez::graphics::{DrawParam, Image};
use ggez::{Context, GameError, GameResult};
use glyph_brush::{BuiltInLineBreaker, Layout};
use slab::Slab;

impl From<TkError> for GameError {
    fn from(tke: TkError) -> Self {
        GameError::RenderError(tke.to_string())
    }
}

pub struct GgezRenderer {
    textures: Slab<Image>,
}

impl GgezRenderer {
    pub fn new(_ctx: &mut Context) -> Self {
        Self {
            textures: Slab::new(),
        }
    }

    pub fn load_texture(&mut self, ctx: &mut Context, name: &str) -> GameResult<TextureId> {
        Ok(TextureId(self.textures.insert(Image::new(ctx, name)?)))
    }

    pub fn do_command(&self, ctx: &mut Context, cmd: Command) -> GameResult<()> {
        match cmd {
            Command::Sprite(sprite) => {
                let img = self.textures.get(sprite.texture.0).ok_or_else(|| {
                    GameError::RenderError("texture missing from cache".to_owned())
                })?;

                let uv_size = if sprite.uv.is_empty() {
                    size(img.width(), img.height()).to_i32()
                } else {
                    sprite.uv.size
                };

                let dest = [sprite.pos.origin.x as f32, sprite.pos.origin.y as f32];
                let scale = [
                    (sprite.pos.size.width as f32 / uv_size.width as f32),
                    (sprite.pos.size.height as f32 / uv_size.height as f32),
                ];

                let src = ggez::graphics::Rect::new(
                    sprite.uv.origin.x as f32 / img.width() as f32,
                    sprite.uv.origin.y as f32 / img.height() as f32,
                    uv_size.width as f32 / img.width() as f32,
                    uv_size.height as f32 / img.height() as f32,
                );

                ggez::graphics::draw(ctx, img, DrawParam::new().dest(dest).src(src).scale(scale))?;
            }
            Command::Text(text) => {
                ggez::graphics::queue_text_raw(
                    ctx,
                    text.to_borrowed(),
                    None::<&Layout<BuiltInLineBreaker>>,
                );
            }
        };

        Ok(())
    }
}
