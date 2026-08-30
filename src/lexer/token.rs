use super::span::Span;
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Pos {
    pub line: usize,
    pub offset: usize,
    pub end_line: Option<usize>,
    pub end_offset: Option<usize>,
}

impl Pos {
    pub fn new(
        line: usize,
        offset: usize,
        end_line: Option<usize>,
        end_offset: Option<usize>,
    ) -> Self {
        Self {
            line,
            offset,
            end_line,
            end_offset,
        }
    }

    pub fn simple(line: usize, offset: usize) -> Self {
        Self::new(line, offset, None, None)
    }

    /// Create a span from this position up to (and including) `end`.
    pub fn span_to(self, end: Pos) -> Span {
        Span { start: self, end }
    }

    /// Return a copy of this position with the end fields filled in.
    pub fn with_end(self, end_line: usize, end_offset: usize) -> Self {
        Self::new(self.line, self.offset, Some(end_line), Some(end_offset))
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum TokenType {
    EOF = 0,
    VarArg = 1,    // <*>
    SepComma = 2,  // ,
    SepDot = 3,    // .
    SepLParen = 4, // (
    SepRParen = 5, // )
    SepLBrack = 6, // [
    SepRBrack = 7, // ]
    SepLCurly = 8, // {
    SepRCurly = 9, // }
    OpMinus = 10,  // -
    OpWave = 11,   // !
    OpAdd = 12,    // +
    OpMul = 13,    // *
    OpDiv = 14,    // /
    OpPow = 15,    // ^
    OpMod = 16,    // %
    OpBand = 17,   // &
    OpShr = 18,    // >>
    OpShl = 19,    // <<
    OpConcat = 20, // <->
    OpLt = 21,     // <
    OpLe = 22,     // <=
    OpGt = 23,     // >
    OpGe = 24,     // >=
    OpEq = 25,     // ==
    OpAssign = 26, // =
    OpNe = 27,     // !=
    OpAnd = 28,    // and
    OpOr = 29,     // or
    OpNot = 30,    // not
    OpBor = 31,    // <|>
    OpIDiv = 32,   // //
    Keyword = 33,
    Identifier = 34,
    String = 35,
    Num = 36,
    CallNativeExpr = 37, // #XD ... 二五仔係我
    Brack = 38,          // |
    Colon = 39,          // :
    Mark = 40,           // ?
    Excl = 41,           // !
    DColon = 42,         // ::
}

impl fmt::Display for TokenType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{self:?}")
    }
}

#[derive(Debug, Clone, PartialEq)]
pub struct Token {
    pub pos: Pos,
    pub typ: TokenType,
    pub value: String,
}

impl Token {
    pub fn new(pos: Pos, typ: TokenType, value: String) -> Self {
        Self { pos, typ, value }
    }
}

impl fmt::Display for Token {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{} ({})", self.value, self.typ)
    }
}
