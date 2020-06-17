use crate::ui::tk::{TkError, TkResult};
use glyph_brush::rusttype::Scale;
use glyph_brush::{FontId, OwnedSectionText};
use pulldown_cmark::{Event, Parser, Tag};

pub fn parse(text: &str) -> TkResult<Vec<OwnedSectionText>> {
    let parser = Parser::new(text);

    //let mut paragraphs = Vec::<Vec::<OwnedSectionText>>::new();
    let mut text = Vec::<OwnedSectionText>::new();

    let mut gstack = Vec::<OwnedSectionText>::new();
    let mut gstate = OwnedSectionText {
        color: [1.0, 1.0, 1.0, 1.0],
        scale: Scale::uniform(18.0),
        font_id: FontId(1), // TODO - font control!
        ..OwnedSectionText::default()
    };

    for event in parser {
        match event {
            Event::Start(Tag::Emphasis) => {
                gstack.push(gstate.clone());
                gstate.color = [1.0, 1.0, 0.0, 1.0]; // yellow
            }
            Event::Start(Tag::Strong) => {
                gstack.push(gstate.clone());
                gstate.color = [1.0, 0.0, 0.0, 1.0]; // red
            }
            Event::Start(Tag::Paragraph) => {}
            Event::Start(Tag::Heading(_n)) => {
                gstack.push(gstate.clone());
                gstate.scale = Scale::uniform(24.0);
            }
            Event::End(Tag::Emphasis) | Event::End(Tag::Strong) => {
                gstate = gstack.pop().expect("gstack empty - unbalanced tags?");
            }
            Event::End(Tag::Heading(_)) => {
                gstate = gstack.pop().expect("gstack empty - unbalanced tags?");
                text.push(OwnedSectionText {
                    text: "\n\n".to_owned(),
                    ..gstate
                });
            }
            Event::End(Tag::Paragraph) => text.push(OwnedSectionText {
                text: "\n\n".to_owned(),
                ..gstate
            }),
            Event::Text(str) => {
                text.push(OwnedSectionText {
                    text: str.into_string(),
                    ..gstate
                });
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
