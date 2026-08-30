use super::Pos;

/// A source span from a start position to an end position.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Span {
    pub start: Pos,
    pub end: Pos,
}

impl Span {
    pub fn new(start: Pos, end: Pos) -> Self {
        Self { start, end }
    }

    /// Create a zero-width span at a single position.
    pub fn at(pos: Pos) -> Self {
        Self {
            start: pos,
            end: pos,
        }
    }

    /// Convert a token `Pos` (which may carry `end_*`) into a span.
    /// Falls back to a zero-width span at `pos` when end fields are missing.
    pub fn from_token_pos(pos: Pos) -> Self {
        let end = Pos::new(
            pos.end_line.unwrap_or(pos.line),
            pos.end_offset.unwrap_or(pos.offset),
            pos.end_line,
            pos.end_offset,
        );
        Self { start: pos, end }
    }
}
