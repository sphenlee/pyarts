use super::Point;

#[derive(PartialEq, Debug, Copy, Clone)]
pub enum MouseButton {
    None,
    Left,
}

impl Default for MouseButton {
    fn default() -> Self {
        MouseButton::None
    }
}

#[derive(Default, Debug)]
pub struct InputState {
    pub mouse_pos: Point,
    pub mouse_button: MouseButton,
}

#[derive(PartialEq, Debug)]
#[non_exhaustive]
pub enum Event {
    Click(Point, MouseButton),
    #[doc(hidden)]
    __NonExhaustive,
}
