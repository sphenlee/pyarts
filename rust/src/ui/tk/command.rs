use super::Sprite;
use glyph_brush::OwnedVariedSection;

#[derive(Debug)]
pub enum Command {
    Sprite(Sprite),
    Text(OwnedVariedSection),
}

#[derive(Default)]
pub struct CommandBuffer {
    commands: Vec<Command>,
}

impl CommandBuffer {
    pub fn sprite(&mut self, sprite: impl Into<Sprite>) {
        self.commands.push(Command::Sprite(sprite.into()));
    }

    pub fn text(&mut self, section: OwnedVariedSection) {
        self.commands.push(Command::Text(section));
    }
}

impl IntoIterator for CommandBuffer {
    type Item = Command;
    type IntoIter = <Vec<Command> as IntoIterator>::IntoIter;

    fn into_iter(self) -> Self::IntoIter {
        self.commands.into_iter()
    }
}
