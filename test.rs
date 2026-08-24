// rustc test.rs && ./test.exe
use std::process::Command;
use std::fmt;

const RUN: &str = "python";
const SCRIPT: &str = "can_source/cantonese.py";

#[derive(Debug, Clone)]
enum Assertion {
    Eq(String, String),
    Contains(String, &'static str),
    NoContainsAndNonEmpty(&'static str),
}

struct TestCase {
    group: &'static str,
    name: &'static str,
    file: &'static str,
    assert: Assertion,
}

impl fmt::Display for Assertion {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Assertion::Eq(a,b) => write!(f, "expect == {:?}, got {:?}", b, a),
            Assertion::Contains(out, s) => write!(f, "expect contains {:?}, output: {:?}", s, out),
            Assertion::NoContainsAndNonEmpty(s) => write!(f, "expect not contains {:?} and non‑empty", s),
        }
    }
}

fn run_example(path: &str) -> String {
    let output = Command::new(RUN)
        .args([SCRIPT, path])
        .output()
        .expect("spawn python failed; check python in PATH");
    String::from_utf8_lossy(&output.stdout).to_string().replace("\r\n", "\n")
}

fn check_assert(output: &str, a: &Assertion) -> bool {
    match a {
        Assertion::Eq(ref actual, ref expect) => actual == expect,
        Assertion::Contains(out, s) => out.contains(s),
        Assertion::NoContainsAndNonEmpty(s) => !output.contains(s) && !output.is_empty(),
    }
}

