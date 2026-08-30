//! Rust-style diagnostic reporter for parser and lexer errors.

use crate::lexer::span::Span;
use crate::parser::ParseError;

/// Controls whether ANSI color codes are emitted in diagnostic output.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ColorChoice {
    /// Use colors only when stderr is a TTY and `NO_COLOR` is not set.
    Auto,
    /// Always use colors.
    Always,
    /// Never use colors.
    Never,
}

impl ColorChoice {
    fn use_color(self) -> bool {
        match self {
            ColorChoice::Always => true,
            ColorChoice::Never => false,
            ColorChoice::Auto => {
                std::io::IsTerminal::is_terminal(&std::io::stderr())
                    && std::env::var_os("NO_COLOR").is_none()
            }
        }
    }
}

/// A single diagnostic message (error, warning, etc.).
#[derive(Debug, Clone)]
pub struct Diagnostic {
    pub severity: Severity,
    pub message: String,
    pub file: String,
    pub span: Span,
    pub label: String,
    pub help: String,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Severity {
    Error,
    Warning,
    Note,
    Help,
}

impl Diagnostic {
    /// Build a diagnostic from a [`ParseError`]. The caller must later supply the
    /// source text via [`Diagnostic::render`].
    pub fn from_parse_error(err: &ParseError) -> Self {
        match err {
            ParseError::SyntaxError {
                file,
                span,
                msg,
                tip,
            } => Diagnostic {
                severity: Severity::Error,
                message: msg.clone(),
                file: file.clone(),
                span: *span,
                label: String::new(),
                help: tip.clone(),
            },
            ParseError::UnexpectedEof { file, pos } => Diagnostic {
                severity: Severity::Error,
                message: "Unexpected end of input".into(),
                file: file.clone(),
                span: Span::at(*pos),
                label: String::new(),
                help: "突然斷尾，係咪漏咗啲符號？".into(),
            },
        }
    }

    /// Render the diagnostic as a multi-line string using the provided source.
    pub fn render(&self, source: &str, colors: ColorChoice) -> String {
        let c = Color::new(colors.use_color());
        let mut out = String::new();

        // Header: "error: message"
        let severity_label = match self.severity {
            Severity::Error => "error",
            Severity::Warning => "warning",
            Severity::Note => "note",
            Severity::Help => "help",
        };
        out.push_str(&c.paint(
            severity_label,
            match self.severity {
                Severity::Error => ColorCode::RedBold,
                Severity::Warning => ColorCode::YellowBold,
                Severity::Note => ColorCode::BlueBold,
                Severity::Help => ColorCode::GreenBold,
            },
        ));
        out.push_str(": ");
        out.push_str(&self.message);
        out.push('\n');

        // Location line: " --> file:line:col"
        out.push_str(" "); // left gutter padding
        out.push_str(&c.paint("-->", ColorCode::Blue));
        out.push_str(&format!(
            " {}:{}:{}\n",
            self.file, self.span.start.line, self.span.start.offset
        ));

        // Source snippet
        let lines: Vec<&str> = source.lines().collect();
        let start_line = self.span.start.line.saturating_sub(1);
        let end_line = self.span.end.line.saturating_sub(1);
        let start_line = start_line.min(lines.len().saturating_sub(1));
        let end_line = end_line.min(lines.len().saturating_sub(1));

        let max_line_num = (end_line + 1).max(lines.len());
        let line_num_width = max_line_num.to_string().len();

        // Gutter separator line: "   |"
        out.push_str(&" ".repeat(line_num_width + 1));
        out.push(' ');
        out.push_str(&c.paint("|", ColorCode::Blue));
        out.push('\n');

        if lines.is_empty() {
            out.push_str(&" ".repeat(line_num_width + 1));
            out.push(' ');
            out.push_str(&c.paint("|", ColorCode::Blue));
            out.push('\n');
        } else if start_line == end_line {
            self.render_single_line(&lines, start_line, line_num_width, &c, &mut out);
        } else {
            self.render_multi_line(&lines, start_line, end_line, line_num_width, &c, &mut out);
        }

        // Help note
        if !self.help.is_empty() {
            out.push_str(&" ".repeat(line_num_width + 1));
            out.push(' ');
            out.push_str(&c.paint("|", ColorCode::Blue));
            out.push('\n');
            out.push_str(&" ".repeat(line_num_width + 1));
            out.push(' ');
            out.push_str(&c.paint("= help", ColorCode::GreenBold));
            out.push_str(": ");
            out.push_str(&self.help);
            out.push('\n');
            out.push_str(":D 不如跟住我嘅tips繼續符碌下?");
        }

        out
    }

