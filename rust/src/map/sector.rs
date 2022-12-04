use super::loader::load_map;
use log::trace;
use pyo3::prelude::*;
use crate::map::loader::LoadedEnt;

pub const NUM_TILES: u16 = 64;
pub const NUM_VERTS: u16 = NUM_TILES + 1;

pub const NUM_TILES_CAPACITY: usize = (NUM_TILES * NUM_TILES) as usize;
pub const NUM_VERTS_CAPACITY: usize = (NUM_VERTS * NUM_VERTS) as usize;

pub const WALK_FOOT: u8 = 0x08;

#[pyclass(module = "yarts", subclass)]
pub struct Sector {
    #[pyo3(get)]
    sx: i32,
    #[pyo3(get)]
    sy: i32,
    tiles: Vec<u32>,
    visited: Vec<u8>,
    visible: Vec<u8>,
    walk: Vec<u8>,
    ents: Vec<LoadedEnt>,
    update_token: u8,
}

#[pymethods]
impl Sector {
    #[new]
    pub fn new(sx: i32, sy: i32) -> PyResult<Self> {
        Ok(Sector {
            sx,
            sy,
            tiles: vec![],
            visited: vec![0u8; NUM_VERTS_CAPACITY],
            visible: vec![0u8; NUM_VERTS_CAPACITY],
            walk: vec![],
            ents: vec![],
            update_token: 1, // the renderer defaults to 0
        })
    }

    fn load(&mut self, file: String) -> PyResult<()> {
        let loaded = load_map(file)?;

        self.tiles = loaded.tiles;
        self.walk = loaded.walk;
        self.ents = loaded.ents;

        Ok(())
    }

    fn loaded_ents(&mut self) -> PyResult<Vec<LoadedEnt>> {
        Ok(std::mem::take(&mut self.ents))
    }

    fn footprint(&mut self, x: i16, y: i16, r: i16) {
        trace!(
            "foot printing sector {},{} -> ({},{})@{}",
            self.sx,
            self.sy,
            x,
            y,
            r
        );
        for i in (x - r)..(x + r) {
            for j in (y - r)..(y + r) {
                if i >= 0 && j >= 0 && i < NUM_TILES as i16 && j < NUM_TILES as i16 {
                    if ((x - i) * (x - i)) + ((y - j) * (y - j)) <= r * r {
                        self.walk[(i + j * NUM_TILES as i16) as usize] |= WALK_FOOT;
                    }
                }
            }
        }
    }

    fn unfootprint(&mut self, x: i16, y: i16, r: i16) {
        trace!(
            "unfoot printing sector {},{} -> ({},{})@{}",
            self.sx,
            self.sy,
            x,
            y,
            r
        );
        for i in (x - r)..(x + r) {
            for j in (y - r)..(y + r) {
                if i >= 0 && j >= 0 && i < NUM_TILES as i16 && j < NUM_TILES as i16 {
                    if ((x - i) * (x - i)) + ((y - j) * (y - j)) <= r * r {
                        self.walk[(i + j * NUM_TILES as i16) as usize] &= !WALK_FOOT;
                    }
                }
            }
        }
    }

    pub fn tile(&self, pt: (u16, u16)) -> u32 {
        let idx = pt.0 + NUM_TILES * pt.1;
        self.tiles[idx as usize]
    }

    pub fn visible(&self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_VERTS * pt.1;
        self.visible[idx as usize]
    }

    pub fn visited(&self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_VERTS * pt.1;
        self.visited[idx as usize]
    }

    pub fn walk(&self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_TILES * pt.1;
        self.walk[idx as usize]
    }

    fn clear_fog(&mut self) {
        self.visible.iter_mut().for_each(|x| *x = 0);
    }

    fn update_fog(&mut self, x: i16, y: i16, sight: i16, tid: u8) {
        trace!(
            "update fog sector {},{} -> ({},{})@{} tid={}",
            self.sx,
            self.sy,
            x,
            y,
            sight,
            tid
        );

        for i in (x - sight)..(x + sight) {
            for j in (y - sight)..(y + sight) {
                if i >= 0 && j >= 0 && i < NUM_VERTS as i16 && j < NUM_VERTS as i16 {
                    if ((x - i) * (x - i)) + ((y - j) * (y - j)) <= sight * sight {
                        self.visible[(i + j * NUM_VERTS as i16) as usize] |= 1 << tid;
                        self.visited[(i + j * NUM_VERTS as i16) as usize] |= 1 << tid;
                    }
                }
            }
        }

        self.update_token = self.update_token.wrapping_add(1);
    }
}

impl Sector {
    pub fn sx(&self) -> i32 {
        self.sx
    }

    pub fn sy(&self) -> i32 {
        self.sy
    }

    pub fn update_token(&self) -> u8 {
        self.update_token
    }
}
