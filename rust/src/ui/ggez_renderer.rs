use crate::scene;
use crate::ui::tk::*;
use ggez::graphics::{DrawParam, Font, Image};
use ggez::{Context, GameError, GameResult};
use glyph_brush::{BuiltInLineBreaker, Layout};
use slab::Slab;
use std::collections::hash_map::Entry;
use std::collections::HashMap;

impl From<TkError> for GameError {
    fn from(tke: TkError) -> Self {
        GameError::RenderError(tke.to_string())
    }
}

pub struct GgezRenderer {
    texture_cache: HashMap<String, TextureId>,
    textures: Slab<Image>,
    input: InputState,
    events: Vec<Event>,
}

impl GgezRenderer {
    pub fn new(ctx: &mut Context) -> GameResult<Self> {
        let mut slf = Self {
            texture_cache: HashMap::new(),
            textures: Slab::new(),
            input: InputState::default(),
            events: vec![],
        };
        slf.load_texture(ctx, "/maps/test/res/ui.png")?;
        // TODO cache this, avoid loading multiple times
        let _font = Font::new(ctx, "/maps/test/res/AccanthisadfstdBold-BYzx.ttf")?;
        Ok(slf)
    }

    pub fn load_texture(&mut self, ctx: &mut Context, name: &str) -> GameResult<TextureId> {
        match self.texture_cache.entry(name.to_owned()) {
            Entry::Occupied(entry) => Ok(*entry.get()),
            Entry::Vacant(entry) => {
                let tex_id = TextureId(self.textures.insert(Image::new(ctx, name)?));
                entry.insert(tex_id);
                Ok(tex_id)
            }
        }
    }

    pub fn event(&mut self, event: scene::Event) {
        // TODO - check buttons (left/right)
        // TODO - abstract out the scene event into a common event
        match event {
            scene::Event::MouseDown { .. } => {
                self.input.mouse_button = MouseButton::Left;
            }
            scene::Event::MouseUp { x, y, .. } => {
                self.events
                    .push(Event::Click(point(x as i32, y as i32), MouseButton::Left));
                self.input.mouse_button = MouseButton::None;
            }
            scene::Event::MouseMotion { x, y, .. } => {
                self.input.mouse_pos = point(x as i32, y as i32);
            }
            _ => {}
        };
    }

    pub fn render<Msg>(
        &mut self,
        ctx: &mut Context,
        mut root: Element<Msg>,
        bounds: Rect,
    ) -> GameResult<impl Iterator<Item = Msg>> {
        root.layout(bounds)?;

        let (tx, rx) = std::sync::mpsc::channel();
        for event in self.events.drain(..) {
            root.event(&event, &tx)?;
        }
        drop(tx); // no more events will be generated

        let mut buf = CommandBuffer::default();
        root.render(&self.input, &mut buf)?;

        for cmd in buf {
            self.do_command(ctx, cmd)?;
        }

        Ok(rx.into_iter())
    }

    fn do_command(&self, ctx: &mut Context, cmd: Command) -> GameResult<()> {
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
