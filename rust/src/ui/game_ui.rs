use crate::scene::{HEIGHT_I, WIDTH_I};
use crate::ui::ggez_renderer::GgezRenderer;
use crate::ui::tk::*;
use crate::util::YartsResult;
use ggez::Context;
use ggez::graphics::{Canvas, TextAlign};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};

const ABILITY_BUTTON: i32 = 96;

#[derive(Clone, Debug)]
pub enum GameMsg {
    AbilityButton(usize),
}

#[pyclass]
pub struct GameUi {
    infopanel: PyObject,
    abilitypanel: PyObject,
    townspanel: PyObject,
    camera: PyObject,
    messages: Vec<GameMsg>,
}

#[pymethods]
impl GameUi {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["infopanel", "abilitypanel", "townspanel", "camera"]
    }

    #[new]
    fn new(py: Python) -> GameUi {
        GameUi {
            infopanel: py.None(),
            abilitypanel: py.None(),
            townspanel: py.None(),
            camera: py.None(),
            messages: vec![],
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        self.infopanel = deps.get_item("infopanel")?.into();
        self.abilitypanel = deps.get_item("abilitypanel")?.into();
        self.townspanel = deps.get_item("townspanel")?.into();
        self.camera = deps.get_item("camera")?.into();

        Ok(())
    }
}

// small helper functions - maybe move to a pyo3 helpers module?
fn dict_get_or_else<'a, K, T, F>(dict: &'a PyDict, key: K, f: F) -> PyResult<T>
where
    K: pyo3::ToBorrowedObject,
    T: FromPyObject<'a>,
    F: FnOnce() -> T,
{
    match dict.get_item(key) {
        None => Ok(f()),
        Some(item) => item.extract::<T>(),
    }
}

fn dict_get_or_default<'a, K, T>(dict: &'a PyDict, key: K) -> PyResult<T>
where
    K: pyo3::ToBorrowedObject,
    T: FromPyObject<'a> + Default,
{
    dict_get_or_else(dict, key, || Default::default())
}

fn dict_get<'a, K, T>(dict: &'a PyDict, key: K) -> PyResult<Option<T>>
where
    K: pyo3::ToBorrowedObject,
    T: FromPyObject<'a>,
{
    // this is basically a map and transpose, but I think this is easier to read
    Ok(match dict.get_item(key) {
        None => None,
        Some(item) => Some(item.extract::<T>()?),
    })
}

impl GameUi {
    pub fn step(&mut self, py: Python) -> YartsResult<()> {
        self.infopanel.call_method1(py, "step", ())?;
        self.abilitypanel.call_method1(py, "step", ())?;
        Ok(())
    }

