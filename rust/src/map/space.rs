use pyo3::prelude::*;
use pyo3::types::PyDict;
use rstar::primitives::Rectangle;
use rstar::{RTree, RTreeObject, AABB};
use std::collections::BTreeMap;
use log::error;

type RectangleI2 = Rectangle<[i64; 2]>;

#[derive(Clone, Copy, Debug)]
struct EntityRect {
    eid: u64,
    rect: RectangleI2,
}

impl EntityRect {
    fn new(eid: u64, pos: (i64, i64), r: i64) -> Self {
        Self {
            eid,
            rect: RectangleI2::from_corners([pos.0 - r, pos.1 - r], [pos.0 + r, pos.1 + r]),
        }
    }
}

impl PartialEq for EntityRect {
    fn eq(&self, other: &Self) -> bool {
        self.eid == other.eid
    }
}

impl RTreeObject for EntityRect {
    type Envelope = <RectangleI2 as RTreeObject>::Envelope;

    fn envelope(&self) -> Self::Envelope {
        self.rect.envelope()
    }
}

#[pyclass]
pub struct Space {
    tree: RTree<EntityRect>,
    index: BTreeMap<u64, EntityRect>,
}

#[pymethods]
impl Space {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec![]
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, _kwargs: Option<&PyDict>) -> PyResult<()> {
        Ok(())
    }

    #[new]
    fn new() -> Self {
        Space {
            tree: RTree::new(),
            index: BTreeMap::new(),
        }
    }

    fn insert(&mut self, eid: u64, pos: (i64, i64), r: i64) -> PyResult<()> {
        let er = EntityRect::new(eid, pos, r);

        if self.index.contains_key(&eid) {
            error!("eid already exists in Space");
        }

        self.tree.insert(er);
        self.index.insert(eid, er);
        Ok(())
    }

    fn r#move(&mut self, eid: u64, pos: (i64, i64), r: i64) -> PyResult<()> {
        self.remove(eid)?;
        self.insert(eid, pos, r)?;
        Ok(())
    }

    fn remove(&mut self, eid: u64) -> PyResult<()> {
        if let Some(old) = self.index.remove(&eid) {
            //warn!("removing eid {}, found {:?}", eid, old);
            if self.tree.remove(&old).is_none() {
                error!("entity {} wasn't removed from the rtree", eid);
            }
        } else {
            error!("failed to remove eid {} from Space", eid);
        }

        Ok(())
    }

    fn get_in_rect(&self, min: [i64; 2], max: [i64; 2]) -> PyResult<Vec<u64>> {
        let aabb = AABB::from_corners(min, max);
        Ok(self
            .tree
            .locate_in_envelope_intersecting(&aabb)
            .map(|entity_rect| entity_rect.eid)
            .collect())
    }
}
