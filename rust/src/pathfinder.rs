use log::{debug, error, warn};
use pathfinding::directed::dijkstra;
use pyo3::prelude::*;
use pyo3::types::PyDict;

use crate::map::sector_renderer::VERTEX_SZ;
use pyo3::PyNativeType;

type Cost = i32;

#[derive(PartialEq, Eq, Hash, Clone, Copy, Debug)]
struct Pt(i64, i64);

const NEIGHBORS: &[(i64, i64)] = &[(0, 1), (1, 0), (0, -1), (-1, 0)];

impl Pt {
    fn successors(&self, map: &PyAny, walk: u8) -> impl IntoIterator<Item = (Pt, Cost)> {
        NEIGHBORS
            .iter()
            .map(|(dx, dy)| Pt(self.0 + *dx, self.1 + *dy))
            .filter_map(|pt| {
                let walkable: bool = map
                    .call_method1("cell_walkable", (walk, pt.0, pt.1))
                    .unwrap()
                    .extract()
                    .unwrap();
                if walkable {
                    Some((pt, 1))
                } else {
                    None
                }
            })
            .collect::<Vec<_>>()
    }

    fn dist(&self, other: Pt) -> i64 {
        (self.0 - other.0) * (self.0 - other.0) + (self.1 - other.1) * (self.1 - other.1)
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

    #[args(range = "0.0")]
    fn findpath(
        &mut self,
        py: Python,
        start: (f32, f32),
        goal: (f32, f32),
        walk: u8,
        range: f32,
    ) -> PyResult<Vec<(f32, f32)>> {
        // first convert the raw points into cells
        let start = Pt((start.0 / VERTEX_SZ) as i64, (start.1 / VERTEX_SZ) as i64);
        let goal = Pt((goal.0 / VERTEX_SZ) as i64, (goal.1 / VERTEX_SZ) as i64);
        let range = (range / VERTEX_SZ) as i64;

        info!(
            "pathfinding from {:?} to {:?}, range of {}",
            start, goal, range
        );

        let (path_map, found) = dijkstra::dijkstra_partial(
            &start,
            |node| node.successors(self.map.as_ref(py), walk),
            |node| node.dist(goal) < range,
        );

        let path = if let Some(goal) = found {
            debug!("found path to goal");
            dijkstra::build_path(&goal, &path_map)
        } else {
            warn!("no path to goal! finding closest approach");
            match path_map.keys().min_by_key(|node| node.dist(goal)) {
                Some(closest) => dijkstra::build_path(closest, &path_map),
                None => {
                    error!("no closest approach - unit is stuck?");
                    vec![]
                }
            }
        };

        Ok(path
            .into_iter()
            .map(|pt| (pt.0 as f32 * VERTEX_SZ, pt.1 as f32 * VERTEX_SZ))
            .collect())
    }
}
