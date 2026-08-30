"""Integration test runner"""

import subprocess
import sys
from dataclasses import dataclass, field

RUN = "cantonese"

GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"


@dataclass
class TestCase:
    group: str
    name: str
    file: str
    assert_type: str  # "eq", "contains", "no_contains_and_non_empty"
    expected: str = ""


def run_example(path: str) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "cantonese_rs.cantonese", path],
        capture_output=True,
        text=True,
    )
    combined = (result.stdout + result.stderr).replace("\r\n", "\n")
    # Filter out Python's RuntimeWarning about module order ( harmless noise )
    filtered = []
    skip_next = False
    for line in combined.split("\n"):
        if "found in sys.modules after import of package" in line:
            skip_next = True
            continue
        if skip_next and "warn(RuntimeWarning(msg))" in line:
            skip_next = False
            continue
        skip_next = False
        filtered.append(line)
    return "\n".join(filtered)


def check_assert(output: str, tc: TestCase) -> bool:
    if tc.assert_type == "eq":
        return output == tc.expected
    elif tc.assert_type == "contains":
        return tc.expected in output
    elif tc.assert_type == "no_contains_and_non_empty":
        return tc.expected not in output and len(output) > 0
    return False


def format_assert(tc: TestCase) -> str:
    if tc.assert_type == "eq":
        return f"expect == {tc.expected!r}"
    elif tc.assert_type == "contains":
        return f"expect contains {tc.expected!r}"
    elif tc.assert_type == "no_contains_and_non_empty":
        return f"expect not contains {tc.expected!r} and non-empty"
    return ""


