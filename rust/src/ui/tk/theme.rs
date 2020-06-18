use super::TextureId;
use glyph_brush::FontId;

pub trait Theme {
    fn ui_texture(&self) -> TextureId;
    fn font(&self) -> FontId;
}
