use euclid;
use thiserror::Error;

mod command;
mod image;
mod input;
mod markup;
mod theme;
mod widget;
mod widgets;

pub use command::{Command, CommandBuffer};
pub use image::{Icon, Sprite, Texture};
pub use input::{Event, InputState, MouseButton};
pub use widget::{Element, Widget};
pub use widgets::*;

pub type Point = euclid::default::Point2D<i32>;
pub type Rect = euclid::default::Rect<i32>;
pub type Size = euclid::default::Size2D<i32>;
pub type Vector = euclid::default::Vector2D<i32>;
pub use euclid::rect;

pub type TkResult<T> = Result<T, TkError>;

#[derive(Error, Debug)]
pub enum TkError {
    #[error("Invalid markup: {0}")]
    InvalidMarkup(String),
    #[error("Error sending event")]
    SendError,
    #[error("Other error: {0}")]
    Other(String),
}
