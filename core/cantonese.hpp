#ifndef cantonese_h
#define cantonese_h

#include <cstdio>
#include <cstdint>
#include <string>

#define _CAN_C(ch) L##ch
typedef wchar_t CAN_Char;
typedef char CAN_Byte;
typedef int CAN_Integer;
typedef uint32_t CAN_UINT32;
typedef double CAN_Double;
typedef float CAN_Float;
typedef std::wstring String;
typedef CAN_UINT32 CANHash;
typedef bool CAN_Bool;
typedef std::wostream Ostream;

#endif