use tracing::info;
use pyo3::prelude::*;
use ggez::graphics::{Image, Drawable, DrawParam, Color};
use std::collections::HashMap;
use slab::Slab;
use pyo3::types::PyDict;
use ggez::{Context, GameResult, graphics};
use std::path::PathBuf;
use crate::map::sector_renderer::SECTOR_SZ;

const SPRITE_SIZE: f32 = 128.0;

struct Sprite {
    img: Option<Image>,
    selected: bool,
    visible: u8,
    dx: f32,
    dy: f32,
    scale: f32,
}

#[pyclass]
pub struct SpriteManager {
    images: HashMap<String, Image>,
    //ring: Image,
    sprites: Slab<Sprite>,
    dx: f32,
    dy: f32,
    tidmask: u8,

    unresolved: Vec<(String, usize)>, // sprites that have not loaded images yet

    datasrc: PyObject,
}

#[pymethods]
impl SpriteManager {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["datasrc", "camera"]
    }

    #[new]
    fn new(py: Python) -> Self {
        SpriteManager {
            images: HashMap::new(),
            sprites: Slab::new(),
            dx: 0.0,
            dy: 0.0,
            tidmask: 0x01, // TODO
            unresolved: Vec::new(),
            datasrc: py.None(),
        }
    }

    #[args(kwargs = "**")]
    fn inject(slf: &PyCell<Self>, _py: Python, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        let camera = deps.get_item("camera")?;
        let look_at = slf.getattr("look_at")?;
        camera.getattr("onlookpointchanged")?.call_method1("add", (look_at,))?;

        slf.borrow_mut().datasrc = deps.get_item("datasrc")?.into();

        Ok(())
    }

    fn look_at(&mut self, sec: &PyAny) -> PyResult<()> {
        info!("looking at {}", sec);

        let sx: u16 = sec.getattr("sx")?.extract()?;
        let sy: u16 = sec.getattr("sy")?.extract()?;

        self.dx = f32::from(sx) * SECTOR_SZ;
        self.dy = f32::from(sy) * SECTOR_SZ;

        Ok(())
    }

    fn new_sprite(&mut self, imgname: String, scale: i16) -> PyResult<usize> {
        let img = self.images.get(&imgname).cloned();

        let is_unresolved = img.is_none();

        let sprite = Sprite {
            img,
            selected: false,
            visible: 0,
            dx: 0.0,
            dy: 0.0,
            scale: f32::from(scale) / SPRITE_SIZE,
        };

        let idx = self.sprites.insert(sprite);
        if is_unresolved {
            self.unresolved.push((imgname, idx));
        }

        Ok(idx)
    }

    fn set_visible(&mut self, idx: usize, visible: u8, selected: bool) {
        let sprite = self.sprites.get_mut(idx).expect("idx missing from slab");
        sprite.visible = visible;
        sprite.selected = selected;
    }

    fn set_pos(&mut self, idx: usize, dx: f32, dy: f32) {
        let sprite = self.sprites.get_mut(idx).expect("idx missing from slab");
        sprite.dx = dx;
        sprite.dy = dy;
    }
}

impl SpriteManager {
    pub fn draw(&mut self, _py: Python, ctx: &mut Context) -> GameResult<()> {
        for (imgname, idx) in self.unresolved.drain(..) {
            let sprite = self.sprites.get_mut(idx).expect("idx missing from slab");

            let path = PathBuf::from("/").join(&imgname);
            let img = Image::new(ctx, &path)?;
            self.images.insert(imgname, img.clone());
            sprite.img = Some(img)
        }

        graphics::push_transform::<ggez::nalgebra::Matrix4<f32>>(ctx, None);
        let transform = DrawParam::new()
            .dest([self.dx, self.dy])
            .to_matrix();
        graphics::mul_transform(ctx, transform);
        graphics::apply_transformations(ctx)?;

        for (_, sprite) in self.sprites.iter() {
            if (sprite.visible & self.tidmask) > 0 {
                if let Some(ref img) = sprite.img {
                    if sprite.selected {
                        img.draw(ctx, DrawParam::new()
                            .dest([sprite.dx, sprite.dy])
                            .scale([sprite.scale, sprite.scale])
                            .color(Color::from_rgb(0xFF, 0xFF, 0x00)))?;
                    } else {
                        img.draw(ctx, DrawParam::new()
                            .dest([sprite.dx, sprite.dy])
                            .scale([sprite.scale, sprite.scale]))?;
                    }
                }
            }


        }

        graphics::pop_transform(ctx);
        graphics::apply_transformations(ctx)?;

        Ok(())
    }
}

