use tiled::{TiledError, PropertyValue, Properties};
use crate::map::sector::{NUM_TILES, NUM_TILES_CAPACITY};
use std::collections::HashMap;
use thiserror::Error;
use pyo3::PyErr;
use log::debug;
use std::num::ParseIntError;

pub struct LoadedMap {
    pub tiles: Vec<u8>,
    pub walk: Vec<u8>,
    pub tileset: String,
}

#[derive(Error, Debug)]
pub enum MapLoadError {
    #[error("tiled error: {0}")]
    TiledError(#[from] TiledError),
    #[error("invalid map configuration: {0}")]
    BadConfig(String),
}

impl From<MapLoadError> for PyErr {
    fn from(err: MapLoadError) -> Self {
        pyo3::exceptions::IOError::py_err(err.to_string())
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

pub fn load_map(file: String) -> Result<LoadedMap, MapLoadError> {
    let map = tiled::parse_file(file.as_ref())?;

    if map.width as u16 != NUM_TILES {
        return Err(MapLoadError::BadConfig(format!("width must be {}, got {}", NUM_TILES, map.width)));
    }
    if map.height as u16 != NUM_TILES {
        return Err(MapLoadError::BadConfig(format!("height must be {}, got {}", NUM_TILES, map.height)));
    }

    let tileset0 = &map.tilesets[0];
    let mut tile_to_walk = HashMap::<u32, u8>::new();

    for tile in &tileset0.tiles {
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
            walk |= 0x03;
        }

        tile_to_walk.insert(tileset0.first_gid + tile.id, walk);
    }

    let layer0 = &map.layers[0];

    let mut tiles = Vec::<u8>::with_capacity(NUM_TILES_CAPACITY);
    let mut walk = Vec::<u8>::with_capacity(NUM_TILES_CAPACITY);

    for row in &layer0.tiles {
        for tile in row {
            tiles.push(tile.gid as u8 - 1); // tiled starts counting tiles at 1
            let mask = tile_to_walk.get(&tile.gid).copied().unwrap_or(0);
            walk.push(mask);
        }
    }

    Ok(LoadedMap {
        tiles,
        walk,
        tileset: tileset0.images[0].source.clone()
    })
}