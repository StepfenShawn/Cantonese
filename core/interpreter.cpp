#include "interpreter.hpp"
#include "canstant.hpp"
#include "arrayList.hpp"
#include "map.hpp"
#include "canString.hpp"
#include "canInteger.hpp"

#include <string.h>

#define PUSH(x) _stack->add((x))
#define POP() _stack->pop()

Interpreter::Interpreter() {
    
}