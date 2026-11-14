#pragma once

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef _cplusplus
extern "C" {
#endif

typedef enum CanTag {
    CAN_NIL = 0,
    CAN_BOOL,
    CAN_INT,
    CAN_FLOAT,
    CAN_STRING,
    CAN_LIST,
    CAN_MAP,
    CAN_FN,
    CAN_CLASS,
    CAN_INSTANCE
} CanTag;

typedef struct CanValue CanValue;
typedef struct CanString CanString;
typedef struct CanList CanList;
typedef struct CanMap CanMap;
typedef struct CanFn CanFn;
typedef struct CanClass CanClass;
typedef struct CanInstance CanInstance;

typedef CanValue (*CanNativeFn)(int argc, CanValue* argv);

typedef struct CanMethod {
    const char* name;
    CanNativeFn fn;
} CanMethod;

struct CanString {
    size_t len;
    char* data;
};

struct CanList {
    size_t len;
    size_t capacity;
    CanValue* items;
};

struct CanMap {
    size_t len;
    size_t capacity;
    CanValue* keys;
    CanValue* values;
};

struct CanFn {
    const char* name;
    CanNativeFn native;
};

struct CanClass {
    const char* name;
    CanClass* parent;
    size_t attr_count;
    size_t attr_capacity;
    const char** attr_names;
    CanValue* attr_defaults;
    size_t method_count;
    size_t method_capacity;
    CanMethod* methods;
};

struct CanInstance {
    CanClass* cls;
    CanMap* fields;
};

struct CanValue {
    CanTag tag;
    union {
        bool boolean;
        int64_t integer;
        double floating;
        CanString* str;
        CanList* list;
        CanMap* map;
        CanFn* fn;
        CanClass* class_;
        CanInstance* instance;
        void* pointer;
    } v;
};

/// Constructors
CanValue can_nil(void);
CanValue can_bool(bool value);
CanValue can_int(int64_t value);
CanValue can_float(double value);
CanValue can_string(const char *value);
CanValue can_string_len(const char *value, size_t len);
CanValue can_list_from(int count, const CanValue *items);
CanValue can_map_from(int count, const CanValue *keys, const CanValue *values);
CanValue can_function(const char *name, CanNativeFn fn);

/// Conversisons and predicates
const char* can_type_name(CanValue value);
bool can_truthy(CanValue value);
bool can_equal(CanValue a, CanValue b);
int can_compare(CanValue a, CanValue b);
CanValue can_eq(CanValue a, CanValue b);

/// Operators
CanValue can_add(CanValue a, CanValue b);
CanValue can_sub(CanValue a, CanValue b);
CanValue can_mul(CanValue a, CanValue b);
CanValue can_div(CanValue a, CanValue b);
CanValue can_floor_div(CanValue a, CanValue b);
CanValue can_mod(CanValue a, CanValue b);
CanValue can_pow(CanValue a, CanValue b);
CanValue can_concat(CanValue a, CanValue b);
CanValue can_not(CanValue value);
CanValue can_neg(CanValue value);
CanValue can_bit_not(CanValue value);
CanValue can_and(CanValue a, CanValue b);
CanValue can_or(CanValue a, CanValue b);
CanValue can_lt(CanValue a, CanValue b);
CanValue can_le(CanValue a, CanValue b);
CanValue can_gt(CanValue a, CanValue b);
CanValue can_ge(CanValue a, CanValue b);

/// Classes and instances
CanValue can_class_new(const char *name, CanValue parent);
void can_class_add_attr(CanValue cls, const char *name, CanValue default_value);
void can_class_add_method(CanValue cls, const char *name, CanNativeFn fn);
CanValue can_class_instantiate(CanValue cls, int argc, const char *const *keys,
                               const CanValue *values);
CanValue can_call_method(CanValue object, const char *name, int argc,
                         const CanValue *args);

/// Containers
CanValue can_index(CanValue container, CanValue key);
void can_set_index(CanValue container, CanValue key, CanValue value);
CanValue can_attr(CanValue object, const char *name);
void can_set_attr(CanValue object, const char *name, CanValue value);

void can_print_values(int count, const CanValue *values);
void can_print_value(CanValue value);
void can_exit(int status);

/* Report a fatal runtime error.  Never returns. */
void can_panic(const char *message);

void can_env_init();

#ifdef _cplusplus
}
#endif