/* Opcode */
pub const LOAD_CONST: u8 = 0x64;
pub const POP_TOP: u8 = 0X1;
pub const BINARY_MULTIPLY: u8 = 0X14;
pub const BINARY_DIVIDE: u8 = 0x1b;
pub const BINARY_MODULO: u8 = 0X16;
pub const BINARY_ADD: u8 = 0x17;
pub const BINARY_SUBTRACT: u8 = 0x18;
pub const PRINT_ITEM: u8 = 0x47;
pub const PRINT_NEWLINE: u8 = 0x48;
pub const POP_BLOCK: u8 = 0x57;
pub const STORE_NAME: u8 = 0X5a;
pub const RETURN_VALUE: u8 = 0x53;

pub const LOAD_NAME: u8 = 0x65;
pub const COMPARE_OP: u8 = 0x6b;
pub const JUMP_FORWARD: u8 = 0x6e;
pub const JUMP_ABSOLUTE: u8 = 0x71;
pub const POP_JUMP_IF_FALSE: u8 = 0x72;
pub const LOAD_GLOBAL: u8 = 0x74;
pub const SETUP_LOOP: u8 = 0x78;
pub const LOAD_FAST: u8 = 0x7c;
pub const STORE_FAST: u8 = 0x7d;
pub const CALL_FUNCTION: u8 = 0x83;
pub const MAKE_FUNCTION: u8 = 0x84;