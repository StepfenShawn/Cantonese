#ifndef _CONSTANT_HPP
#define _CONSTANT_HPP

#include <stdio.h>

class Can_Integer;
class Can_Object;

class Constant {
public:
    static Can_Integer* Can_True;
    static Can_Integer* Can_False;
    static Can_Object* Can_None;

public:
    static void genesis();
    static void destroy();
};

#endif