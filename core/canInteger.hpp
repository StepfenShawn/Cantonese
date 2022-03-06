#ifndef CAN_INTEGER_HPP
#define CAN_INTEGER_HPP

#include "canObject.hpp"

class Can_Integer : Can_Object {
    private:
        int _value;
    public:
        Can_Integer(int x);
        int value() {
            return _value;
        }
};

#endif