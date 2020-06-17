/// Promises - Like Futures, but designed to work with Python
use pyo3::prelude::*;
use std::sync::mpsc;

type Extractable = Box<dyn ToPyObject + Send + 'static>;

enum PromiseInner {
    Ready(PyObject),
    Pending(mpsc::Receiver<Extractable>),
}

#[pyclass]
pub struct Promise {
    inner: PromiseInner,
}

#[pymethods]
impl Promise {
    fn get(&mut self, py: Python) -> PyResult<PyObject> {
        match &self.inner {
            PromiseInner::Ready(obj) => Ok(obj.clone()),
            PromiseInner::Pending(rx) => {
                match rx.try_recv() {
                    Ok(extractable) => {
                        let obj = extractable.to_object(py);
                        self.inner = PromiseInner::Ready(obj.clone());
                        Ok(obj)
                    }
                    Err(mpsc::TryRecvError::Disconnected) => {
                        // python error?
                        panic!("promise didn't send a value");
                    }
                    Err(mpsc::TryRecvError::Empty) => Ok(py.None()),
                }
            }
        }
    }
}

impl Promise {
    pub fn new<F, T>(f: F) -> Promise
    where
        F: FnOnce() -> T + Send + 'static,
        T: ToPyObject + Send + 'static,
    {
        let (tx, rx) = mpsc::channel();

        std::thread::spawn(move || {
            let extractable = f();
            let _ = tx.send(Box::new(extractable) as Extractable);
        });

        Promise {
            inner: PromiseInner::Pending(rx),
        }
    }
}
