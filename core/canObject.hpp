#ifndef CAN_OBJECT_HPP
#define CAN_OBJECT_HPP

// This is the base class of all the object in Cantonese.
class Can_Object {
    public:
        virtual void print() {}

        virtual Can_Object* add(Can_Object* x) {};
        virtual Can_Object* greater(Can_Object* x) {}; // >
        virtual Can_Object* less(Can_Object* x) {}; // <
        virtual Can_Object* equal(Can_Object* x) {}; // ==
        virtual Can_Object* not_equal(Can_Object* x) {}; // !=
        virtual Can_Object* ge(Can_Object* x) {}; // >=
        virtual Can_Object* le(Can_Object* x) {}; // <=
};

#endif