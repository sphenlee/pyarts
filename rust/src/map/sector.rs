use pyo3::prelude::*;
use pyo3::types::PyBytes;

pub const NUM_TILES: u16 = 32;
pub const NUM_VERTS: u16 = NUM_TILES + 1;


#[pyclass(module="yarts")]
pub struct Sector {
    sx: i32,
    sy: i32,
    tiles: Vec<u8>,
    visited: Vec<u8>,
    visible: Vec<u8>,
    walk: Vec<u8>,
}

#[pymethods]
impl Sector {
    #[new]
    pub fn new(sx: i32, sy: i32, tiles: &PyBytes, visited: Option<&PyBytes>, walk: Option<&PyBytes>) -> Self {
        Sector {
            sx,
            sy,
            tiles: tiles.as_bytes().to_owned(),
            visited: visited.map(|bytes| bytes.as_bytes().to_owned()).unwrap_or_else(Vec::new),
            visible: vec![0u8; (NUM_VERTS * NUM_VERTS) as usize],
            walk: walk.map(|bytes| bytes.as_bytes().to_owned()).unwrap_or_else(Vec::new),
        }
    }

    fn footprint(&mut self, _x: u64, _y: u64, _r: u64) {
        // TODO
    }

    pub fn tile(&mut self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_TILES * pt.1;
        self.tiles[idx as usize]
    }

    fn visible(&mut self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_VERTS * pt.1;
        self.visible[idx as usize]
    }

    fn visited(&mut self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_VERTS * pt.1;
        self.visited[idx as usize]
    }

    fn walk(&mut self, pt: (u16, u16)) -> u8 {
        let idx = pt.0 + NUM_VERTS * pt.1;
        self.walk[idx as usize]
    }

    fn update_fog(&mut self, _x: u64, _y: u64, _sight: u64, _tid: u8) {

    }
}
