use crate::map::sector::{NUM_TILES, NUM_TILES_CAPACITY};
use pyo3::PyErr;
use std::collections::HashMap;
use thiserror::Error;
use tiled::{LayerData, Properties, PropertyValue, TiledError, Map, Tileset};
use std::num::ParseIntError;

#[pyo3::prelude::pyclass]
pub struct LoadedEnt {
    #[pyo3(get)]
    pub eid: Option<u64>,
    #[pyo3(get)]
    pub proto: String,
    #[pyo3(get)]
    pub tid: i32,
    #[pyo3(get)]
    pub x: i64,
    #[pyo3(get)]
    pub y: i64,
}

pub struct LoadedMap {
    pub tiles: Vec<u32>,
    pub walk: Vec<u8>,
    pub tileset: String,
    pub ents: Vec<LoadedEnt>,
}

#[derive(Error, Debug)]
pub enum MapLoadError {
    #[error("tiled error: {0}")]
    TiledError(#[from] TiledError),
    #[error("invalid map configuration: {0}")]
    BadConfig(String),
    #[error("map is missing a tileset named {0}")]
    MissingTileset(String),
    #[error("object name is not an eid: {0}")]
    EidParseError(#[from] ParseIntError)
}

impl From<MapLoadError> for PyErr {
    fn from(err: MapLoadError) -> Self {
        pyo3::exceptions::PyIOError::new_err(err.to_string())
    }
}

fn get_bool_property(props: &Properties, key: &str) -> Option<bool> {
    if let Some(prop) = props.get(key) {
        match prop {
            PropertyValue::BoolValue(b) => Some(*b),
            _ => None,
        }
    } else {
        None
    }
}

fn get_int_property(props: &Properties, key: &str) -> Option<i32> {
    if let Some(prop) = props.get(key) {
        match prop {
            PropertyValue::IntValue(i) => Some(*i),
            _ => None,
        }
    } else {
        None
    }
}

fn generate_walk_map(terrain: &Tileset) -> Result<HashMap<u32, u8>, MapLoadError> {
    if terrain.tiles.len() == 0 {
        return Err(MapLoadError::BadConfig("tileset has no tiles?".to_owned()));
    };

    let mut tile_to_walk = HashMap::new();

    for tile in &terrain.tiles {
        let ground = get_bool_property(&tile.properties, "Ground").unwrap_or(true);
        let sea = get_bool_property(&tile.properties, "Sea").unwrap_or(false);
        let air = get_bool_property(&tile.properties, "Air").unwrap_or(true);

        let mut walk = 0u8;
        if !ground {
            walk |= 0x01;
        }
        if !sea {
            walk |= 0x02;
        }
        if !air {
            walk |= 0x04;
        }

        tile_to_walk.insert(terrain.first_gid + tile.id, walk);
    }

    Ok(tile_to_walk)
}

fn generate_ent_map(map: &Map) -> Result<HashMap<u32, String>, MapLoadError> {
    let mut ent_map = HashMap::new();

    let objects = match map.tilesets
        .iter()
        .find(|t| t.name == "objects")
    {
        Some(tileset) => tileset,
        None => return Ok(ent_map),
    };

    if objects.tiles.len() == 0 {
        return Err(MapLoadError::BadConfig("tileset has no tiles?".to_owned()));
    };

    for tile in &objects.tiles {
        let typ = tile.tile_type.clone().ok_or_else(|| MapLoadError::BadConfig(format!("tile {} has no type", tile.id)))?;

        ent_map.insert(objects.first_gid + tile.id, typ);
    }

    Ok(ent_map)
}

pub fn load_map(file: String) -> Result<LoadedMap, MapLoadError> {
    let map = tiled::parse_file(file.as_ref())?;

    if map.width as u16 != NUM_TILES {
        return Err(MapLoadError::BadConfig(format!(
            "width must be {}, got {}",
            NUM_TILES, map.width
        )));
    }
    if map.height as u16 != NUM_TILES {
        return Err(MapLoadError::BadConfig(format!(
            "height must be {}, got {}",
            NUM_TILES, map.height
        )));
    }

    if map.tilesets.len() < 1 {
        return Err(MapLoadError::BadConfig(
            "expected at least 1 tileset".to_owned(),
        ));
    };

    let terrain = map.tilesets
        .iter()
        .find(|t| t.name == "terrain")
        .ok_or_else(|| MapLoadError::MissingTileset("terrain".to_owned()))?;

    let tile_to_walk = generate_walk_map(&terrain)?;
    let ent_map = generate_ent_map(&map)?;

    if map.layers.len() != 1 {
        return Err(MapLoadError::BadConfig(
            "expected exactly 1 layer".to_owned(),
        ));
    };

    // terrain layer
    let layer0 = &map.layers[0];

    let mut tiles = Vec::with_capacity(NUM_TILES_CAPACITY);
    let mut walk = Vec::with_capacity(NUM_TILES_CAPACITY);

    let rows = match layer0.tiles {
        LayerData::Finite(ref rows) => rows,
        LayerData::Infinite(_) => panic!("can't support infinite maps"),
    };

    for row in rows {
        for tile in row {
            tiles.push(tile.gid - terrain.first_gid); // tiled starts counting tiles at 1
            let mask = tile_to_walk.get(&tile.gid).copied().unwrap_or(0x02);
            walk.push(mask);
        }
    }

    let mut ents = vec![];
    if map.object_groups.len() == 1 {
        // object layer
        let entities = &map.object_groups[0];
        
        for obj in &entities.objects {
            let proto = ent_map
                .get(&obj.gid)
                .ok_or_else(|| MapLoadError::BadConfig(
                        format!("object {} type not found", obj.id))
                    )?.clone();

            let eid = if obj.name.is_empty() {
                None
            } else {
                Some(obj.name.parse()?)
            };

            let team = get_int_property(&obj.properties, "Team").unwrap_or(0);

            let ent = LoadedEnt {
                x: obj.x as i64,
                y: obj.y as i64,
                eid,
                proto,
                tid: team,
            };
            ents.push(ent);   
        }
    }

    Ok(LoadedMap {
        tiles,
        walk,
        tileset: "".to_owned(), //tileset0.images[0].source.clone()
        ents
    })
}
