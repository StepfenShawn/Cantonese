#include "byteObject.hpp"

ByteObject::ByteObject(int argcount, int nlocals, int stacksize, int flag, Can_String* bytecodes,
        ArrayList<Can_Object*>* consts, ArrayList<Can_Object*>* names, 
        ArrayList<Can_Object*>* varnames, 
        ArrayList<Can_Object*>* freevars, ArrayList<Can_Object*>* cellvars,
        Can_String* file_name, Can_String* co_name, int lineno, Can_String* notable):
    _argcount(argcount),
    _nlocals(nlocals),
    _stack_size(stacksize),
    _flag(flag),
    _bytecodes(bytecodes),
    _names(names),
    _consts(consts),
    _var_names(varnames),
    _free_vars(freevars),
    _cell_vars(cellvars),
    _co_name(co_name),
    _file_name(file_name),
    _lineno(lineno),
    _notable(notable){}