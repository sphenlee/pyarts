use ggez::graphics::{DrawParam, Text};
use super::Sprite;

#[derive(Debug)]
pub enum Command {
    Sprite(Sprite),
    Text(Text, DrawParam),
}

#[derive(Default)]
pub struct CommandBuffer {
    commands: Vec<Command>,
}

impl CommandBuffer {
    pub fn sprite(&mut self, sprite: impl Into<Sprite>) {
        self.commands.push(Command::Sprite(sprite.into()));
    }

    pub fn text(&mut self, section: Text, param: DrawParam) {
        self.commands.push(Command::Text(section, param));
    }
}

impl IntoIterator for CommandBuffer {
    type Item = Command;
    type IntoIter = <Vec<Command> as IntoIterator>::IntoIter;

    fn into_iter(self) -> Self::IntoIter {
        self.commands.into_iter()
    }
}
