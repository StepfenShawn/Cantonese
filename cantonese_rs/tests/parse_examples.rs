//! Integration tests that verify the Rust parser produces a valid syntax tree
//! for every `.cantonese` example exercised by `test.rb`.
//!
//! These tests only check that lexing + parsing succeeds; they do not assert on
//! the runtime output of the programs.

use std::path::Path;

use cantonese_rs::lexer::Lexer;
use cantonese_rs::parser::{Parser as CanParser, StatParser};

fn parse_cantonese_file(path: &Path) -> Result<Vec<cantonese_rs::ast::Stat>, String> {
    let source = std::fs::read_to_string(path)
        .map_err(|e| format!("failed to read {}: {e}", path.display()))?;
    let path_str = path.to_string_lossy().to_string();
    let mut lexer = Lexer::new(path_str.clone(), &source);
    let tokens = lexer
        .tokenize_all()
        .map_err(|e| format!("lexer error in {}: {e}", path.display()))?;
    let mut parser = CanParser::new(&tokens, &path_str);
    StatParser::parse_stats(&mut parser)
        .map_err(|e| format!("parser error in {}: {e}", path.display()))
}

fn assert_parses(path: &str) {
    let full_path = Path::new(env!("CARGO_MANIFEST_DIR")).join("..").join(path);
    let stats = parse_cantonese_file(&full_path).unwrap_or_else(|e| panic!("{e}"));
    // Ensure the parser consumed the whole file and produced at least an Exit
    // placeholder for an empty program.
    assert!(
        !stats.is_empty(),
        "expected at least one statement for {}",
        full_path.display()
    );
}

// ---------------------------------------------------------------------------
// BasicTest (from test.rb)
// ---------------------------------------------------------------------------

#[test]
fn parse_hello_world() {
    assert_parses("examples/basic/HelloWorld.cantonese");
}

#[test]
fn parse_assign() {
    assert_parses("examples/basic/assign.cantonese");
}

#[test]
fn parse_comment() {
    assert_parses("examples/basic/comment.cantonese");
}

#[test]
fn parse_assert() {
    assert_parses("examples/basic/assert.cantonese");
}

#[test]
fn parse_class() {
    assert_parses("examples/basic/class.cantonese");
}

#[test]
fn parse_call_python() {
    assert_parses("examples/basic/call_python.cantonese");
}

#[test]
fn parse_exit() {
    assert_parses("examples/basic/exit.cantonese");
}

#[test]
fn parse_for() {
    assert_parses("examples/basic/for.cantonese");
}

#[test]
fn parse_function() {
    assert_parses("examples/basic/function.cantonese");
}

#[test]
fn parse_if() {
    assert_parses("examples/basic/if.cantonese");
}

#[test]
fn parse_import() {
    assert_parses("examples/basic/import.cantonese");
}

#[test]
fn parse_lambda() {
    assert_parses("examples/basic/lambda.cantonese");
}

#[test]
fn parse_list() {
    assert_parses("examples/basic/list.cantonese");
}

#[test]
fn parse_match() {
    assert_parses("examples/basic/match.cantonese");
}

#[test]
fn parse_raise() {
    assert_parses("examples/basic/raise.cantonese");
}

#[test]
fn parse_set() {
    assert_parses("examples/basic/set.cantonese");
}

#[test]
fn parse_try_finally() {
    assert_parses("examples/basic/try_finally.cantonese");
}

#[test]
fn parse_type() {
    assert_parses("examples/basic/type.cantonese");
}

#[test]
fn parse_while() {
    assert_parses("examples/basic/while.cantonese");
}

// ---------------------------------------------------------------------------
// AlgoTest (from test.rb)
// ---------------------------------------------------------------------------

#[test]
fn parse_binary_search() {
    assert_parses("examples/algorithms/binary_search.cantonese");
}

#[test]
fn parse_bubble_sort() {
    assert_parses("examples/algorithms/bubble_sort.cantonese");
}

#[test]
fn parse_fib() {
    assert_parses("examples/algorithms/fib.cantonese");
}

#[test]
fn parse_factorial() {
    assert_parses("examples/algorithms/factorial.cantonese");
}

#[test]
fn parse_fizzbuzz() {
    assert_parses("examples/algorithms/fizzbuzz.cantonese");
}

#[test]
fn parse_insert_sort() {
    assert_parses("examples/algorithms/insert_sort.cantonese");
}

#[test]
fn parse_linear_search() {
    assert_parses("examples/algorithms/linear_search.cantonese");
}

#[test]
fn parse_max() {
    assert_parses("examples/algorithms/max.cantonese");
}

#[test]
fn parse_tower_of_hanoi() {
    assert_parses("examples/algorithms/Tower_of_Hanoi.cantonese");
}

#[test]
fn parse_climb_stairs() {
    assert_parses("examples/leetcode/climbStairs.cantonese");
}

#[test]
fn parse_get_sum() {
    assert_parses("examples/leetcode/getSum.cantonese");
}

#[test]
fn parse_num_identical_pairs() {
    assert_parses("examples/leetcode/numIdenticalPairs.cantonese");
}

#[test]
fn parse_rotate_string() {
    assert_parses("examples/leetcode/rotateString.cantonese");
}

#[test]
fn parse_single_number() {
    assert_parses("examples/leetcode/singleNumber.cantonese");
}

// ---------------------------------------------------------------------------
// MiscTest (from test.rb)
// ---------------------------------------------------------------------------

#[test]
fn parse_calc_corr() {
    assert_parses("examples/numerical/calc_corr.cantonese");
}

#[test]
fn parse_matrix() {
    assert_parses("examples/numerical/Matrix.cantonese");
}

#[test]
fn parse_knn() {
    assert_parses("examples/machine_learning/KNN.cantonese");
}

#[test]
fn parse_linear_regression() {
    assert_parses("examples/machine_learning/linear_regression.cantonese");
}

// ---------------------------------------------------------------------------
// LibTest (from test.rb)
// ---------------------------------------------------------------------------

#[test]
fn parse_csv_parse() {
    assert_parses("examples/lib_sample/csv_parse.cantonese");
}

#[test]
fn parse_file() {
    assert_parses("examples/lib_sample/file.cantonese");
}

#[test]
fn parse_random() {
    assert_parses("examples/lib_sample/random.cantonese");
}

#[test]
fn parse_re() {
    assert_parses("examples/lib_sample/re.cantonese");
}
