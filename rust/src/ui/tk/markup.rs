use crate::ui::tk::{TkError, TkResult};
use glyph_brush::ab_glyph::PxScale;
use glyph_brush::{Extra, FontId, OwnedSection, OwnedText};
use pulldown_cmark::{Event, Parser, Tag};

pub fn parse(text: &str) -> TkResult<OwnedSection> {
    let parser = Parser::new(text);

    //let mut paragraphs = Vec::<Vec::<OwnedSectionText>>::new();
    let mut text = Vec::<OwnedText>::new();

    let mut gstack = Vec::<OwnedText>::new();
    let mut gstate = OwnedText::new("")
        .with_color([1.0, 1.0, 1.0, 1.0])
        .with_font_id(FontId(1))
        .with_scale(PxScale::from(18.0));

    for event in parser {
        match event {
            Event::Start(Tag::Emphasis) => {
                gstack.push(gstate.clone());
                gstate.extra.color = [1.0, 1.0, 0.0, 1.0]; // yellow
            }
            Event::Start(Tag::Strong) => {
                gstack.push(gstate.clone());
                gstate.extra.color = [1.0, 0.0, 0.0, 1.0]; // red
            }
            Event::Start(Tag::Paragraph) => {}
            Event::Start(Tag::Heading(_n)) => {
                gstack.push(gstate.clone());
                gstate.scale = PxScale::from(24.0);
            }
            Event::End(Tag::Emphasis) | Event::End(Tag::Strong) => {
                gstate = gstack.pop().expect("gstack empty - unbalanced tags?");
            }
            Event::End(Tag::Heading(_)) => {
                gstate = gstack.pop().expect("gstack empty - unbalanced tags?");
                text.push(gstate.clone().with_text("\n\n".to_owned()));
            }
            Event::End(Tag::Paragraph) => text.push(gstate.clone().with_text("\n\n".to_owned())),
            Event::Text(str) => {
                text.push(gstate.clone().with_text(&str.into_string()));
            }
            Event::SoftBreak => {}
            Event::HardBreak => {}
            event => {
                return Err(TkError::InvalidMarkup(format!("{:?}", event)));
            }
        }
    }

    Ok(OwnedSection::<Extra>::default().with_text(text))
}