    fn render_single_line(
        &self,
        lines: &[&str],
        line_idx: usize,
        line_num_width: usize,
        c: &Color,
        out: &mut String,
    ) {
        let line_no = line_idx + 1;
        let line_text = lines[line_idx];

        // Source line: " 2 | <text>"
        out.push_str(&format!("{:>width$} ", line_no, width = line_num_width));
        out.push_str(&c.paint("|", ColorCode::Blue));
        out.push(' ');
        out.push_str(line_text);
        out.push('\n');

        // Underline line: "   |      ^^^ label"
        out.push_str(&" ".repeat(line_num_width + 1));
        out.push(' ');
        out.push_str(&c.paint("|", ColorCode::Blue));
        out.push(' ');

        let start_col = self.span.start.offset;
        let end_col = self.span.end.offset;
        let (prefix_width, _) = display_width_up_to(line_text, start_col);
        out.push_str(&" ".repeat(prefix_width));

        let highlight_len = if end_col > start_col {
            let (start_w, _) = display_width_up_to(line_text, start_col);
            let (end_w, _) = display_width_up_to(line_text, end_col);
            end_w.saturating_sub(start_w).max(1)
        } else {
            1
        };
        let highlight = "^".repeat(highlight_len);
        out.push_str(&c.paint(&highlight, ColorCode::RedBold));

        if !self.label.is_empty() {
            out.push(' ');
            out.push_str(&self.label);
        }
        out.push('\n');
    }

    #[allow(clippy::too_many_arguments)]
    fn render_multi_line(
        &self,
        lines: &[&str],
        start_idx: usize,
        end_idx: usize,
        line_num_width: usize,
        c: &Color,
        out: &mut String,
    ) {
        for line_idx in start_idx..=end_idx {
            let line_no = line_idx + 1;
            let line_text = lines[line_idx];

            out.push_str(&format!("{:>width$} ", line_no, width = line_num_width));
            out.push_str(&c.paint("|", ColorCode::Blue));
            out.push(' ');
            out.push_str(line_text);
            out.push('\n');

            // Underline for this line
            out.push_str(&" ".repeat(line_num_width + 1));
            out.push(' ');
            out.push_str(&c.paint("|", ColorCode::Blue));
            out.push(' ');

            let start_col = if line_idx == start_idx {
                self.span.start.offset
            } else {
                0
            };
            let end_col = if line_idx == end_idx {
                self.span.end.offset
            } else {
                line_text.chars().count()
            };

            let (prefix_width, _) = display_width_up_to(line_text, start_col);
            out.push_str(&" ".repeat(prefix_width));

            let highlight_len = if end_col > start_col {
                let (start_w, _) = display_width_up_to(line_text, start_col);
                let (end_w, _) = display_width_up_to(line_text, end_col);
                end_w.saturating_sub(start_w).max(1)
            } else {
                1
            };
            let highlight = "^".repeat(highlight_len);
            out.push_str(&c.paint(&highlight, ColorCode::RedBold));
            out.push('\n');
        }
    }
}

/// Returns the display width of the first `char_count` characters of `s` and
/// the byte index where those characters end.
fn display_width_up_to(s: &str, char_count: usize) -> (usize, usize) {
    let mut width = 0;
    let mut byte_idx = 0;
    let mut count = 0;
    for (idx, ch) in s.char_indices() {
        if count >= char_count {
            break;
        }
        width += unicode_width::UnicodeWidthChar::width(ch).unwrap_or(0);
        byte_idx = idx + ch.len_utf8();
        count += 1;
    }
    (width, byte_idx)
}

enum ColorCode {
    RedBold,
    YellowBold,
    BlueBold,
    GreenBold,
    Blue,
}

struct Color {
    enabled: bool,
}

impl Color {
    fn new(enabled: bool) -> Self {
        Self { enabled }
    }

    fn paint(&self, text: &str, code: ColorCode) -> String {
        if !self.enabled {
            return text.to_string();
        }
        let escape = match code {
            ColorCode::RedBold => "\x1b[1;31m",
            ColorCode::YellowBold => "\x1b[1;33m",
            ColorCode::BlueBold => "\x1b[1;34m",
            ColorCode::GreenBold => "\x1b[1;32m",
            ColorCode::Blue => "\x1b[0;34m",
        };
        format!("{escape}{text}\x1b[0m")
    }
}
