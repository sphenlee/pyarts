pub struct Camera {
    lookx: i64,
    looky: i64,
}

impl Camera {
    pub fn new() -> Self {
        Self {
            lookx: 0,
            looky: 0,
        }
    }
}
