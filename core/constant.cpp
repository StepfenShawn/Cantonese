#include "canstant.hpp"
#include "canInteger.hpp"
#include "canObject.hpp"

Can_Integer Constant::Can_True = NULL;
Can_Integer Constant::Can_False = NULL;
Can_Object Constant::Can_None = NULL;

void Constant::gensis() {
    Can_True = new Can_Integer(1);
    Can_False = new Can_Integer(0);
    Can_None = new Can_Object();
}

void Constant::destroy() {

}