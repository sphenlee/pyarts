use ggez::graphics::{Color, PxScale, Text, TextFragment};
use crate::ui::tk::{TkError, TkResult};
//use glyph_brush::ab_glyph::PxScale;
//use glyph_brush::{Extra, FontId, OwnedSection, OwnedText};
use pulldown_cmark::{Event, Parser, Tag};

#[derive(Clone)]
struct GState {
    color: Color,
    font: Option<String>,
    scale: PxScale,
}

pub fn parse(text: &str) -> TkResult<Text> {
    let parser = Parser::new(text);

    //let mut paragraphs = Vec::<Vec::<OwnedSectionText>>::new();
    let mut text = Text::default();

    let mut gstack = Vec::<GState>::new();
    let mut gstate = GState {
        color: [1.0, 1.0, 1.0, 1.0].into(),
        font: None,
        scale: 18.0.into(),
    };

    for event in parser {
        match event {
            Event::Start(Tag::Emphasis) => {
                gstack.push(gstate.clone());
                gstate.color = [1.0, 1.0, 0.0, 1.0].into(); // yellow
            }
            Event::Start(Tag::Strong) => {
                gstack.push(gstate.clone());
                gstate.color = [1.0, 0.0, 0.0, 1.0].into(); // red
            }
            Event::Start(Tag::Paragraph) => {}
            Event::Start(Tag::Heading(_n)) => {
                gstack.push(gstate.clone());
                gstate.scale = 24.0.into();
            }
            Event::End(Tag::Emphasis) | Event::End(Tag::Strong) => {
                gstate = gstack.pop().expect("gstack empty - unbalanced tags?");
            }
            Event::End(Tag::Heading(_)) => {
                gstate = gstack.pop().expect("gstack empty - unbalanced tags?");
                text.add(TextFragment::new("\n\n")
                    .color(gstate.color)
                    .scale(gstate.scale)
                );
            }
            Event::End(Tag::Paragraph) => {
                text.add(
                    TextFragment::new("\n\n")
                        .color(gstate.color)
                        .scale(gstate.scale)
                );
            },
            Event::Text(str) => {
                text.add(
                    TextFragment::new(&str.into_string())
                        .color(gstate.color)
                        .scale(gstate.scale)
                );
            }
            Event::SoftBreak => {}
            Event::HardBreak => {}
            event => {
                return Err(TkError::InvalidMarkup(format!("{:?}", event)));
            }
        }
    }

    Ok(text)
}
