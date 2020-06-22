use crate::ui::tk::{CommandBuffer, Element, Icon, InputState, Rect, Size, TkResult, Widget};

pub struct Image<Msg> {
    bounds: Rect,
    icon: Icon,
    _msg: std::marker::PhantomData<Msg>,
}

impl<Msg: 'static> Image<Msg> {
    pub fn new(icon: Icon) -> Self {
        Image {
            bounds: Rect::default(),
            icon,
            _msg: std::marker::PhantomData,
        }
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

// TODO - move me somewhere
/// create a rectangle of a given size centered inside another rect
fn centered_rect(outer: Rect, size: Size) -> Rect {
    let border = (outer.size - size) / 2;
    Rect::new(outer.origin + border.to_vector(), size)
}

/// create a rect inside a given rect with the same aspect ratio as another
fn fit_rect(outer: Size, size: Size) -> Size {
    let scale =
        (outer.width as f32 / size.width as f32).min(outer.height as f32 / size.height as f32);
    Size::new(
        (size.width as f32 * scale) as i32,
        (size.height as f32 * scale) as i32,
    )
}

impl<Msg: 'static> Widget<Msg> for Image<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        if self.icon.texture().size == Size::zero() {
            // no texture size info, just scale to bounds
            self.bounds = bounds;
        } else {
            // try to scale the image without breaking aspect ratio
            let scaled = fit_rect(bounds.size, self.icon.texture().size);
            self.bounds = centered_rect(bounds, scaled);
        }
        Ok(())
    }

    fn render(&self, _input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        buffer.sprite(self.icon.at(self.bounds));
        Ok(())
    }
}
