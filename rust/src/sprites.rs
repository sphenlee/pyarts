use crate::map::sector_renderer::SECTOR_SZ;
use crate::util::YartsResult;
use ggez::graphics::{DrawParam, Drawable, Image};
use ggez::{graphics, Context, GameResult};
use log::info;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use slab::Slab;
use std::collections::HashMap;
use std::path::PathBuf;

const SPRITE_SIZE: f32 = 64.0;

struct Sprite {
    img: Option<Image>,
    selected: bool,
    visible: u8,
    dx: f32,
    dy: f32,
    r: f32,
}

#[pyclass]
pub struct SpriteManager {
    images: HashMap<String, Image>,
    sprites: Slab<Sprite>,
    dx: f32,
    dy: f32,
    //tidmask: u8,
    unresolved: Vec<(String, usize)>, // sprites that have not loaded images yet

    datasrc: PyObject,
    local: PyObject,
}

#[pymethods]
impl SpriteManager {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["datasrc", "camera", "local"]
    }

    #[new]
    fn new(py: Python) -> Self {
        SpriteManager {
            images: HashMap::new(),
            sprites: Slab::new(),
            dx: 0.0,
            dy: 0.0,
            unresolved: Vec::new(),
            datasrc: py.None(),
            local: py.None(),
        }
    }

    #[args(kwargs = "**")]
    fn inject(slf: &PyCell<Self>, _py: Python, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        let camera = deps.get_item("camera")?;
        let look_at = slf.getattr("look_at")?;
        camera
            .getattr("onlookpointchanged")?
            .call_method1("add", (look_at,))?;

        slf.borrow_mut().datasrc = deps.get_item("datasrc")?.into();
        slf.borrow_mut().local = deps.get_item("local")?.into();

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

    fn new_sprite(&mut self, imgname: String, r: i16) -> PyResult<usize> {
        let img = self.images.get(&imgname).cloned();

        let is_unresolved = img.is_none();

        let sprite = Sprite {
            img,
            selected: false,
            visible: 0,
            dx: 0.0,
            dy: 0.0,
            r: f32::from(r),// / SPRITE_SIZE,
        };

        let idx = self.sprites.insert(sprite);
        if is_unresolved {
            self.unresolved.push((imgname, idx));
        }

        Ok(idx)
    }

    fn remove(&mut self, idx: usize) -> PyResult<()> {
        self.sprites.remove(idx);
        Ok(())
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
    fn get_tidmask(&self, py: Python) -> PyResult<u8> {
        self.local.getattr(py, "tidmask")?.extract(py)
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context) -> YartsResult<()> {
        let tidmask = self.get_tidmask(py)?;

        for (imgname, idx) in self.unresolved.drain(..) {
            let sprite = self.sprites.get_mut(idx).expect("idx missing from slab");

            let path = PathBuf::from("/").join(&imgname);
            let img = Image::new(ctx, &path)?;
            self.images.insert(imgname, img.clone());
            sprite.img = Some(img)
        }

        graphics::push_transform::<ggez::nalgebra::Matrix4<f32>>(ctx, None);
        let transform = DrawParam::new().dest([-self.dx, -self.dy]).to_matrix();
        graphics::mul_transform(ctx, transform);
        graphics::apply_transformations(ctx)?;

        for (_, sprite) in self.sprites.iter() {
            let scale = sprite.r / SPRITE_SIZE;


            if (sprite.visible & tidmask) > 0 {
                if let Some(ref img) = sprite.img {
                    if sprite.selected {
                        let circle = SpriteManager::make_ring(ctx, sprite)?;

                        circle.draw(ctx, DrawParam::new()
                            .dest([sprite.dx + sprite.r, sprite.dy + (sprite.r * 1.5)]))?;
                    }

                    let param = DrawParam::new()
                        .dest([sprite.dx, sprite.dy])
                        .scale([scale, scale]);

                    img.draw(ctx, param)?;
                }
            }
        }

        graphics::pop_transform(ctx);
        graphics::apply_transformations(ctx)?;

        Ok(())
    }

    fn make_ring(ctx: &mut Context, sprite: &Sprite) -> GameResult<graphics::Mesh> {
        graphics::Mesh::new_ellipse(
            ctx,
            graphics::DrawMode::stroke(2.0),
            [0.0, 0.0],
            sprite.r,
            sprite.r * 0.5,
            0.01,
            graphics::Color::new(0.5, 1.0, 0.0, 1.0),
        )
    }
}
