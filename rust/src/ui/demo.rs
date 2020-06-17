use crate::scene;
use crate::ui::ggez_renderer::GgezRenderer;
use crate::ui::tk::{self, *};
use ggez::graphics::Font;
use ggez::{Context, GameResult};
use crate::ui::demo::DemoMsg::AbilityButton;

#[derive(Clone, PartialEq)]
pub enum DemoMsg {
    Button1Click,
    Button2Click,
    AbilityButton(i32),
}

pub struct Demo {
    ggez_rend: GgezRenderer,
    input: InputState,
    events: Vec<Event>,
    bounds: Rect,

    //ui_tex: TextureId,
    archer: TextureId,
}

impl Demo {
    pub fn new(ctx: &mut Context) -> GameResult<Self> {
        let mut ggez_rend = GgezRenderer::new(ctx);

        let _ui_tex = ggez_rend.load_texture(ctx, "/maps/test/res/ui.png")?;
        let archer = ggez_rend.load_texture(ctx, "/maps/test/res/unit-archer.png")?;

        let _font = Font::new(ctx, "/maps/test/res/AccanthisadfstdBold-BYzx.ttf")?;

        Ok(Demo {
            ggez_rend,
            input: InputState::default(),
            events: Vec::new(),
            bounds: rect(200, 200, 512, 800),
            archer,
        })
    }

    pub fn render(&mut self, ctx: &mut Context) -> GameResult<impl Iterator<Item = DemoMsg>> {
        let mut root = self.build()?;

        root.layout(self.bounds)?;

        let (tx, rx) = std::sync::mpsc::channel();
        for event in self.events.drain(..) {
            root.event(&event, &tx)?;
        }

        let mut buf = CommandBuffer::default();
        root.render(&self.input, &mut buf)?;

        for cmd in buf {
            self.ggez_rend.do_command(ctx, cmd)?;
        }

        Ok(rx.into_iter())
    }

    pub fn event(&mut self, event: &scene::Event) {
        // TODO - check buttons (left/right)
        match event {
            scene::Event::MouseDown { .. } => {
                self.input.mouse_button = MouseButton::Left;
            }
            scene::Event::MouseUp { x, y, .. } => {
                self.events
                    .push(Event::Click(point(*x as i32, *y as i32), MouseButton::Left));
                self.input.mouse_button = MouseButton::None;
            }
            scene::Event::MouseMotion { x, y, .. } => {
                self.input.mouse_pos = point(*x as i32, *y as i32);
            }
            _ => return,
        };
    }

    fn build(&self) -> TkResult<Element<DemoMsg>> {
        let top = Panel::hbox()
            .add(Button::new().onclick(DemoMsg::Button1Click))
            .add_flex(2, Button::new().onclick(DemoMsg::Button2Click))
            .add(Button::new().icon(self.archer.whole()));

        let left = Panel::vbox()
            .add(top)
            .add(Button::new().text("Click Me!"))
            .add_flex(
                14,
                Border::new(Text::new(
                    "\
                # *Important* Information\n\
                \n\
                Lorem ipsum *dolor* sit amet, consectetur adipiscing elit,\
                sed do eiusmod tempor i*ncididunt* ut labore \
                et dolore magna aliqua. Ut enim ad minim veniam,\n\
                quis nostrud exercitation ullamco laboris nisi ut \
                aliquip ex ea commodo consequat.\n\
                \n\
                Duis aute irure \
                dolor in repre*hend*erit in voluptate velit esse \
                cillum dolore eu **fugiat** nulla pariatur. Excepteur \
                sint occaecat cupidatat non proident, sunt in \
                culpa qui officia deserunt mollit anim id est laborum. \
            ",
                )),
            );

        let panel = Panel::hbox().add(left).add(
            Panel::vbox()
                .add(
                    Panel::hbox()
                        .add(Button::new().onclick(AbilityButton(0)))
                        .add(Button::new().onclick(AbilityButton(1)))
                        .add(Button::new().onclick(AbilityButton(2))),
                )
                .add(
                    Panel::hbox()
                        .add(Button::new().onclick(AbilityButton(3)))
                        .add(Button::new().onclick(AbilityButton(4)))
                        .add(Button::new().onclick(AbilityButton(5))),
                )
                .add(
                    Panel::hbox()
                        .add(Button::new().onclick(AbilityButton(6)))
                        .add(Button::new().onclick(AbilityButton(7)))
                        .add(Button::new().onclick(AbilityButton(8))),
                ),
        );

        Ok(panel.build())
    }
}
