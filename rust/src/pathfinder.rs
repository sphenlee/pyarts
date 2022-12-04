use log::{debug, error, info, trace, warn};
use pathfinding::directed::dijkstra;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::map::sector_renderer::VERTEX_SZ;

const CELL_FACTOR: i64 = VERTEX_SZ as i64;

type Cost = i32;

#[derive(PartialEq, Eq, Hash, Clone, Copy, Debug)]
struct Pt(i64, i64);

const NEIGHBORS: &[(i64, i64)] = &[
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
    (1, 1),
    (1, -1),
    (-1, -1),
    (-1, 1),
];
const COSTS: &[Cost] = &[2, 2, 2, 2, 3, 3, 3, 3];

impl Pt {
    fn successors(&self, map: &PyAny, walk: u8) -> impl IntoIterator<Item = (Pt, Cost)> {
        NEIGHBORS
            .iter()
            .zip(COSTS)
            .map(|(&dxy, &c)| (self.offset(dxy), c))
            .filter_map(|(pt, c)| {
                let walkable: bool = map
                    .call_method1("cell_walkable", (walk, pt.0, pt.1))
                    .unwrap()
                    .extract()
                    .unwrap();
                if walkable {
                    Some((pt, c))
                } else {
                    None
                }
            })
            .collect::<Vec<_>>()
    }

    fn dist(&self, other: Pt) -> i64 {
        (self.0 - other.0) * (self.0 - other.0) + (self.1 - other.1) * (self.1 - other.1)
    }

    fn to_pos(&self) -> (i64, i64) {
        (self.0 * CELL_FACTOR, self.1 * CELL_FACTOR)
    }

    fn offset(&self, dxy: (i64, i64)) -> Self {
        Pt(self.0 + dxy.0, self.1 + dxy.1)
    }
}

impl From<(i64, i64)> for Pt {
    fn from(pos: (i64, i64)) -> Self {
        Pt(pos.0 / CELL_FACTOR, pos.1 / CELL_FACTOR)
    }
}

#[pyclass]
pub struct Pathfinder {
    map: PyObject,
}

#[pymethods]
impl Pathfinder {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["map"]
    }

    #[new]
    fn new(py: Python) -> Self {
        Pathfinder { map: py.None() }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, _py: Python, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        self.map = deps.get_item("map")?.into();
        Ok(())
    }

    #[args(range = "0")]
    fn findpath(
        &mut self,
        py: Python,
        start: (i64, i64),
        goal: (i64, i64),
        walk: u8,
        range: i64,
    ) -> PyResult<Vec<(i64, i64)>> {
        // first convert the raw points into cells
        let start_pt = Pt::from(start);
        let goal_pt = Pt::from(goal);
        let range = range / CELL_FACTOR;

        // don't consider any nodes that are 2x further away than the goal
        // otherwise we have to travsese the entire map to determine that no
        // path exists in trivial cases eg. goal is in the water
        let search_radius = start_pt.dist(goal_pt) * 2;
        info!(
            "pathfinding from {:?} to {:?}, range of {}",
            start_pt, goal_pt, range
        );

        let (path_map, found) = dijkstra::dijkstra_partial(
            &start_pt,
            |node| {
                node.successors(self.map.as_ref(py), walk)
                    .into_iter()
                    .filter(|(pt, _cost)| pt.dist(goal_pt) < search_radius)
            },
            |node| node.dist(goal_pt) <= range,
        );

        let path = if let Some(goal) = found {
            debug!("found path to goal");
            dijkstra::build_path(&goal, &path_map)
        } else {
            warn!("no path to goal! finding closest approach");
            match path_map.keys().min_by_key(|node| node.dist(goal_pt)) {
                Some(closest) => {
                    trace!(
                        "closest approach is {:?}@{}",
                        closest,
                        closest.dist(goal_pt)
                    );
                    if closest.dist(goal_pt) >= start_pt.dist(goal_pt) {
                        warn!("can't get any closer");
                        vec![]
                    } else {
                        dijkstra::build_path(closest, &path_map)
                    }
                }
                None => {
                    error!("no closest approach - unit is stuck?");
                    vec![]
                }
            }
        };

        // skip the first path point - it moves us from start to the centre of the start cell
        let mut result = path
            .into_iter()
            .skip(1)
            .map(|pt| pt.to_pos())
            .collect::<Vec<_>>();

        if found.is_some() && range == 0 {
            // update the goal cell with the actual goal pos (if we found the goal)
            match result.last_mut() {
                Some(last) => *last = goal,
                None => {}
            };
        }

        trace!("path is: {:?}", result);
        Ok(result)
    }
}
