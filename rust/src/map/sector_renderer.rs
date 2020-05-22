use ggez::{graphics, Context, GameResult};
use pyo3::prelude::*;
use tracing;

use super::sector::{Sector, NUM_TILES, NUM_VERTS, NUM_VERTS_CAPACITY};
use ggez::graphics::{DrawParam, Drawable, FilterMode};

pub const VERTEX_SZ: f32 = 64.0;
pub const TEX_SZ: f32 = 1.0 / 8.0;
pub const SECTOR_SZ: f32 = NUM_TILES as f32 * VERTEX_SZ;
pub const NUM_TILES_CAPACITY: usize = (NUM_TILES * NUM_TILES) as usize;

struct GfxState {
    terrain: graphics::Mesh,
    fog1: graphics::Mesh,
    fog2: graphics::Mesh,
}

pub struct SectorRenderer {
    sector: PyObject,
    tiles: Vec<u8>,
    visible: Vec<u8>,
    visited: Vec<u8>,
    texture: String,
    fogofwar: String,
    gfx: Option<GfxState>,
    dirty: bool,
    dx: f32,
    dy: f32,
}

fn vert(vx: f32, vy: f32, tx: f32, ty: f32, _id: u8) -> graphics::Vertex {
    graphics::Vertex {
        pos: [vx, vy],
        uv: [tx, ty],
        color: [1.0, 1.0, 1.0, 1.0],
        /*[if id == 1 || id == 4{ 1.0} else {0.0},
        if id == 2 || id == 4 {1.0} else {0.0},
        if id == 3 {1.0} else {0.0}, 1.0],*/
    }
}

impl SectorRenderer {
    pub fn new(py: Python, sector: PyObject) -> PyResult<Self> {
        let texture = {
            let texture = sector.as_ref(py).getattr("tileset")?.get_item("texture")?;
            texture.extract()?
        };

        let fogofwar = {
            let fogofwar = sector.as_ref(py).getattr("tileset")?.get_item("fogofwar")?;
            fogofwar.extract()?
        };

        Ok(Self {
            sector,
            tiles: vec![0u8; NUM_TILES_CAPACITY],
            visible: vec![0u8; NUM_VERTS_CAPACITY],
            visited: vec![0u8; NUM_VERTS_CAPACITY],
            texture,
            fogofwar,
            gfx: None,
            dirty: true,
            dx: 0.0,
            dy: 0.0,
        })
    }

    pub fn update_offset(&mut self, dx: i16, dy: i16) {
        self.dx = f32::from(dx) * SECTOR_SZ;
        self.dy = f32::from(dy) * SECTOR_SZ;
    }

    pub fn update_fog(&mut self, py: Python) -> PyResult<()> {
        let pypeer = self.sector.getattr(py, "peer")?;
        let peer: PyRefMut<Sector> = pypeer.extract(py)?;

        peer.copy_tiles(&mut self.tiles);
        peer.copy_visible(&mut self.visible);
        peer.copy_visited(&mut self.visited);

        dbg!("update fog!");
        self.dirty = true;

        Ok(())
    }

    #[tracing::instrument(skip(self, py, ctx), level = "warn")]
    fn prepare_gfx(&mut self, py: Python, ctx: &mut Context) -> GameResult<GfxState> {
        let mut vdata = Vec::with_capacity(NUM_TILES_CAPACITY * 4);
        let mut index = Vec::with_capacity(NUM_TILES_CAPACITY * 6);
        let mut i = 0;

        for y in 0..NUM_TILES {
            for x in 0..NUM_TILES {
                let vx = f32::from(x) * VERTEX_SZ;
                let vy = f32::from(y) * VERTEX_SZ;

                let tile = i16::from(self.tiles[(x + y * NUM_TILES) as usize]);
                let (ty, tx): (i16, i16) = num_integer::div_rem(tile, 8);
                let tx = f32::from(tx) * TEX_SZ;
                let ty = f32::from(ty) * TEX_SZ;

                index.extend_from_slice(&[i, i + 1, i + 2, i, i + 3, i + 1]);
                i += 4;

                vdata.push(vert(vx, vy, tx, ty, 1));
                vdata.push(vert(
                    vx + VERTEX_SZ,
                    vy + VERTEX_SZ,
                    tx + TEX_SZ,
                    ty + TEX_SZ,
                    2,
                ));
                vdata.push(vert(vx, vy + VERTEX_SZ, tx, ty + TEX_SZ, 3));
                vdata.push(vert(vx + VERTEX_SZ, vy, tx + TEX_SZ, ty, 4));
            }
        }

        let mut image = graphics::Image::new(ctx, &self.texture)?;
        image.set_filter(FilterMode::Nearest);

        let terrain = graphics::MeshBuilder::new()
            .raw(&vdata, &index, Some(image))
            .build(ctx)?;

        let mut image = graphics::Image::new(ctx, &self.fogofwar)?;
        image.set_filter(FilterMode::Nearest);

        let fog1 = graphics::MeshBuilder::new()
            .raw(&vdata, &index, Some(image.clone()))
            .build(ctx)?;
        let fog2 = graphics::MeshBuilder::new()
            .raw(&vdata, &index, Some(image.clone()))
            .build(ctx)?;

        Ok(GfxState {
            terrain,
            fog1,
            fog2,
        })
    }

