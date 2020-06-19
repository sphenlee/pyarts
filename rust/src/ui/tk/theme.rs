use super::Texture;
use glyph_brush::FontId;

pub trait Theme {
    fn ui_texture(&self) -> Texture;
    fn font(&self) -> FontId;
}
