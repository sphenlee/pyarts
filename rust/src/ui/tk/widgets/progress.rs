use ggez::graphics::{DrawParam, Text, TextFragment, TextLayout};
use crate::ui::tk::{rect, CommandBuffer, Element, InputState, Rect, Texture, TkResult, Widget};

const PROGRESS_OFFSET_X: i32 = 0;
const PROGRESS_OFFSET_Y: i32 = 192;
const PROGRESS_WIDTH: i32 = 192;
const PROGRESS_HEIGHT: i32 = 32;

pub struct Progress<Msg> {
    text: String,
    percentage: f32,
    bounds: Rect,
    _msg: std::marker::PhantomData<Msg>,
}

impl<Msg: 'static> Progress<Msg> {
    pub fn new() -> Self {
        Progress {
            text: String::new(),
            percentage: 0.0,
            bounds: Rect::default(),
            _msg: std::marker::PhantomData,
        }
    }

    pub fn fraction(val: i32, max: i32) -> Self {
        Self::new()
            .text(format!("{} / {}", val, max))
            .percentage(val as f32 / max as f32)
    }

    pub fn text(mut self, text: impl Into<String>) -> Self {
        self.text = text.into();
        self
    }

    pub fn percentage(mut self, percentage: f32) -> Self {
        // TODO - better name? it's not out of 100
        self.percentage = percentage;
        self
    }

    pub fn build(self) -> Element<Msg> {
        Box::new(self)
    }
}

impl<Msg: 'static> Widget<Msg> for Progress<Msg> {
    fn layout(&mut self, bounds: Rect) -> TkResult<()> {
        self.bounds = bounds;
        Ok(())
    }

    fn render(&self, _input: &InputState, buffer: &mut CommandBuffer) -> TkResult<()> {
        let uv_bar = rect(
            PROGRESS_OFFSET_X,
            PROGRESS_OFFSET_Y + PROGRESS_HEIGHT,
            PROGRESS_WIDTH,
            PROGRESS_HEIGHT,
        );
        let uv_fill = rect(
            PROGRESS_OFFSET_X,
            PROGRESS_OFFSET_Y,
            PROGRESS_WIDTH,
            PROGRESS_HEIGHT,
        );

        let offset_y = 0; //(self.bounds.size.height - PROGRESS_HEIGHT) / 2;

        let bar = rect(
            self.bounds.origin.x,
            self.bounds.origin.y + offset_y,
            self.bounds.size.width,
            self.bounds.size.height,
        );
        let fill = rect(
            self.bounds.origin.x,
            self.bounds.origin.y + offset_y,
            (self.bounds.size.width as f32 * self.percentage) as i32,
            self.bounds.size.height,
        );

        buffer.sprite(Texture::from_id(0).icon(uv_bar).at(bar));
        buffer.sprite(Texture::from_id(0).icon(uv_fill).at(fill));

        if !self.text.is_empty() {
            let pos = self.bounds.center().to_tuple();

            let frag = TextFragment::new(&self.text)
                .color([1.0, 1.0, 1.0, 1.0])
                .scale(18.0);

            let mut text = Text::new(frag);
            text.set_bounds([
                self.bounds.size.width as f32,
                self.bounds.size.height as f32,
            ])
            .set_layout(TextLayout::center());

            /*
            sec.with_bounds((
                    self.bounds.size.width as f32,
                    self.bounds.size.height as f32,
                ))
                .with_screen_position((pos.0 as f32, pos.1 as f32))
                .with_layout(Layout::SingleLine {
                    line_breaker: BuiltInLineBreaker::AnyCharLineBreaker,
                    h_align: HorizontalAlign::Center,
                    v_align: VerticalAlign::Center,
                })
                .add_text(
                    OwnedText::new(&self.text)
                        .with_color([1.0, 1.0, 1.0, 1.0])
                        .with_font_id(FontId(1))
                        .with_scale(PxScale::from(18.0)),
                );
*/
            buffer.text(text, DrawParam::new().dest([pos.0 as f32, pos.1 as f32]));
        }

        Ok(())
    }
}
