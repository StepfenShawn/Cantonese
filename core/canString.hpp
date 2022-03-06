#ifndef CAN_STRING_HPP
#define CAN_STRINF_HPP

#include "canObject.hpp"

class Can_String : Can_Object {
    private: 
        char* _value;
        int _length;

    public:
        Can_String(const char* x);
        Can_String(const char* x, int length);

        const char* value() {return _value;}
        int Length() {return _length;}
};

#endif