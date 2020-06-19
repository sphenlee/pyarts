use crate::scene::{HEIGHT_I, WIDTH_I};
use crate::ui::ggez_renderer::GgezRenderer;
use crate::ui::tk::*;
use crate::util::YartsResult;
use ggez::Context;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use glyph_brush::HorizontalAlign;

#[derive(Clone, Debug)]
pub enum GameMsg {
    AbilityButton(u32),
}

#[pyclass]
pub struct GameUi {
    infopanel: PyObject,
}

#[pymethods]
impl GameUi {
    #[staticmethod]
    fn depends() -> Vec<&'static str> {
        vec!["infopanel"]
    }

    #[new]
    fn new(py: Python) -> GameUi {
        GameUi {
            infopanel: py.None(),
        }
    }

    #[args(kwargs = "**")]
    fn inject(&mut self, kwargs: Option<&PyDict>) -> PyResult<()> {
        let deps: &PyAny = kwargs.expect("inject must be called with kwargs").as_ref();

        self.infopanel = deps.get_item("infopanel")?.into();

        Ok(())
    }
}

// small helper functions - maybe move to a pyo3 helpers module?
fn dict_get_or_else<'a, K, T, F>(dict: &'a PyDict, key: K, f: F) -> PyResult<T>
where K: pyo3::ToBorrowedObject,
    T: FromPyObject<'a>,
    F: FnOnce() -> T
{
    match dict.get_item(key) {
        None => Ok(f()),
        Some(item) => item.extract::<T>(),
    }
}

fn dict_get_or_default<'a, K, T>(dict: &'a PyDict, key: K) -> PyResult<T>
where  K: pyo3::ToBorrowedObject,
       T: FromPyObject<'a> + Default
{
    dict_get_or_else(dict, key, || Default::default())
}

fn dict_get<'a, K, T>(dict: &'a PyDict, key: K) -> PyResult<Option<T>>
    where K: pyo3::ToBorrowedObject,
          T: FromPyObject<'a>
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
        Ok(())
    }

    pub fn draw(
        &mut self,
        py: Python,
        ctx: &mut Context,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<()> {
        let infopanel = self.build_infopanel(py, ctx, ggez_rend)?;

        let messages = ggez_rend.render(
            ctx,
            infopanel,
            rect(0, HEIGHT_I / 4 * 3, WIDTH_I / 2, HEIGHT_I / 4),
        )?;
        for msg in messages {
            log::warn!("{:?}", msg);
        }

        Ok(())
    }

    fn build_infopanel(
        &mut self,
        py: Python,
        ctx: &mut Context,
        ggez_rend: &mut GgezRenderer,
    ) -> YartsResult<Element<GameMsg>> {
        let entities: &PyList = self.infopanel.as_ref(py).getattr("data")?.extract()?;

        if entities.len() == 1 {
            let data: &PyDict = entities.get_item(0).extract()?;

            // name
            let name: String = dict_get_or_default(data, "name")?;
            let mut info = Panel::vbox().add(Text::new(name)?.halign(HorizontalAlign::Center));

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

            let panel = Panel::hbox().add(info)
                .add_flex(2, Panel::vbox())
                ;

            Ok(Border::new(panel).build())
        } else {
            let text = Text::new("Multiple Entities Selected *TODO*")?;
            Ok(Border::new(text).build())
        }


    }
}
