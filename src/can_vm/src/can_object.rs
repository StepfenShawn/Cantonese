use std::{fmt, ops, cmp};

#[derive(Copy, Clone)]
pub enum CanObject<'a> {
    Bool(bool),
    Num(f32),
    Ref(u32),
    Str(&'a str)
}

/* To string */
impl fmt::Display for CanObject<'_> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        let outline = match *self {
            CanObject::Num(num) => {
                if num % 1.0 == 0.0 {
                    (num as i32).to_string()
                } else {
                    num.to_string()
                }
            },
            CanObject::Ref(_ref) => {
                "Reference".to_string()
            },
            CanObject::Bool(b) => {
                b.to_string()
            }
            CanObject::Str(s) => {
                s.to_string()
            }
        };
        write!(f, "{}", outline)
    }
}

impl<'a> ops::Add for CanObject<'a> {
    type Output = CanObject<'a>;
    fn add(self, right: CanObject<'a>) -> CanObject<'a> {
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


impl<'a> ops::Sub for CanObject<'a> {
    type Output = CanObject<'a>;
    fn sub(self, right: CanObject<'a>) -> CanObject<'a> {
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

impl<'a> ops::Mul for CanObject<'a> {
    type Output = CanObject<'a>;
    fn mul(self, right: CanObject<'a>) -> CanObject<'a> {
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

impl<'a> ops::Div for CanObject<'a> {
    type Output = CanObject<'a>;
    fn div(self, right: CanObject<'a>) -> CanObject<'a> {
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

impl<'a> ops::BitAnd for CanObject<'a> {
    type Output = CanObject<'a>;
    fn bitand(self, right: CanObject<'a>) -> CanObject<'a> {
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

impl<'a> ops::BitOr for CanObject<'a> {
    type Output = CanObject<'a>;
    fn bitor(self, right: CanObject<'a>) -> CanObject<'a> {
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

impl cmp::PartialEq for CanObject<'_> {
    fn eq(&self, right: &CanObject) -> bool {
        match self {
            CanObject::Num(arg1) => {
                match right {
                    CanObject::Num(arg2) => arg1 == arg2,
                    _ => panic!("Cannot perform operations on refs (yet)"),
                }
            }
            _ => panic!("Cannot perform operations on refs (yet)"),
        }
    }
}

impl cmp::PartialOrd for CanObject<'_> {
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