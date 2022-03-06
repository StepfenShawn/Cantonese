#include "canString.hpp"
#include <string.h>


Can_String::Can_String(const char* x) {
    _length = strlen(x);
    _value = new char[_length];
    strcpy(_value, x);
}

Can_String::Can_String(const char* x, const int length) {
    _length = length;
    _value = new char[length];

    for (int i = 0; i < length; i++) {
        _value[i] = x[i];
    }
}