#ifndef OPCODE_HPP
#define OPCODE_HPP

class opCode {
   public:
      static const unsigned char POP_TOP = 1;
      static const unsigned char ROT_TWO = 2;
      static const unsigned char ROT_THREE = 3;
      static const unsigned char DUP_TOP = 4;
      static const unsigned char UNARY_NEGATIVE = 11;
      static const unsigned char BINARY_MULTIPLY = 20;
      static const unsigned char BINARY_MODULO = 22;
      static const unsigned char BINARY_SUBSCR = 25;
      static const unsigned char BINARY_DIVIDE = 21;
      static const unsigned char BINARY_ADD = 23;
      static const unsigned char BINARY_SUBSTRACT = 24;

      static const unsigned char INPLACE_ADD = 55;
      static const unsigned char STORE_MAP = 54;
      static const unsigned char INPLACE_SUBSTRACT = 56;
      static const unsigned char INPLACE_MULTIPLY = 57;
      static const unsigned char INPLACE_DIVIDE = 58;
      static const unsigned char INPLACE_MODULO = 59;
      static const unsigned char STORE_SUBSCR = 60;

      static const unsigned char GET_ITER = 68;

      static const unsigned char PRINT_ITEM = 71;
      static const unsigned char PRINT_NEWLINE = 72;

      static const unsigned char BREAK_LOOP = 80;
      static const unsigned char LOAD_LOCALS = 82;
      static const unsigned char RETURN_VALUE = 83;
      static const unsigned char POP_BLOCK = 87;
      static const unsigned char BUILD_CLASS = 89;

      static const unsigned char HAVE_ARGUMENT = 90; /* Opcodes from here have an argument: */

      static const unsigned char STORE_NAME = 90; /* Index in name list */
      static const unsigned char FOR_ITER = 93;
      static const unsigned char STORE_ATTR = 95;  /* Index in name list */
      static const unsigned char STORE_GLOBAL = 97;
      static const unsigned char DUP_TOPX = 99;   /* number of items to duplicate */
      static const unsigned char LOAD_CONST = 100; /* Index in const list */
      static const unsigned char LOAD_NAME = 101; /* Index in name list */
      static const unsigned char BUILD_LIST = 103;
      static const unsigned char BUILD_MAP = 105;
      static const unsigned char LOAD_ATTR = 106; /* Index in name list */
      static const unsigned char COMPARE_OP = 107; /* Comparison operator */
      static const unsigned char JUMP_FORWARD = 110; /* Number of bytes to skip */
      static const unsigned char JUMP_IF_FALSE_OR_POP = 111; /* Target byte offset from beginning
                                       of code */

      static const unsigned char JUMP_ABSOLUTE = 113;
      static const unsigned char POP_JUMP_IF_FALSE = 114;
      static const unsigned char POP_JUMP_IF_TRUE = 115;
      static const unsigned char LOAD_GLOBAL = 116; /* Index in name list */
      static const unsigned char SETUP_LOOP = 120; /* Target address (relative) */
      static const unsigned char LOAD_FAST  = 124; /* Local variable number */
      static const unsigned char STORE_FAST = 125; /* Local variable number */

      static const unsigned char CALL_FUNCTION = 131;
      static const unsigned char MAKE_FUNCTION = 132;

      enum COMPARE {
         LESS = 0,
         LESS_EQUAL,
         EQUAL,
         NOT_EQUAL,
         GREATER,
         GREATER_EQUAL
      };
};

#endif