fn main() {
    println!("OK sir! Ready to test!!!");
    let cases: &[TestCase] = &[
        // ========== BasicTest ==========
        TestCase{group:"BasicTest", name:"test_hello_world", file:"examples/basic/HelloWorld.cantonese", assert:Assertion::Eq(run_example("examples/basic/HelloWorld.cantonese"), "Hello World!\n".into())},
        TestCase{group:"BasicTest", name:"test_assign", file:"examples/basic/assign.cantonese", assert:Assertion::Eq(run_example("examples/basic/assign.cantonese"), "1\n3\n".into())},
        TestCase{group:"BasicTest", name:"test_comment", file:"examples/basic/comment.cantonese", assert:Assertion::Eq(run_example("examples/basic/comment.cantonese"), "Run OK\n".into())},
        TestCase{group:"BasicTest", name:"test_assert", file:"examples/basic/assert.cantonese", assert:Assertion::Contains(run_example("examples/basic/assert.cantonese"), "AssertionError")},
        TestCase{group:"BasicTest", name:"test_class", file:"examples/basic/class.cantonese", assert:Assertion::Eq(run_example("examples/basic/class.cantonese"), "Duck is swimming\nDuck is sleeping\n公\n".into())},
        TestCase{group:"BasicTest", name:"test_callpython", file:"examples/basic/call_python.cantonese", assert:Assertion::Eq(run_example("examples/basic/call_python.cantonese"), "10\n".into())},
        TestCase{group:"BasicTest", name:"test_exit", file:"examples/basic/exit.cantonese", assert:Assertion::Eq(run_example("examples/basic/exit.cantonese"), "执行exit\n".into())},
        TestCase{group:"BasicTest", name:"test_for", file:"examples/basic/for.cantonese", assert:Assertion::Eq(run_example("examples/basic/for.cantonese"), "1\n2\n3\n4\n1\n2\n3\n".into())},
        TestCase{group:"BasicTest", name:"test_function", file:"examples/basic/function.cantonese", assert:Assertion::Eq(run_example("examples/basic/function.cantonese"), "Hello\nHello World1\n".into())},
        TestCase{group:"BasicTest", name:"test_if", file:"examples/basic/if.cantonese", assert:Assertion::Eq(run_example("examples/basic/if.cantonese"), "A 係 3\nB 係 1\n".into())},
        TestCase{group:"BasicTest", name:"test_import", file:"examples/basic/import.cantonese", assert:Assertion::Eq(run_example("examples/basic/import.cantonese"), "1\n3\n5.0\n1\n测试成功\n".into())},
        TestCase{group:"BasicTest", name:"test_lambda", file:"examples/basic/lambda.cantonese", assert:Assertion::Eq(run_example("examples/basic/lambda.cantonese"), "4\n".into())},
        TestCase{group:"BasicTest", name:"test_list", file:"examples/basic/list.cantonese", assert:Assertion::Eq(run_example("examples/basic/list.cantonese"), "[2, 3, 3]\n3\n2\n3\n3\n[]\n".into())},
        TestCase{group:"BasicTest", name:"test_match", file:"examples/basic/match.cantonese", assert:Assertion::Eq(run_example("examples/basic/match.cantonese"), "Not found\n".into())},
        TestCase{group:"BasicTest", name:"test_raise", file:"examples/basic/raise.cantonese", assert:Assertion::Contains(run_example("examples/basic/raise.cantonese"), "濑嘢!")},
        TestCase{group:"BasicTest", name:"test_set", file:"examples/basic/set.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"BasicTest", name:"test_try_finally", file:"examples/basic/try_finally.cantonese", assert:Assertion::Eq(run_example("examples/basic/try_finally.cantonese"), "揾到NameError\n执手尾: \n1 1\n".into())},
        TestCase{group:"BasicTest", name:"test_type", file:"examples/basic/type.cantonese", assert:Assertion::Eq(run_example("examples/basic/type.cantonese"), "<class 'int'>\n<class 'libs.std.impl.Str'>\n".into())},
        TestCase{group:"BasicTest", name:"test_while", file:"examples/basic/while.cantonese", assert:Assertion::Eq(run_example("examples/basic/while.cantonese"), "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n".into())},

        // ========== AlgoTest ==========
        TestCase{group:"AlgoTest", name:"test_binary_search", file:"examples/algorithms/binary_search.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/binary_search.cantonese"), "揾到啦!!!\n揾唔到: (\n".into())},
        TestCase{group:"AlgoTest", name:"test_bubble_sort", file:"examples/algorithms/bubble_sort.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/bubble_sort.cantonese"), "[11, 12, 22, 25, 34, 64, 90]\n[12, 21, 22, 55, 77, 90, 97]\n".into())},
        TestCase{group:"AlgoTest", name:"test_fib", file:"examples/algorithms/fib.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/fib.cantonese"), "55\n1\n".into())},
        TestCase{group:"AlgoTest", name:"test_factorial", file:"examples/algorithms/factorial.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/factorial.cantonese"), "2\n720\n".into())},
        TestCase{group:"AlgoTest", name:"test_fizzbuzz", file:"examples/algorithms/fizzbuzz.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"AlgoTest", name:"test_insert_sort", file:"examples/algorithms/insert_sort.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/insert_sort.cantonese"), "[11, 12, 22, 25, 34, 64, 90]\n[12, 21, 22, 55, 77, 90, 97]\n".into())},
        TestCase{group:"AlgoTest", name:"test_linear_search", file:"examples/algorithms/linear_search.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/linear_search.cantonese"), "揾到啦:)\n揾唔到:(\n".into())},
        TestCase{group:"AlgoTest", name:"test_max", file:"examples/algorithms/max.cantonese", assert:Assertion::Eq(run_example("examples/algorithms/max.cantonese"), "34\n27\n".into())},
        TestCase{group:"AlgoTest", name:"test_Tower_of_Hanoi", file:"examples/algorithms/Tower_of_Hanoi.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"AlgoTest", name:"test_climbStairs", file:"examples/leetcode/climbStairs.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"AlgoTest", name:"test_getSum", file:"examples/leetcode/getSum.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"AlgoTest", name:"test_numIdenticalPairs", file:"examples/leetcode/numIdenticalPairs.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"AlgoTest", name:"test_rotateString", file:"examples/leetcode/rotateString.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"AlgoTest", name:"test_singleNumber", file:"examples/leetcode/singleNumber.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},

        // ========== MiscTest ==========
        TestCase{group:"MiscTest", name:"test_calc_corr", file:"examples/numerical/calc_corr.cantonese", assert:Assertion::Eq(run_example("examples/numerical/calc_corr.cantonese"), "0.8066499427138474\n".into())},
        TestCase{group:"MiscTest", name:"test_Matrix", file:"examples/numerical/Matrix.cantonese", assert:Assertion::Eq(run_example("examples/numerical/Matrix.cantonese"), "Matrix: [[1, 1], [2, 2]]\nMatrix: [[2, 2], [3, 3]]\nMatrix: [[3, 3], [5, 5]]\nMatrix: [[3, 3, 3], [6, 6, 6]]\n".into())},
        TestCase{group:"MiscTest", name:"test_knn", file:"examples/machine_learning/KNN.cantonese", assert:Assertion::Eq(run_example("examples/machine_learning/KNN.cantonese"), "动作片\n".into())},
        TestCase{group:"MiscTest", name:"test_linear_regression", file:"examples/machine_learning/linear_regression.cantonese", assert:Assertion::Eq(run_example("examples/machine_learning/linear_regression.cantonese"), "Linear function is:\ny=0.530960991635149x+189.75347155122432\n667.6183640228585\n".into())},

        // ========== LibTest ==========
        TestCase{group:"LibTest", name:"test_csv_parse", file:"examples/lib_sample/csv_parse.cantonese", assert:Assertion::Eq(run_example("examples/lib_sample/csv_parse.cantonese"), "['id', 'name', ' age', 'gender', 'class_num']\n['1001', '张三', '18', 'male', '01']\n['1002', '李四', '19', 'male', '01']\n['1003', '王五', '19', 'famale', '01']\n['1004', '李华', '18', 'male', '01']\n".into())},
        TestCase{group:"LibTest", name:"test_file", file:"examples/lib_sample/file.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"LibTest", name:"test_random", file:"examples/lib_sample/random.cantonese", assert:Assertion::NoContainsAndNonEmpty("濑嘢!")},
        TestCase{group:"LibTest", name:"test_re", file:"examples/lib_sample/re.cantonese", assert:Assertion::Eq(run_example("examples/lib_sample/re.cantonese"), "(0, 3)\nNone\n".into())},
    ];

    let mut passed = 0usize;
    let mut failed = 0usize;

    for tc in cases {
        let out = run_example(tc.file);
        let ok = check_assert(&out, &tc.assert);
        if ok {
            println!("\x1b[32mPASS {}/{} {} \x1b[0m", tc.group, tc.name, tc.file);
            passed +=1;
        } else {
            println!("\x1b[31mFAIL {}/{} {} \x1b[0m", tc.group, tc.name, tc.file);
            println!("  Assert: {}", tc.assert);
            println!("  Output:\n---\n{}\n---", out);
            failed +=1;
        }
    }

    println!("\nTotal: {} | Passed: {} | Failed: {}", passed+failed, passed, failed);
    if failed > 0 {
        std::process::exit(1);
    }
}