cases: list[TestCase] = [
    # ========== BasicTest ==========
    TestCase("BasicTest", "test_hello_world", "examples/basic/HelloWorld.cantonese", "eq", "Hello World!\n"),
    TestCase("BasicTest", "test_assign", "examples/basic/assign.cantonese", "eq", "1\n3\n"),
    TestCase("BasicTest", "test_comment", "examples/basic/comment.cantonese", "eq", "Run OK\n"),
    TestCase("BasicTest", "test_assert", "examples/basic/assert.cantonese", "contains", "AssertionError"),
    TestCase("BasicTest", "test_class", "examples/basic/class.cantonese", "eq", "Duck is swimming\nDuck is sleeping\n公\n"),
    TestCase("BasicTest", "test_callpython", "examples/basic/call_python.cantonese", "eq", "10\n"),
    TestCase("BasicTest", "test_exit", "examples/basic/exit.cantonese", "eq", "执行exit\n"),
    TestCase("BasicTest", "test_for", "examples/basic/for.cantonese", "eq", "1\n2\n3\n4\n1\n2\n3\n"),
    TestCase("BasicTest", "test_function", "examples/basic/function.cantonese", "eq", "Hello\nHello World1\n"),
    TestCase("BasicTest", "test_if", "examples/basic/if.cantonese", "eq", "A 係 3\nB 係 1\n"),
    TestCase("BasicTest", "test_import", "examples/basic/import.cantonese", "eq", "1\n3\n5.0\n1\n测试成功\n"),
    TestCase("BasicTest", "test_lambda", "examples/basic/lambda.cantonese", "eq", "4\n"),
    TestCase("BasicTest", "test_list", "examples/basic/list.cantonese", "eq", "[2, 3, 3]\n3\n2\n3\n3\n[]\n"),
    TestCase("BasicTest", "test_match", "examples/basic/match.cantonese", "eq", "Not found\n"),
    TestCase("BasicTest", "test_raise", "examples/basic/raise.cantonese", "contains", "ImportError"),
    TestCase("BasicTest", "test_set", "examples/basic/set.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("BasicTest", "test_try_finally", "examples/basic/try_finally.cantonese", "eq", "揾到NameError\n执手尾: \n1 1\n"),
    TestCase("BasicTest", "test_type", "examples/basic/type.cantonese", "eq", "<class 'int'>\n<class 'cantonese_rs.libs.std.impl.Str'>\n"),
    TestCase("BasicTest", "test_while", "examples/basic/while.cantonese", "eq", "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"),
    # ========== AlgoTest ==========
    TestCase("AlgoTest", "test_binary_search", "examples/algorithms/binary_search.cantonese", "eq", "揾到啦!!!\n揾唔到: (\n"),
    TestCase("AlgoTest", "test_bubble_sort", "examples/algorithms/bubble_sort.cantonese", "eq", "[11, 12, 22, 25, 34, 64, 90]\n[12, 21, 22, 55, 77, 90, 97]\n"),
    TestCase("AlgoTest", "test_fib", "examples/algorithms/fib.cantonese", "eq", "55\n1\n"),
    TestCase("AlgoTest", "test_factorial", "examples/algorithms/factorial.cantonese", "eq", "2\n720\n"),
    TestCase("AlgoTest", "test_fizzbuzz", "examples/algorithms/fizzbuzz.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("AlgoTest", "test_insert_sort", "examples/algorithms/insert_sort.cantonese", "eq", "[11, 12, 22, 25, 34, 64, 90]\n[12, 21, 22, 55, 77, 90, 97]\n"),
    TestCase("AlgoTest", "test_linear_search", "examples/algorithms/linear_search.cantonese", "eq", "揾到啦:)\n揾唔到:(\n"),
    TestCase("AlgoTest", "test_max", "examples/algorithms/max.cantonese", "eq", "34\n27\n"),
    TestCase("AlgoTest", "test_Tower_of_Hanoi", "examples/algorithms/Tower_of_Hanoi.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("AlgoTest", "test_climbStairs", "examples/leetcode/climbStairs.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("AlgoTest", "test_getSum", "examples/leetcode/getSum.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("AlgoTest", "test_numIdenticalPairs", "examples/leetcode/numIdenticalPairs.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("AlgoTest", "test_rotateString", "examples/leetcode/rotateString.cantonese", "no_contains_and_non_empty", "濑嘢"),
    TestCase("AlgoTest", "test_singleNumber", "examples/leetcode/singleNumber.cantonese", "no_contains_and_non_empty", "濑嘢"),
    # ========== MiscTest ==========
    TestCase("MiscTest", "test_calc_corr", "examples/numerical/calc_corr.cantonese", "eq", "0.8066499427138474\n"),
    TestCase("MiscTest", "test_Matrix", "examples/numerical/Matrix.cantonese", "eq", "Matrix: [[1, 1], [2, 2]]\nMatrix: [[2, 2], [3, 3]]\nMatrix: [[3, 3], [5, 5]]\nMatrix: [[3, 3, 3], [6, 6, 6]]\n"),
    TestCase("MiscTest", "test_knn", "examples/machine_learning/KNN.cantonese", "eq", "动作片\n"),
    TestCase("MiscTest", "test_linear_regression", "examples/machine_learning/linear_regression.cantonese", "eq", "Linear function is:\ny=0.530960991635149x+189.75347155122432\n667.6183640228585\n"),
    # ========== LibTest ==========
    TestCase("LibTest", "test_csv_parse", "examples/lib_sample/csv_parse.cantonese", "eq", "['id', 'name', ' age', 'gender', 'class_num']\n['1001', '张三', '18', 'male', '01']\n['1002', '李四', '19', 'male', '01']\n['1003', '王五', '19', 'famale', '01']\n['1004', '李华', '18', 'male', '01']\n"),
    TestCase("LibTest", "test_file", "examples/lib_sample/file.cantonese", "no_contains_and_non_empty", "濑嘢!"),
    TestCase("LibTest", "test_random", "examples/lib_sample/random.cantonese", "no_contains_and_non_empty", "濑嘢!"),
    TestCase("LibTest", "test_re", "examples/lib_sample/re.cantonese", "eq", "(0, 3)\nNone\n"),
]


def main() -> int:
    print("OK sir! Ready to test!!!")

    passed = 0
    failed = 0

    for tc in cases:
        out = run_example(tc.file)
        ok = check_assert(out, tc)
        if ok:
            print(f"{GREEN}PASS {tc.group}/{tc.name} {tc.file} {RESET}")
            passed += 1
        else:
            print(f"{RED}FAIL {tc.group}/{tc.name} {tc.file} {RESET}")
            print(f"  Assert: {format_assert(tc)}")
            print(f"  Output:\n---\n{out}\n---")
            failed += 1

    total = passed + failed
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
