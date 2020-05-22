use pyo3::prelude::*;
use pyo3::types::PyBytes;

pub const NUM_TILES: u16 = 32;
pub const NUM_VERTS: u16 = NUM_TILES + 1;

pub const NUM_VERTS_CAPACITY: usize = (NUM_VERTS * NUM_VERTS) as usize;


#[pyclass(module="yarts")]
pub struct Sector {
    #[pyo3(get)]
    sx: i32,
    #[pyo3(get)]
    sy: i32,
    tiles: Vec<u8>,
    visited: Vec<u8>,
    visible: Vec<u8>,
    walk: Vec<u8>,
}

#[pymethods]
impl Sector {
    #[new]
    pub fn new(
        sx: i32,
        sy: i32,
        tiles: &PyBytes,
        visited: Option<&PyBytes>,
        walk: Option<&PyBytes>,
    ) -> Self {
        Sector {
            sx,
            sy,
            tiles: tiles.as_bytes().to_owned(),
            visited: visited.map(|bytes| bytes.as_bytes().to_owned()).unwrap_or_else(|| vec![0u8; NUM_VERTS_CAPACITY]),
            visible: vec![0u8; NUM_VERTS_CAPACITY],
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

    fn clear_fog(&mut self) {
        self.visible.iter_mut().for_each(|x| *x = 0);
    }

    fn update_fog(&mut self, x: i16, y: i16, sight: i16, tid: u8) {
        for i in (x - sight) .. (x + sight) {
            for j in (y - sight) .. (y + sight) {
                if i >= 0 && j >= 0 && i < NUM_VERTS as i16 && j < NUM_VERTS as i16 {
                    if ((x-i)*(x-i)) + ((y-j)*(y-j)) < sight*sight {
                        self.visible[(i + j * NUM_VERTS as i16) as usize] |= 1 << tid;
                        self.visited[(i + j * NUM_VERTS as i16) as usize] |= 1 << tid;
                    }
                }
            }
        }
    }
}

impl Sector {
    pub fn copy_tiles(&self, out: &mut [u8]) {
        assert_eq!(out.len(), self.tiles.len());
        out.copy_from_slice(&self.tiles);
    }

    pub fn copy_visible(&self, out: &mut [u8]) {
        assert_eq!(out.len(), self.visible.len());
        out.copy_from_slice(&self.visible);
    }

    pub fn copy_visited(&self, out: &mut [u8]) {
        assert_eq!(out.len(), self.visited.len());
        out.copy_from_slice(&self.visited);
    }
}
