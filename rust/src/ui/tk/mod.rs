use euclid;
use thiserror::Error;

mod border;
mod button;
mod command;
mod image;
mod input;
mod markup;
mod panel;
mod popup;
mod text;
mod theme;
mod widget;
mod progress;

pub use border::Border;
pub use button::Button;
pub use command::{Command, CommandBuffer};
pub use image::{Icon, Sprite, TextureId};
pub use input::{Event, InputState, MouseButton};
pub use panel::Panel;
pub use popup::Popup;
pub use progress::Progress;
pub use text::Text;
pub use widget::{Element, Widget};

pub type Point = euclid::default::Point2D<i32>;
pub type Rect = euclid::default::Rect<i32>;
pub type Size = euclid::default::Size2D<i32>;
pub use euclid::{point2 as point, rect, size2 as size};

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
