// use crate::ui::ggez_renderer::GgezRenderer;
// use crate::ui::tk::*;
// use ggez::{Context, GameResult};
// use crate::ui::ui::DemoMsg::AbilityButton;
//
// #[derive(Clone, PartialEq)]
// pub enum DemoMsg {
//     Button1Click,
//     Button2Click,
//     AbilityButton(i32),
// }
//
// pub struct UI {
//     ggez_rend: GgezRenderer,
//     bounds: Rect,
//     archer: TextureId,
//     counter: i32,
// }
//
// impl UI {
//     pub fn new(ctx: &mut Context, bounds: Rect) -> GameResult<Self> {
//         let mut ggez_rend = GgezRenderer::new(ctx)?;
//
//         let archer = ggez_rend.load_texture(ctx, "/maps/test/res/unit-archer.png")?;
//
//         Ok(UI {
//             ggez_rend,
//             bounds, //rect(200, 200, 512, 512)
//             archer,
//             counter: 0
//         })
//     }
//
//     pub fn render(&mut self, ctx: &mut Context) -> GameResult<impl Iterator<Item = DemoMsg>> {
//         let root = self.build()?;
//
//         self.ggez_rend.render(ctx, root, self.bounds)
//     }
//
//     fn build(&self) -> TkResult<Element<DemoMsg>> {
//         let top = Panel::hbox()
//             .add(Button::new().onclick(DemoMsg::Button1Click))
//             .add_flex(2, Button::new().onclick(DemoMsg::Button2Click))
//             .add(Button::new().icon(self.archer.whole()));
//
//         let left = Panel::vbox()
//             .add(top)
//             .add(Button::new().text("Click Me!"))
//             .add_flex(
//                 14,
//                 Border::new(Text::new(
//                     "\
//                 # *Important* Information\n\
//                 \n\
//                 Lorem ipsum *dolor* sit amet, consectetur adipiscing elit,\
//                 sed do eiusmod tempor i*ncididunt* ut labore \
//                 et dolore magna aliqua. Ut enim ad minim veniam,\n\
//                 quis nostrud exercitation ullamco laboris nisi ut \
//                 aliquip ex ea commodo consequat.\n\
//                 \n\
//                 Duis aute irure \
//                 dolor in repre*hend*erit in voluptate velit esse \
//                 cillum dolore eu **fugiat** nulla pariatur. Excepteur \
//                 sint occaecat cupidatat non proident, sunt in \
//                 culpa qui officia deserunt mollit anim id est laborum. \
//             ",
//                 )),
//             );
//
//         let panel = Panel::hbox().add(left).add(
//             Panel::vbox()
//                 .add(
//                     Panel::hbox()
//                         .add(Button::new().onclick(AbilityButton(0)))
//                         .add(Button::new().onclick(AbilityButton(1)))
//                         .add(Button::new().onclick(AbilityButton(2))),
//                 )
//                 .add(
//                     Panel::hbox()
//                         .add(Button::new().onclick(AbilityButton(3)))
//                         .add(Button::new().onclick(AbilityButton(4)))
//                         .add(Button::new().onclick(AbilityButton(5))),
//                 )
//                 .add(
//                     Panel::hbox()
//                         .add(Button::new().onclick(AbilityButton(6)))
//                         .add(Button::new().onclick(AbilityButton(7)))
//                         .add(Text::new(format!("{}", self.counter))),
//                 ),
//         );
//
//         Ok(panel.build())
//     }
// }
