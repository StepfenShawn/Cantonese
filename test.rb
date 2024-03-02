#coding:utf-8
require 'test/unit'

RUN = "python can_source/cantonese.py "

puts "OK sir! Ready to test!!!"
puts %q{
     ______            __                           
    / ________ _____  / /_____  ____  ___  ________ 
   / /   / __ `/ __ \/ __/ __ \/ __ \/ _ \/ ___/ _ \
  / /___/ /_/ / / / / /_/ /_/ / / / /  __(__  /  __/
  \____/\__,_/_/ /_/\__/\____/_/ /_/\___/____/\___/ 
        
}

class BasicTest < Test::Unit::TestCase

  def test_hello_world
    res = %x(#{RUN} examples/basic/helloworld.cantonese).encode("UTF-8")
    assert res == "Hello World!\n"
  end

  def test_assign
    res = %x(#{RUN} examples/basic/assign.cantonese).encode("UTF-8")
    assert res == "1\n3\n"
  end

  def test_comment
    res = %x(#{RUN} examples/basic/comment.cantonese).encode("UTF-8")
    assert res == "Run OK\n"
  end

  def test_assert
    res = %x(#{RUN} examples/basic/assert.cantonese).encode("UTF-8")
    assert res.include?("AssertionError")
  end

  def test_class
    res = %x(#{RUN} examples/basic/class.cantonese).encode("UTF-8")
    assert res == "Duck is swimming\nDuck is sleeping\n公\n"
  end

  def test_callpython
    res = %x(#{RUN} examples/basic/call_python.cantonese).encode("UTF-8")
    assert res == "10\n"
  end

  def test_exit
    res = %x(#{RUN} examples/basic/exit.cantonese).encode("UTF-8")
    assert res == "执行exit\n"
  end

  def test_for
    res = %x(#{RUN} examples/basic/for.cantonese).encode("UTF-8")
    assert res == "1\n2\n3\n4\n1\n2\n3\n"
  end

  def test_function
    res = %x(#{RUN} examples/basic/function.cantonese).encode("UTF-8")
    assert res == "Hello\nHello\nHello World1\nHello World2\n"
  end

  def test_if
    res = %x(#{RUN} examples/basic/if.cantonese).encode("UTF-8")
    assert res == "A 係 3\nB 係 1\n"
  end

  def test_import
    res = %x(#{RUN} examples/basic/import.cantonese).encode("UTF-8")
    assert res == "1\n3\n5.0\n1\n测试成功\n"
  end

  def test_lambda
    res = %x(#{RUN} examples/basic/lambda.cantonese).encode("UTF-8")
    assert res == "4\n"
  end

  def test_list
    res = %x(#{RUN} examples/basic/list.cantonese).encode("UTF-8")
    assert res == "[2, 3, 3]\n3\n2\n3\n3\n[]\n"
  end

  def test_match
    res = %x(#{RUN} examples/basic/match.cantonese).encode("UTF-8")
    assert res == "Not found\n"
  end

  def test_raise
    res = %x(#{RUN} examples/basic/raise.cantonese).encode("UTF-8")
    assert res.include?("濑嘢!")
  end

  def test_set
    res = %x(#{RUN} examples/basic/set.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_try_finally
    res = %x(#{RUN} examples/basic/try_finally.cantonese).encode("UTF-8")
    assert res == "揾到NameError\n执手尾: \n1 1\n"
  end

  def test_type
    res = %x(#{RUN} examples/basic/type.cantonese).encode("UTF-8")
    assert res == "<class 'int'>\n<class 'str'>\n"
  end

  def test_while
    res = %x(#{RUN} examples/basic/while.cantonese).encode("UTF-8")
    assert res == "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n"
  end

end

class AlgoTest < Test::Unit::TestCase
  def test_binary_search
    res = %x(#{RUN} examples/algorithms/binary_search.cantonese).encode("UTF-8")
    assert res == "揾到啦!!!\n揾唔到: (\n"
  end

  def test_bubble_sort
    res = %x(#{RUN} examples/algorithms/bubble_sort.cantonese).encode("UTF-8")
    assert res == "[11, 12, 22, 25, 34, 64, 90]\n[12, 21, 22, 55, 77, 90, 97]\n"
  end

  def test_fib
    res = %x(#{RUN} examples/algorithms/fib.cantonese).encode("UTF-8")
    assert res == "55\n1\n"
  end

  def test_factorial
    res = %x(#{RUN} examples/algorithms/factorial.cantonese).encode("UTF-8")
    assert res == "2\n720\n"
  end

  def test_fizzbuzz
    res = %x(#{RUN} examples/algorithms/fizzbuzz.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!"))
  end

  def test_insert_sort
    res = %x(#{RUN} examples/algorithms/insert_sort.cantonese).encode("UTF-8")
    assert res == "[11, 12, 22, 25, 34, 64, 90]\n[12, 21, 22, 55, 77, 90, 97]\n"
  end

  def test_linear_search
    res = %x(#{RUN} examples/algorithms/linear_search.cantonese).encode("UTF-8")
    assert res == "揾到啦:)\n揾唔到:(\n"
  end

  def test_max
    res = %x(#{RUN} examples/algorithms/max.cantonese).encode("UTF-8")
    assert res == "34\n27\n"
  end

  def test_Tower_of_Hanoi
    res = %x(#{RUN} examples/algorithms/Tower_of_Hanoi.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_climbStairs
    res = %x(#{RUN} examples/leetcode/climbStairs.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_getSum
    res = %x(#{RUN} examples/leetcode/getSum.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_numIdenticalPairs
    res = %x(#{RUN} examples/leetcode/numIdenticalPairs.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_rotateString
    res = %x(#{RUN} examples/leetcode/rotateString.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_singleNumber
    res = %x(#{RUN} examples/leetcode/singleNumber.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

end

class MiscTest < Test::Unit::TestCase
  
  def test_calc_corr
    res = %x(#{RUN} examples/numerical/calc_corr.cantonese).encode("UTF-8")
    assert res == "0.8066499427138474\n"
  end

  def test_Matrix
    res = %x(#{RUN} examples/numerical/Matrix.cantonese).encode("UTF-8")
    assert res == "Matrix: [[1, 1], [2, 2]]\nMatrix: [[2, 2], [3, 3]]\nMatrix: [[3, 3], [5, 5]]\nMatrix: [[3, 3, 3], [6, 6, 6]]\n"
  end

  def test_knn
    res = %x(#{RUN} examples/machine_learning/KNN.cantonese).encode("UTF-8")
    assert res == "动作片\n"
  end

  def test_linear_regression
    res = %x(#{RUN} examples/machine_learning/linear_regression.cantonese).encode("UTF-8")
    assert res == "Linear function is:\ny=0.530960991635149x+189.75347155122432\n667.6183640228585\n"
  end

end

class LibTest < Test::Unit::TestCase
  
  def test_csv_parse
    res = %x(#{RUN} examples/lib_sample/csv_parse.cantonese).encode("UTF-8")
    assert res == "['id', 'name', ' age', 'gender', 'class_num']\n['1001', '张三', '18', 'male', '01']\n['1002', '李四', '19', 'male', '01']\n['1003', '王五', '19', 'famale', '01']\n['1004', '李华', '18', 'male', '01']\n"
  end

  def test_file
    res = %x(#{RUN} examples/lib_sample/file.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_random
    res = %x(#{RUN} examples/lib_sample/random.cantonese).encode("UTF-8")
    assert (not res.include?("濑嘢!")) and res != ""
  end

  def test_re
    res = %x(#{RUN} examples/lib_sample/re.cantonese).encode("UTF-8")
    assert res == "(0, 3)\nNone\n"
  end

end

# AppGUITest
