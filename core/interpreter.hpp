#ifndef INTERPRETER_HPP
#define INTERPRETER_HPP

#include "opCode.hpp"
#include "byteObject.hpp"

class Interpreter {
private:
    ArrayList<Can_Object*>* _stack;
    ArrayList<Can_Object*>* _consts;
public:
    Interpreter();

    void run(ByteObject* codes);
};

#endif