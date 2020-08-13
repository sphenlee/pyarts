use ggez::{Context, GameResult};
use log::trace;
use pyo3::prelude::*;

use super::sector::{Sector, NUM_TILES};
use ggez::graphics::{self, DrawParam, Drawable, FilterMode};

pub const VERTEX_SZ: f32 = 32.0;
pub const TILES_PER_ROW: u16 = 16;
pub const TEX_SZ: f32 = 1.0 / 8.0;
pub const TEX_SZ_X: f32 = 1.0 / TILES_PER_ROW as f32; // tiles per row
pub const TEX_SZ_Y: f32 = 1.0 / 259.0; // tiles per column TODO this can't be a const!
pub const SECTOR_SZ: f32 = NUM_TILES as f32 * VERTEX_SZ;
pub const NUM_TILES_CAPACITY: usize = (NUM_TILES * NUM_TILES) as usize;

struct GfxState {
    terrain: graphics::Mesh,
    fog1: graphics::Mesh,
    fog2: graphics::Mesh,
    fogofwar: graphics::Image,
}

pub struct SectorRenderer {
    sector: PyObject,
    texture: String,
    fogofwar: String,
    gfx: Option<GfxState>,
    dx: f32,
    dy: f32,
    update_token: u8,
}

fn vert(vx: f32, vy: f32, tx: f32, ty: f32, walk: u8) -> graphics::Vertex {
    let _color = match walk {
        0x00 => [1.0, 1.0, 1.0, 1.0],        // open => shallows (white)
        0x01 => [0.0, 0.0, 1.0, 1.0],        // sea+air => water (blue)
        0x02 => [0.0, 1.0, 0.0, 1.0],        // ground+air => land (green)
        0x03 => [0.1, 0.0, 0.0, 1.0],        // air => hole (red)
        0x04 => [0.0, 1.0, 1.0, 1.0],        // ground+sea => no fly zone (cyan)
        0x05 => [1.0, 0.0, 1.0, 1.0],        // sea => deep ocean (magenta)
        0x06 => [1.0, 1.0, 0.0, 1.0],        // ground => forest (yellow)
        0x07 => [0.5, 0.5, 0.5, 1.0],        // totally impassable (gray)
        0x08..=0x0F => [0.0, 0.0, 0.0, 1.0], // footprint (black)
        _ => panic!("invalid walk bitpattern"),
    };

    graphics::Vertex {
        pos: [vx, vy],
        uv: [tx, ty],
        color: [1.0, 1.0, 1.0, 1.0],
        //color,
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
            texture,
            fogofwar,
            gfx: None,
            dx: 0.0,
            dy: 0.0,
            update_token: 0,
        })
    }

    pub fn update_offset(&mut self, dx: i16, dy: i16) {
        self.dx = f32::from(dx) * SECTOR_SZ;
        self.dy = f32::from(dy) * SECTOR_SZ;
    }

    fn prepare_gfx(&mut self, py: Python, ctx: &mut Context) -> GameResult<GfxState> {
        trace!("updating gfx");

        let sector: PyRefMut<Sector> = self.sector.extract(py).expect("sector is wrong type");

        trace!("(sector is {},{})", sector.sx(), sector.sy());

        let mut vdata = Vec::with_capacity(NUM_TILES_CAPACITY * 4);
        let mut index = Vec::with_capacity(NUM_TILES_CAPACITY * 6);
        let mut i = 0;

        trace!("preparing vert data for terrain");
        for y in 0..NUM_TILES {
            for x in 0..NUM_TILES {
                let vx = f32::from(x) * VERTEX_SZ;
                let vy = f32::from(y) * VERTEX_SZ;

                //let tile = i16::from(self.tiles[(x + y * NUM_TILES) as usize]);
                let tile = sector.tile((x, y)) as u16;
                let (ty, tx): (u16, u16) = num_integer::div_rem(tile, TILES_PER_ROW);
                let tx = f32::from(tx) * TEX_SZ_X;
                let ty = f32::from(ty) * TEX_SZ_Y;

                let walk = sector.walk((x, y));

                index.extend_from_slice(&[i, i + 1, i + 2, i, i + 3, i + 1]);
                i += 4;

                vdata.push(vert(vx, vy, tx, ty, walk));
                vdata.push(vert(
                    vx + VERTEX_SZ,
                    vy + VERTEX_SZ,
                    tx + TEX_SZ_X,
                    ty + TEX_SZ_Y,
                    walk,
                ));
                vdata.push(vert(vx, vy + VERTEX_SZ, tx, ty + TEX_SZ_Y, walk));
                vdata.push(vert(vx + VERTEX_SZ, vy, tx + TEX_SZ_X, ty, walk));
            }
        }

        trace!("loading texture image: {}", self.texture);
        let mut image = graphics::Image::new(ctx, &self.texture)?;
        image.set_filter(FilterMode::Nearest);

        trace!("building mesh");
        let terrain = graphics::MeshBuilder::new()
            .raw(&vdata, &index, Some(image))
            .build(ctx)?;

        trace!("loading fog image: {}", self.fogofwar);
        let mut fogofwar = graphics::Image::new(ctx, &self.fogofwar)?;
        fogofwar.set_filter(FilterMode::Nearest);

        trace!("building (empty) fog mesh1");
        let fog1 = graphics::MeshBuilder::new()
            .raw(&vdata, &index, None)
            .build(ctx)?;
        trace!("building (empty) fog mesh2");
        let fog2 = graphics::MeshBuilder::new()
            .raw(&vdata, &index, None)
            .build(ctx)?;

        trace!("gfx done");
        Ok(GfxState {
            terrain,
            fog1,
            fog2,
            fogofwar,
        })
    }

    fn prepare_fog(&mut self, ctx: &mut Context, sector: &PyRefMut<Sector>) -> GameResult<()> {
        trace!("preparing fog: ({}, {})", self.dx, self.dy);

        let mut fog1 = Vec::with_capacity(NUM_TILES_CAPACITY * 4);
        let mut fog2 = Vec::with_capacity(NUM_TILES_CAPACITY * 4);
        let mut index = Vec::with_capacity(NUM_TILES_CAPACITY * 6);
        let mut i = 0;

        let tidmask = 1u8; // TODO

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

                let a = is_set(sector.visible((x, y)), tidmask);
                let b = is_set(sector.visible((x + 1, y)), tidmask);
                let c = is_set(sector.visible((x, y + 1)), tidmask);
                let d = is_set(sector.visible((x + 1, y + 1)), tidmask);

                // let a = 1 - is_set(peer.walk((x, y)), 0x08 | 0x01);
                // let b = a; let c = a; let d = a;

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

                let a = is_set(sector.visited((x, y)), tidmask);
                let b = is_set(sector.visited((x + 1, y)), tidmask);
                let c = is_set(sector.visited((x, y + 1)), tidmask);
                let d = is_set(sector.visited((x + 1, y + 1)), tidmask);

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

        trace!("update fog mesh 1");
        gfx.fog1 = graphics::Mesh::from_raw(ctx, &fog1, &index, Some(gfx.fogofwar.clone()))?;
        trace!("update fog mesh 2");
        gfx.fog2 = graphics::Mesh::from_raw(ctx, &fog2, &index, Some(gfx.fogofwar.clone()))?;

        trace!("fog done");
        Ok(())
    }

    pub fn draw(&mut self, py: Python, ctx: &mut Context, offset: (f32, f32)) -> GameResult<()> {
        if self.gfx.is_none() {
            self.gfx = Some(self.prepare_gfx(py, ctx)?);
        }

        let pysector = self.sector.clone_ref(py);
        let sector: PyRefMut<Sector> = pysector.extract(py).expect("sector is wrong type");

        if self.update_token != sector.update_token() {
            self.prepare_fog(ctx, &sector)?;
            self.update_token = sector.update_token();
        }

        let gfx = self.gfx.as_mut().unwrap();

        let dp = DrawParam::new().dest([self.dx + offset.0, self.dy + offset.1]);

        gfx.terrain.draw(ctx, dp)?;
        gfx.fog1.draw(ctx, dp)?;
        gfx.fog2.draw(ctx, dp)?;
        Ok(())
    }
}