    pub fn messages<'a>(&'a mut self) -> impl Iterator<Item = GameMsg> + 'a {
        self.messages.drain(..)
    }

    pub fn draw(
        &mut self,
        py: Python,
        ctx: &mut Context,
        canvas: &mut Canvas,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<()> {
        let infopanel = self.build_infopanel(py, ctx, ggez_rend)?;
        let abilitypanel = self.build_abilitypanel(py, ctx, ggez_rend)?;
        let townspanel = self.build_townspanel(py, ctx, ggez_rend)?;

        let ui = Stack::new()
            .add(
                Popup::new()
                    .anchor(Point::new(0, HEIGHT_I / 4 * 3))
                    .size(Size::new(WIDTH_I / 6, HEIGHT_I / 4))
                    .add(infopanel),
            )
            .add(
                Popup::new()
                    .anchor(Point::new(
                        WIDTH_I - ABILITY_BUTTON * 5,
                        HEIGHT_I - ABILITY_BUTTON * 2,
                    ))
                    .size(Size::new(ABILITY_BUTTON * 5, ABILITY_BUTTON * 2))
                    .add(abilitypanel),
            )
            .add(townspanel)
            .build();

        let messages = ggez_rend.render(
            ctx,
            canvas,
            ui,
            rect(0, 0, WIDTH_I, HEIGHT_I)
        )?;
        self.messages.extend(messages);

        Ok(())
    }

    fn build_infopanel(
        &mut self,
        py: Python,
        ctx: &mut Context,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<impl Widget<GameMsg> + 'static> {
        let entities: &PyList = self.infopanel.as_ref(py).getattr("data")?.extract()?;

        if entities.len() == 1 {
            let data: &PyDict = entities.get_item(0).extract()?;

            // name
            let name: String = dict_get_or_default(data, "name")?;
            let mut info = Panel::vbox().add(Text::new(name)?.halign(TextAlign::Middle));

            // portrait
            let portrait: Option<String> = dict_get(data, "portrait")?;
            if let Some(image) = portrait {
                let texid = ggez_rend.load_texture(ctx, &image)?;
                info.push(2, Image::new(texid.whole()))
            }

            // hp
            let hp: Option<(i32, i32)> = dict_get(data, "hp")?;
            if let Some((val, max)) = hp {
                info.push(1, Progress::fraction(val, max));
            }

            // mana
            let mana: Option<(i32, i32)> = dict_get(data, "mana")?;
            if let Some((val, max)) = mana {
                info.push(1, Progress::fraction(val, max));
            }

            /*let panel = Panel::hbox().add(info)
               .add_flex(2, Panel::vbox())
               ;
            */

            Ok(Border::new(info))
        } else {
            let mut grid = Grid::new(3, 5);

            for ent in entities {
                let data: &PyDict = ent.extract()?;

                // portrait
                let portrait: Option<String> = dict_get(data, "portrait")?;
                if let Some(image) = portrait {
                    let texid = ggez_rend.load_texture(ctx, &image)?;
                    grid.push(Image::new(texid.whole()))
                }
            }

            Ok(Border::new(grid))
        }
    }

    fn build_abilitypanel(
        &mut self,
        py: Python,
        ctx: &mut Context,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<impl Widget<GameMsg> + 'static> {
        let abilities: &PyList = self.abilitypanel.as_ref(py).getattr("data")?.extract()?;

        let mut grid = Grid::new(2, 5);

        for (idx, a) in abilities.iter().enumerate() {
            let data: &PyDict = a.extract()?;

            let mut button = Button::new().onclick(GameMsg::AbilityButton(idx));
            let mut wait_animation = None;

            let image: Option<String> = dict_get(data, "image")?;
            if let Some(image) = image {
                let texid = ggez_rend.load_texture(ctx, &image)?;
                button = button.icon(texid.whole());
            }

            let cooldown: Option<f32> = dict_get(data, "cooldown")?;
            if let Some(cooldown) = cooldown {
                button = button.enabled(cooldown == 0.0);

                let idx = 6 - f32::ceil(6.0 * cooldown) as i32;
                let icon = Texture::from_id(0).icon(rect(64 * idx, 320, 64, 64));
                wait_animation = Some(Image::new(icon));
            }

            let desc: Option<String> = dict_get(data, "description")?;
            if let Some(desc) = desc {
                button = button.popup(
                    Popup::new()
                        .size(Size::new(400, 400))
                        .anchor(Point::new(
                            WIDTH_I - 400,
                            HEIGHT_I - 400 - ABILITY_BUTTON * 2,
                        ))
                        .add(Text::new(desc)?),
                );
            }

            let mut stack = Stack::new();
            stack.push(button);
            if let Some(w) = wait_animation {
                stack.push(w);
            }

            grid.push(stack);
        }

        Ok(Border::new(grid))
    }

    fn build_townspanel(
        &mut self,
        py: Python,
        ctx: &mut Context,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<impl Widget<GameMsg> + 'static> {
        let towns: &PyDict = self.townspanel.as_ref(py).getattr("resources")?.extract()?;

        let origin = (0, 0);
        let transform: (f32, f32) = self
            .camera
            .as_ref(py)
            .call_method1("project", (origin,))?
            .extract()?;

        let mut stack = Stack::new();

        let icon = Texture::from_id(0).icon(rect(0, 6 * 64, 3 * 64, 64));

        for (_, town) in towns {
            let dict: &PyDict = town.extract()?;

            let name: String = dict_get_or_default(dict, "name")?;
            let pos: (i32, i32) = dict_get_or_default(dict, "position")?;
            let anchor = Point::new(
                (pos.0 as f32 + transform.0 - 150.0) as i32,
                (pos.1 as f32 + transform.1 - 128.0) as i32,
            );

            let resource_image: String = dict_get_or_default(dict, "resource_image")?;
            let energy_image: String = dict_get_or_default(dict, "energy_image")?;

            let resource_icon = ggez_rend.load_texture(ctx, &resource_image)?.whole();
            let energy_icon = ggez_rend.load_texture(ctx, &energy_image)?.whole();

            let resource_value: u64 = dict_get_or_default(dict, "resource_value")?;
            let energy_value: u64 = dict_get_or_default(dict, "energy_value")?;

            stack.push(
                Popup::new()
                    .size(Size::new(300, 64))
                    .anchor(anchor)
                    .add(Border::with_icon(
                        icon,
                        Panel::hbox()
                            .add_flex(4, Text::new(name)?.valign(TextAlign::Middle))
                            .add_flex(1, Image::new(energy_icon))
                            .add_flex(
                                3,
                                Text::new(format!("{}", energy_value))?
                                    .valign(TextAlign::Middle),
                            )
                            .add_flex(1, Image::new(resource_icon))
                            .add_flex(
                                3,
                                Text::new(format!("{}", resource_value))?
                                    .valign(TextAlign::Middle),
                            ),
                    )),
            );
        }

        Ok(stack)
    }
}
