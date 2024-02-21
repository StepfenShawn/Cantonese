"""
    Created at 2021/1/16 16:23
    The interpreter for Cantonese    
"""
import cmd
import sys, os
import argparse
from collections import defaultdict

from infoprinter import ptree
from can_error import *

import can_lexer
import can_parser
import can_compile

from libraries.can_lib import *
from web_core.can_web_parser import *

_version_ = "Cantonese\033[5;33m 1.0.8\033[0m Copyright (C) 2020-2024\033[5;35m StepfenShawn\033[0m"
logo = "\033[0;34m" + r"""
   ______            __                           
  / ________ _____  / /_____  ____  ___  ________ 
 / /   / __ `/ __ \/ __/ __ \/ __ \/ _ \/ ___/ _ \
/ /___/ /_/ / / / / /_/ /_/ / / / /  __(__  /  __/
\____/\__,_/_/ /_/\__/\____/_/ /_/\___/____/\___/ 
         
""" + "\033[0m" + "Hope you enjoy it.\nSource: https://github.com/StepfenShawn/Cantonese\n鐘意嘅話star埋我啊! Thank you!" 

class Options:
    dump_ast = False
    dump_lex = False
    mkfile = False
    _to_llvm = False
    debug = False

TO_PY_CODE = ''

def show_pretty_lex(tokens):
    lines_tracker = defaultdict(list)
    for token in tokens:
        lines_tracker[f"line {token.pos.line}"].append(str(token))
    ptree(lines_tracker)

def show_pretty_ast(stats):
    def class_to_dict(obj):
        if isinstance(obj, dict):
            return {k: class_to_dict(v) for k, v in obj.items()}
        if isinstance(obj, can_parser.can_ast.Stat):
            return class_to_dict(vars(obj))
        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(class_to_dict(x) for x in obj)
        else:
            return obj

    for stat in stats:
        ptree({"%s" % stat.__class__.__name__: class_to_dict(stat)}, depth=10)

def cantonese_run(code: str, is_to_py : bool, file : str, 
                    REPL = False, get_py_code = False) -> None:
    
    global TO_PY_CODE
    global variable
  
    tokens = can_lexer.cantonese_token(file, code)

    if Options.dump_lex:
        show_pretty_lex(tokens)
        exit()

    stats = can_parser.StatParser(tokens, file=file).parse_stats()

    if Options.dump_ast:
        show_pretty_ast(stats)
        exit()
    
    code_gen = can_compile.Codegen(stats, file)    
    TO_PY_CODE = ''
    for stat in stats:
        TO_PY_CODE += code_gen.codegen_stat(stat)

    
    if Options._to_llvm:
        import llvm_core.can_llvm_build as can_llvm_build
        import llvm_core.llvm_evaluator as llvm_evaluator
        evaluator = llvm_evaluator.LLvmEvaluator(file)
        for i,stat in enumerate(stats):
            if i != len(stats) - 1:
                evaluator.evaluate(stat, llvmdump=Options.debug)
            else:
                evaluator.evaluate(stat, llvmdump=Options.debug, endMainBlock=True)
        exit()

    cantonese_lib_init()
    if is_to_py:
        print(TO_PY_CODE)

    if Options.mkfile:
        f = open(file[: len(file) - 10] + '.py', 'w', encoding = 'utf-8')
        f.write("###########################################\n")
        f.write("#        Generated by Cantonese           #\n")
        f.write("###########################################\n")
        f.write("# Run it by " + "'cantonese " + file[: len(file) - 10] + '.py' + " -build' \n")
        f.write(TO_PY_CODE)
    
    if Options.debug:
        import dis
        print(dis.dis(TO_PY_CODE))
    else:
        import traceback
        try:
            c = TO_PY_CODE
            if REPL:
                TO_PY_CODE = "" # reset the global variable in REPL mode
            if get_py_code:
                return c
            exec(TO_PY_CODE, variable)
        except Exception as e:
            print("濑嘢!" + "\n".join(濑啲咩嘢(e)))

class 交互(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = '> '
    
    def var_def(self, key):
        pass
    
    def run(self, code):
        if code in variable.keys():
            print(variable[code])
        try:
            exec(code, variable)
        except Exception as e:
            print("濑嘢!" + "\n".join(濑啲咩嘢(e)))

    def default(self, code):
        
        global kw_exit_1
        global kw_exit_2
        global kw_exit

        if code is not None:
            if code == ".quit":
                sys.exit(1)
            c = cantonese_run(code, False, '【标准输入】', 
                REPL = True, get_py_code = True)
            if len(c) == 0:
                c = code
            self.run(c)


def 开始交互():
    global _version_
    print(_version_)
    import time
    交互().cmdloop(str(time.asctime(time.localtime(time.time()))))

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", nargs = '?', default = "")
    arg_parser.add_argument("others", nargs = '?', default = "")
    arg_parser.add_argument("-to_py", action = "store_true", help = "Translate Cantonese to Python")
    arg_parser.add_argument("-讲翻py", action = "store_true", help = "Translate Cantonese to Python")
    arg_parser.add_argument("-to_web", action = "store_true")
    arg_parser.add_argument("-倾偈", action = "store_true")
    arg_parser.add_argument("-update", action = "store_true")
    arg_parser.add_argument("-compile", action = "store_true")
    arg_parser.add_argument("-讲白啲", action = "store_true")
    arg_parser.add_argument("-build", action = "store_true")
    arg_parser.add_argument("-ast", action = "store_true")
    arg_parser.add_argument("-lex", action = "store_true")
    arg_parser.add_argument("-debug", action = "store_true")
    arg_parser.add_argument("-v", "-verison", action = "store_true", help = "Print the version")
    arg_parser.add_argument("-mkfile", action = "store_true")
    arg_parser.add_argument("-l", action = "store_true")
    arg_parser.add_argument("-llvm", action = "store_true")
    args = arg_parser.parse_args()

    global _version_

    if args.v:
        print(_version_, logo)
        sys.exit(1)

    if not args.file:
        sys.exit(开始交互())

    if not os.path.exists(args.file):
        print("Error occurred when checking the path of file!")
        ptree({f"File `{args.file}`": ["\033[0;31m濑嘢!!!\033[0m: 揾唔到你嘅文件 :("]},
                sprout_str='> ')
    else: 
        is_to_py = False
        code = ""
        with open(args.file, encoding = "utf-8") as f:
            code = f.read()

        if args.build:
            cantonese_lib_init()
            exec(code, variable)
            exit()
        if args.to_py or args.讲翻py:
            is_to_py = True
        if args.to_web or args.倾偈:
            if args.compile or args.讲白啲:
                cantonese_web_run(code, args.file, False)
            else:
                cantonese_web_run(code, args.file, True)
        if args.ast:
            Options.dump_ast = True
        if args.lex:
            Options.dump_lex = True
        if args.debug:
            Options.debug = True
        if args.mkfile:
            Options.mkfile = True
        if args.llvm or args.l:
            Options._to_llvm = True
        
        cantonese_run(code, is_to_py, args.file)

if __name__ == '__main__':
    # Support colorful fonts on windows
    if os.name == "nt":
        os.system("")

    main()