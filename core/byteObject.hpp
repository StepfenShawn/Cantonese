#ifndef BYTE_OBJECT_HPP
#define BYTE_OBJECT_HPP

#include "canObject.hpp"

class Can_String;

template <typename T>
class ArrayList;

class ByteObject : public Can_Object {
    public:
        int _argcout;
        int _nlocals;
        int _stack_size;
        int _flag;

        Can_String* _bytecodes;
        ArrayList<Can_Object*>* _names;
        ArrayList<Can_Object*>* _consts;
        ArrayList<Can_Object*>* _var_names;

        ArrayList<Can_Object*>* _free_vars;
        ArrayList<Can_Object*>* _cell_vars;

        Can_String* co_name;
        Can_String* _file_name;

        int _lineno;
        Can_String* _notable;

        // Construction for ByteObject
        ByteObject(int argcount, int nlocals, int stacksize, int flag, Can_String* bytecodes,
        ArrayList<Can_Object*>* consts, ArrayList<Can_Object*>* names, 
        ArrayList<Can_Object*>* varnames, 
        ArrayList<Can_Object*>* freevars, ArrayList<Can_Object*>* cellvars,
        Can_String* file_name, Can_String* co_name, int lineno, Can_String* notable);
};

#endif