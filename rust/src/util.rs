use crate::ui::tk::TkError;
use ggez::GameError;
use pyo3::PyErr;
use std::error::Error;
use thiserror::Error;

pub type YartsResult<T> = std::result::Result<T, YartsError>;

#[derive(Error, Debug)]
pub enum YartsError {
    #[error("GGEZ Error: {0}")]
    GameError(#[from] GameError),

    #[error("TkError: {0}")]
    TkError(#[from] TkError),

    #[error("Python Exception {0:?}")]
    PyErr(PyErr),

    #[error(transparent)]
    Other(#[from] Box<dyn Error>),
}

impl From<PyErr> for YartsError {
    fn from(pyerr: PyErr) -> Self {
        YartsError::PyErr(pyerr)
    }
}

impl From<YartsError> for GameError {
    fn from(err: YartsError) -> Self {
        match err {
            YartsError::GameError(ge) => ge,
            YartsError::PyErr(pyerr) => {
                panic!("{:?}", pyerr);
            }
            YartsError::Other(err) => GameError::EventLoopError(err.to_string()),
            YartsError::TkError(err) => GameError::RenderError(err.to_string()),
        }
    }
}

impl From<YartsError> for PyErr {
    fn from(err: YartsError) -> Self {
        match err {
            YartsError::GameError(ge) => pyo3::exceptions::PyIOError::new_err(ge.to_string()),
            YartsError::PyErr(pyerr) => pyerr,
            YartsError::Other(err) => pyo3::exceptions::PyIOError::new_err(err.to_string()),
            YartsError::TkError(err) => pyo3::exceptions::PyIOError::new_err(err.to_string()),
        }
    }
}
