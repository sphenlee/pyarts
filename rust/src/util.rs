use ggez::GameError;
use pyo3::PyErr;

pub struct PyGgezError {
    inner: GameError
}

impl From<GameError> for PyGgezError {
    fn from(err: GameError) -> Self {
        Self { inner: err }
    }
}

impl From<PyGgezError> for PyErr {
    fn from(err: PyGgezError) -> Self {
        let msg = err.inner.to_string();
        pyo3::exceptions::IOError::py_err(msg)
    }
}