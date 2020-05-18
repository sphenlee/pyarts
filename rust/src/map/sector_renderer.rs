use pyo3::prelude::*;
use ggez::{graphics, Context, GameResult};

use super::sector::NUM_TILES;
use ggez::graphics::{Drawable, DrawParam};

const VERTEX_SZ: f32 = 64.0;
const TEX_SZ: f32 = 1.0 / 8.0;
const SECTOR_SZ: f32 = NUM_TILES as f32 * VERTEX_SZ;

struct GfxState {
    terrain: graphics::Mesh,
}

pub struct SectorRenderer {
    sector: PyObject,
    peer: PyObject,
    gfx: Option<GfxState>,
    dx: f32,
    dy: f32,
}

fn vert(vx: f32, vy: f32, tx: f32, ty: f32, id: u8) -> graphics::Vertex {
    graphics::Vertex {
        pos: [vx, vy],
        uv: [tx, ty],
        color: [if id == 1 || id == 4{ 1.0} else {0.0},
            if id == 2 || id == 4 {1.0} else {0.0},
            if id == 3 {1.0} else {0.0}, 1.0],
    }
}

impl SectorRenderer {
    pub fn new(py: Python, sector: PyObject) -> PyResult<Self> {
        let peer: PyObject = sector.getattr(py, "peer")?.extract(py)?;

        Ok(Self {
            sector,
            peer,
            gfx: None,
            dx: 0.0,
            dy: 0.0,
        })
    }

    pub fn update_offset(&mut self, dx: i16, dy: i16) {
        self.dx = dbg!(f32::from(dx) * SECTOR_SZ);
        self.dy = dbg!(f32::from(dy) * SECTOR_SZ);

    }

    fn prepare_gfx(&mut self, ctx: &mut Context) -> GameResult<GfxState> {


        let mut vdata = Vec::with_capacity((NUM_TILES * NUM_TILES * 4) as usize);
        let mut index = Vec::with_capacity((NUM_TILES * NUM_TILES * 6) as usize);
        let mut i = 0;

        for y in 0..NUM_TILES {
            for x in 0..NUM_TILES {
                let vx = f32::from(x) * VERTEX_SZ;
                let vy = f32::from(y) * VERTEX_SZ;

                let tile = 0;//self.peer.tile((x, y));
                let (ty, tx): (i16, i16) = num_integer::div_rem(tile, 8);
                let tx = f32::from(tx) * TEX_SZ;
                let ty = 1.0 - f32::from(ty) * TEX_SZ;

                index.extend_from_slice(&[
                    i, i + 1, i + 2,
                    i, i + 3, i + 1]);
                i += 4;

                vdata.push( vert(vx, vy, tx, ty, 1));
                vdata.push( vert(vx + VERTEX_SZ, vy + VERTEX_SZ, tx + TEX_SZ, ty - TEX_SZ, 2));
                vdata.push( vert(vx, vy + VERTEX_SZ, tx, ty - TEX_SZ, 3));
                vdata.push( vert(vx + VERTEX_SZ, vy, tx + TEX_SZ, ty, 4));
            }
        }

        let mesh = graphics::MeshBuilder::new()
            .raw(&vdata, &index, None)
            .build(ctx)?;

        Ok(GfxState{
            terrain: mesh
        })
    }

    pub fn draw(&mut self, ctx: &mut Context) -> GameResult<()> {
        if self.gfx.is_none() {
            self.gfx = Some(self.prepare_gfx(ctx)?);
        }

        let gfx = self.gfx.as_mut().unwrap();

        gfx.terrain.draw(ctx, DrawParam::new().dest([self.dx, self.dy]))?;
        Ok(())
    }
}
