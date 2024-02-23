use std::{fmt, ops, cmp};

#[derive(Copy, Clone)]
pub enum CanObject {
    Bool(bool),
    Num(f32),
    Ref(u32),
}

/* To string */
impl fmt::Display for CanObject {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let outline = match *self {
            CanObject::Num(num) => {
                num.to_string()
            },
            CanObject::Ref(_ref) => {
                "Reference".to_string()
            },
            CanObject::Bool(b) => {
                b.to_string()
            }
        };
        write!(f, "{}", outline)
    }
}

impl ops::Add for CanObject {
    type Output = CanObject;
    fn add(self, right: CanObject) -> CanObject {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => CanObject::Num(arg1 + arg2),
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)")
        }
    }
}


impl ops::Sub for CanObject {
    type Output = CanObject;
    fn sub(self, right: CanObject) -> CanObject {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => CanObject::Num(arg1 - arg2),
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)")
        }
    }
}

impl ops::Mul for CanObject {
    type Output = CanObject;
    fn mul(self, right: CanObject) -> CanObject {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => CanObject::Num(arg1 * arg2),
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)")
        }
    }
}

impl ops::Div for CanObject {
    type Output = CanObject;
    fn div(self, right: CanObject) -> CanObject {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => CanObject::Num(arg1 / arg2),
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)")
        }
    }
}

impl ops::BitAnd for CanObject {
    type Output = CanObject;
    fn bitand(self, right: CanObject) -> CanObject {
        match self {
            CanObject::Bool(arg1) => {
                match right {
                    CanObject::Bool(arg2) => CanObject::Bool(arg1 & arg2),
                    _ => panic!("Cannot perform operations exclude bool type"),
                }
            }
            _ => panic!("Cannot perform operations exclude bool type")
        }
    }
}

impl ops::BitOr for CanObject {
    type Output = CanObject;
    fn bitor(self, right: CanObject) -> CanObject {
        match self {
            CanObject::Bool(arg1) => {
                match right {
                    CanObject::Bool(arg2) => CanObject::Bool(arg1 | arg2),
                    _ => panic!("Cannot perform operations exclude bool type"),
                }
            }
            _ => panic!("Cannot perform operations exclude bool type")
        }
    }
}

impl cmp::PartialEq for CanObject {
    fn eq(&self, right: &CanObject) -> bool {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => (arg1 == arg2),
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)"),
        }
    }
}

impl cmp::PartialOrd for CanObject {
    fn partial_cmp(&self, right: &CanObject) -> Option<cmp::Ordering> {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => {
                        arg1.partial_cmp(&arg2)
                    },
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)"),
        }
    }
}