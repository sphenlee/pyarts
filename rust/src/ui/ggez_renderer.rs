use crate::scene;
use crate::ui::tk::*;
use ggez::graphics::{Canvas, DrawParam, FontData, Image};
use ggez::{Context, GameError, GameResult};
use slab::Slab;
use std::collections::hash_map::Entry;
use std::collections::HashMap;

impl From<TkError> for GameError {
    fn from(tke: TkError) -> Self {
        GameError::RenderError(tke.to_string())
    }
}

pub struct GgezRenderer {
    texture_cache: HashMap<String, Texture>,
    textures: Slab<Image>,
    input: InputState,
    events: Vec<Event>,
    //pub font: FontData,
}

impl GgezRenderer {
    pub fn new(ctx: &mut Context) -> GameResult<Self> {
        let mut slf = Self {
            texture_cache: HashMap::new(),
            textures: Slab::new(),
            input: InputState::default(),
            events: vec![],
            //font: FontData::from_path(ctx, "/maps/test/res/AccanthisadfstdBold-BYzx.ttf")?,
        };

        let font = FontData::from_path(ctx, "/maps/test/res/AccanthisadfstdBold-BYzx.ttf")?;
        ctx.gfx.add_font("Accanthis", font);

        slf.load_texture(ctx, "/maps/test/res/ui.png")?;
        Ok(slf)
    }

    pub fn load_texture(&mut self, ctx: &mut Context, name: &str) -> GameResult<Texture> {
        match self.texture_cache.entry(name.to_owned()) {
            Entry::Occupied(entry) => Ok(*entry.get()),
            Entry::Vacant(entry) => {
                let img = Image::from_path(ctx, name)?;
                let size = Size::new(img.width() as i32, img.height() as i32);
                let id = self.textures.insert(img);
                let tex = Texture { id, size };
                entry.insert(tex);
                Ok(tex)
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
                self.events.push(Event::Click(
                    Point::new(x as i32, y as i32),
                    MouseButton::Left,
                ));
                self.input.mouse_button = MouseButton::None;
            }
            scene::Event::MouseMotion { x, y, .. } => {
                self.input.mouse_pos = Point::new(x as i32, y as i32);
            }
            _ => {}
        };
    }

    pub fn render<Msg>(
        &mut self,
        _ctx: &mut Context,
        canvas: &mut Canvas,
        mut root: Element<Msg>,
        bounds: Rect,
    ) -> GameResult<impl Iterator<Item = Msg>> {
        root.layout(bounds)?;

        let (tx, rx) = std::sync::mpsc::channel();
        for event in self.events.drain(..) {
            log::trace!("sending event to root component {:?}", event);
            root.event(&event, &tx)?;
        }
        drop(tx); // no more events will be generated

        let mut buf = CommandBuffer::default();
        root.render(&self.input, &mut buf)?;

        for cmd in buf {
            self.do_command(canvas, cmd)?;
        }

        Ok(rx.into_iter())
    }

    fn do_command(&self, canvas: &mut Canvas, cmd: Command) -> GameResult<()> {
        match cmd {
            Command::Sprite(sprite) => {
                let img = self.textures.get(sprite.texture.id).ok_or_else(|| {
                    GameError::RenderError("texture missing from cache".to_owned())
                })?;

                let uv_size = if sprite.uv.is_empty() {
                    Size::new(img.width() as i32, img.height() as i32)
                } else {
                    sprite.uv.size
                };
                let pos_size = if sprite.pos.is_empty() {
                    Size::new(img.width() as i32, img.height() as i32)
                } else {
                    sprite.pos.size
                };

                let dest = [sprite.pos.origin.x as f32, sprite.pos.origin.y as f32];
                let scale = [
                    (pos_size.width as f32 / uv_size.width as f32),
                    (pos_size.height as f32 / uv_size.height as f32),
                ];

                let src = ggez::graphics::Rect::new(
                    sprite.uv.origin.x as f32 / img.width() as f32,
                    sprite.uv.origin.y as f32 / img.height() as f32,
                    uv_size.width as f32 / img.width() as f32,
                    uv_size.height as f32 / img.height() as f32,
                );

                canvas.draw(img, DrawParam::new().dest(dest).src(src).scale(scale));
            }
            Command::Text(text, param) => {
                canvas.draw(&text, param);
            }
        };

        Ok(())
    }
}