    #[tracing::instrument(skip(self, py, ctx), level = "warn")]
    fn prepare_fog(&mut self, py: Python, ctx: &mut Context) -> GameResult<()> {
        let mut fog1 = Vec::with_capacity(NUM_TILES_CAPACITY * 4);
        let mut fog2 = Vec::with_capacity(NUM_TILES_CAPACITY * 4);
        let mut index = Vec::with_capacity(NUM_TILES_CAPACITY * 6);
        let mut i = 0;

        let tidmask = 1u8;

        fn idx(x: u16, y: u16) -> usize {
            (x + y * NUM_VERTS) as usize
        }

        fn is_set(x: u8, tidmask: u8) -> u8 {
            if (x & tidmask) > 0 {
                1
            } else {
                0
            }
        }

        for y in 0..NUM_TILES {
            for x in 0..NUM_TILES {
                let vx = f32::from(x) * VERTEX_SZ;
                let vy = f32::from(y) * VERTEX_SZ;

                let a = is_set(self.visible[idx(x, y)], tidmask);
                let b = is_set(self.visible[idx(x + 1, y)], tidmask);
                let c = is_set(self.visible[idx(x, y + 1)], tidmask);
                let d = is_set(self.visible[idx(x + 1, y + 1)], tidmask);

                let tx = f32::from(4 * b + 2 * c + d) * TEX_SZ;
                let ty = f32::from(a + 2) * TEX_SZ;

                index.extend_from_slice(&[i, i + 1, i + 2, i, i + 3, i + 1]);
                i += 4;

                fog1.push(vert(vx, vy, tx, ty, 1));
                fog1.push(vert(
                    vx + VERTEX_SZ,
                    vy + VERTEX_SZ,
                    tx + TEX_SZ,
                    ty + TEX_SZ,
                    2,
                ));
                fog1.push(vert(vx, vy + VERTEX_SZ, tx, ty + TEX_SZ, 3));
                fog1.push(vert(vx + VERTEX_SZ, vy, tx + TEX_SZ, ty, 4));

                let a = is_set(self.visited[idx(x, y)], tidmask);
                let b = is_set(self.visited[idx(x + 1, y)], tidmask);
                let c = is_set(self.visited[idx(x, y + 1)], tidmask);
                let d = is_set(self.visited[idx(x + 1, y + 1)], tidmask);

                let tx = f32::from(4 * b + 2 * c + d) * TEX_SZ;
                let ty = f32::from(a) * TEX_SZ;

                fog2.push(vert(vx, vy, tx, ty, 1));
                fog2.push(vert(
                    vx + VERTEX_SZ,
                    vy + VERTEX_SZ,
                    tx + TEX_SZ,
                    ty + TEX_SZ,
                    2,
                ));
                fog2.push(vert(vx, vy + VERTEX_SZ, tx, ty + TEX_SZ, 3));
                fog2.push(vert(vx + VERTEX_SZ, vy, tx + TEX_SZ, ty, 4));
            }
        }

        let gfx = self.gfx.as_mut().unwrap();

        gfx.fog1.set_vertices(ctx, &fog1, &index);
        gfx.fog2.set_vertices(ctx, &fog2, &index);

        Ok(())
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context) -> GameResult<()> {
        if self.gfx.is_none() {
            self.gfx = Some(self.prepare_gfx(py, ctx)?);
        }

        if self.dirty {
            self.prepare_fog(py, ctx)?;
            self.dirty = false;
        }

        let gfx = self.gfx.as_mut().unwrap();

        gfx.terrain
            .draw(ctx, DrawParam::new().dest([self.dx, self.dy]))?;
        gfx.fog1
            .draw(ctx, DrawParam::new().dest([self.dx, self.dy]))?;
        gfx.fog2
            .draw(ctx, DrawParam::new().dest([self.dx, self.dy]))?;
        Ok(())
    }
}
