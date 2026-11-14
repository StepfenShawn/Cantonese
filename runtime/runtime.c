#include "runtime.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void* can_alloc(size_t size) {
    void* ptr = malloc(size == 0 ? 1 : size);
    if (ptr == NULL) {
        fputs("RUNTIME: out of memory\n", stderr);
        exit(70);
    }
    return ptr;
}

static void* can_realloc(void* ptr, size_t size) {
    void* next = realloc(ptr, size == 0 ? 1 : size);
    if (next == NULL) {
        fputs("RUNTIME: out of memory\n", stderr);
        exit(70);
    }
    return next;
}

static CanValue can_make(CanTag tag) {
    CanValue v;
    memset(&v, 0, sizeof v);
    v.tag = tag;
    return v;
}

CanValue can_nil() {
    return can_make(CAN_NIL);
}

CanValue can_bool(bool value) {
    CanValue result = can_make(CAN_BOOL);
    result.v.boolean = value;
    return result;
}

CanValue can_int(int64_t value) {
    CanValue result = can_make(CAN_INT);
    result.v.integer = value;
    return result;
}

CanValue can_float(double value) {
    CanValue result = can_make(CAN_FLOAT);
    result.v.floating = value;
    return result;
}

CanValue can_string_len(const char* value, size_t len) {
    CanString* str = can_alloc(sizeof (*str));
    str->len = len;
    str->data = can_alloc(len + 1);
    if (len > 0) {
        memcpy(str->data, value, len);
    }
    str->data[len] = '\0';
    CanValue result = can_make(CAN_STRING);
    result.v.str = str;
    return result;
}

CanValue can_string(const char* value) {
    return can_string_len(value, strlen(value));
}

CanValue can_list_from(int count, const CanValue* items) {
    CanList* l = can_alloc(sizeof (*l));
    l->len = count < 0 ? 0 : (size_t)count;
    l->capacity = l->len == 0 ? 4 : l->len;
    l->items = can_alloc(l->capacity * sizeof (CanValue));
    for (size_t i = 0; i < l->len; i++)
        l->items[i] = items[i];
    CanValue v = can_make(CAN_LIST);
    v.v.list = l;
    return v;
}

static void can_list_append(CanList* list, CanValue value) {
    if (list->len == list->capacity) {
        list->capacity = list->capacity == 0 ? 4 : list->capacity * 2;
        list->items = can_realloc(list->items, list->capacity * sizeof(CanValue));
    }
    list->items[list->len++] = value;
}

CanValue can_map_from(int count, const CanValue *keys, const CanValue *values) {
    CanMap *map = can_alloc(sizeof(*map));
    map->len = count < 0 ? 0 : (size_t)count;
    map->capacity = map->len == 0 ? 4 : map->len;
    map->keys = can_alloc(map->capacity * sizeof(CanValue));
    map->values = can_alloc(map->capacity * sizeof(CanValue));
    for (size_t i = 0; i < map->len; i++) {
        map->keys[i] = keys[i];
        map->values[i] = values[i];
    }

    CanValue result = can_make(CAN_MAP);
    result.v.map = map;
    return result;
}

CanValue can_function(const char *name, CanNativeFn fn) {
    CanFn *f = can_alloc(sizeof(*f));
    f->name = name;
    f->native = fn;

    CanValue result = can_make(CAN_FN);
    result.v.fn = f;
    return result;
}

CanValue can_class_new(const char *name, CanValue parent) {
    CanClass *cls = can_alloc(sizeof(*cls));
    memset(cls, 0, sizeof(*cls));
    cls->name = name;
    cls->parent = parent.tag == CAN_CLASS ? parent.v.class_ : NULL;

    CanValue result = can_make(CAN_CLASS);
    result.v.class_ = cls;
    return result;
}

static CanClass *can_require_class(CanValue value) {
    if (value.tag != CAN_CLASS) {
        can_panic("value is not a class");
    }
    return value.v.class_;
}

void can_class_add_attr(CanValue cls, const char *name, CanValue default_value) {
    CanClass *klass = can_require_class(cls);
    if (klass->attr_count == klass->attr_capacity) {
        klass->attr_capacity = klass->attr_capacity == 0 ? 4 : klass->attr_capacity * 2;
        klass->attr_names =
            can_realloc(klass->attr_names, klass->attr_capacity * sizeof(const char *));
        klass->attr_defaults =
            can_realloc(klass->attr_defaults, klass->attr_capacity * sizeof(CanValue));
    }
    klass->attr_names[klass->attr_count] = name;
    klass->attr_defaults[klass->attr_count] = default_value;
    klass->attr_count++;
}

void can_class_add_method(CanValue cls, const char *name, CanNativeFn fn) {
    CanClass *klass = can_require_class(cls);
    if (klass->method_count == klass->method_capacity) {
        klass->method_capacity =
            klass->method_capacity == 0 ? 4 : klass->method_capacity * 2;
        klass->methods = can_realloc(
            klass->methods, klass->method_capacity * sizeof(CanMethod));
    }
    klass->methods[klass->method_count].name = name;
    klass->methods[klass->method_count].fn = fn;
    klass->method_count++;
}

static void can_map_insert(CanMap *map, CanValue key, CanValue value) {
    CanValue container = can_make(CAN_MAP);
    container.v.map = map;
    can_set_index(container, key, value);
}

static void can_instance_apply_defaults(CanClass *cls, CanMap *fields) {
    if (cls->parent != NULL) {
        can_instance_apply_defaults(cls->parent, fields);
    }
    for (size_t i = 0; i < cls->attr_count; i++) {
        can_map_insert(fields, can_string(cls->attr_names[i]), cls->attr_defaults[i]);
    }
}

CanValue can_class_instantiate(CanValue cls, int argc, const char *const *keys,
                               const CanValue *values) {
    CanClass *klass = can_require_class(cls);

    CanInstance *instance = can_alloc(sizeof(*instance));
    instance->cls = klass;
    instance->fields = can_alloc(sizeof(*instance->fields));
    memset(instance->fields, 0, sizeof(*instance->fields));
    can_instance_apply_defaults(klass, instance->fields);

    CanValue result = can_make(CAN_INSTANCE);
    result.v.instance = instance;

    for (int i = 0; i < argc; i++) {
        can_set_attr(result, keys[i], values[i]);
    }
    return result;
}

static CanMethod *can_find_method(CanClass *cls, const char *name) {
    for (CanClass *current = cls; current != NULL; current = current->parent) {
        for (size_t i = 0; i < current->method_count; i++) {
            if (strcmp(current->methods[i].name, name) == 0) {
                return &current->methods[i];
            }
        }
    }
    return NULL;
}

CanValue can_call_method(CanValue object, const char *name, int argc,
                         const CanValue *args) {
    if (object.tag != CAN_INSTANCE) {
        can_panic("value has no methods");
    }
    CanMethod *method = can_find_method(object.v.instance->cls, name);
    if (method == NULL) {
        can_panic("method not found");
    }

    CanValue *argv = can_alloc((size_t)(argc + 1) * sizeof(CanValue));
    argv[0] = object;
    for (int i = 0; i < argc; i++) {
        argv[i + 1] = args[i];
    }
    CanValue result = method->fn(argc + 1, argv);
    free(argv);
    return result;
}

const char *can_type_name(CanValue value) {
    switch (value.tag) {
        case CAN_NIL: return "NoneType";
        case CAN_BOOL: return "bool";
        case CAN_INT: return "int";
        case CAN_FLOAT: return "float";
        case CAN_STRING: return "str";
        case CAN_LIST: return "list";
        case CAN_MAP: return "dict";
        case CAN_FN: return "function";
        case CAN_CLASS: return "class";
        case CAN_INSTANCE: return "instance";
    }
    return "unknown";
}

bool can_truthy(CanValue value) {
    switch (value.tag) {
        case CAN_NIL: return false;
        case CAN_BOOL: return value.v.boolean;
        case CAN_INT: return value.v.integer != 0;
        case CAN_FLOAT: return value.v.floating != 0.0;
        case CAN_STRING: return value.v.str->len != 0;
        case CAN_LIST: return value.v.list->len != 0;
        case CAN_MAP: return value.v.map->len != 0;
        default: return true;
    }
}

static bool can_is_number(CanValue value) {
    return value.tag == CAN_INT || value.tag == CAN_FLOAT;
}

static double can_as_double(CanValue value) {
    if (value.tag == CAN_INT) {
        return (double)value.v.integer;
    }
    if (value.tag == CAN_FLOAT) {
        return value.v.floating;
    }
    can_panic("expected a number");
    return 0.0;
}

bool can_equal(CanValue a, CanValue b) {
    if (can_is_number(a) && can_is_number(b)) {
        if (a.tag == CAN_INT && b.tag == CAN_INT) {
            return a.v.integer == b.v.integer;
        }
        return can_as_double(a) == can_as_double(b);
    }
    if (a.tag != b.tag) {
        return false;
    }
    switch (a.tag) {
        case CAN_NIL: return true;
        case CAN_BOOL: return a.v.boolean == b.v.boolean;
        case CAN_STRING:
            return a.v.str->len == b.v.str->len &&
                   memcmp(a.v.str->data, b.v.str->data,
                          a.v.str->len) == 0;
        case CAN_LIST: {
            if (a.v.list->len != b.v.list->len) return false;
            for (size_t i = 0; i < a.v.list->len; i++) {
                if (!can_equal(a.v.list->items[i], b.v.list->items[i])) {
                    return false;
                }
            }
            return true;
        }
        case CAN_MAP: {
            if (a.v.map->len != b.v.map->len) return false;
            for (size_t i = 0; i < a.v.map->len; i++) {
                if (!can_equal(a.v.map->values[i], b.v.map->values[i])) {
                    return false;
                }
            }
            return true;
        }
        default: return a.v.pointer == b.v.pointer;
    }
}

int can_compare(CanValue a, CanValue b) {
    if (can_is_number(a) && can_is_number(b)) {
        double left = can_as_double(a);
        double right = can_as_double(b);
        return (left > right) - (left < right);
    }
    if (a.tag == CAN_STRING && b.tag == CAN_STRING) {
        size_t length = a.v.str->len < b.v.str->len
                            ? a.v.str->len
                            : b.v.str->len;
        int cmp = memcmp(a.v.str->data, b.v.str->data, length);
        if (cmp != 0) return cmp;
        return (a.v.str->len > b.v.str->len) -
               (a.v.str->len < b.v.str->len);
    }
    can_panic("values are not comparable");
    return 0;
}

CanValue can_add(CanValue a, CanValue b) {
    if (a.tag == CAN_INT && b.tag == CAN_INT) {
        return can_int(a.v.integer + b.v.integer);
    }
    if (a.tag == CAN_STRING && b.tag == CAN_STRING) {
        return can_concat(a, b);
    }
    if (a.tag == CAN_LIST && b.tag == CAN_LIST) {
        CanValue result = can_list_from((int)a.v.list->len, a.v.list->items);
        for (size_t i = 0; i < b.v.list->len; i++) {
            can_list_append(result.v.list, b.v.list->items[i]);
        }
        return result;
    }
    if (can_is_number(a) && can_is_number(b)) {
        return can_float(can_as_double(a) + can_as_double(b));
    }
    can_panic("unsupported operand types for +");
    return can_nil();
}

CanValue can_sub(CanValue a, CanValue b) {
    if (a.tag == CAN_INT && b.tag == CAN_INT) {
        return can_int(a.v.integer - b.v.integer);
    }
    if (can_is_number(a) && can_is_number(b)) {
        return can_float(can_as_double(a) - can_as_double(b));
    }
    can_panic("unsupported operand types for -");
    return can_nil();
}

CanValue can_mul(CanValue a, CanValue b) {
    if (a.tag == CAN_INT && b.tag == CAN_INT) {
        return can_int(a.v.integer * b.v.integer);
    }
    if (can_is_number(a) && can_is_number(b)) {
        return can_float(can_as_double(a) * can_as_double(b));
    }
    can_panic("unsupported operand types for *");
    return can_nil();
}

CanValue can_div(CanValue a, CanValue b) {
    if (can_is_number(a) && can_is_number(b)) {
        double divisor = can_as_double(b);
        if (divisor == 0.0) can_panic("division by zero");
        return can_float(can_as_double(a) / divisor);
    }
    can_panic("unsupported operand types for /");
    return can_nil();
}

CanValue can_floor_div(CanValue a, CanValue b) {
    if (a.tag == CAN_INT && b.tag == CAN_INT) {
        if (b.v.integer == 0) can_panic("division by zero");
        int64_t left = a.v.integer;
        int64_t right = b.v.integer;
        int64_t quotient = left / right;
        if ((left % right != 0) && ((left < 0) != (right < 0))) {
            quotient -= 1;
        }
        return can_int(quotient);
    }
    if (can_is_number(a) && can_is_number(b)) {
        double divisor = can_as_double(b);
        if (divisor == 0.0) can_panic("division by zero");
        return can_float(floor(can_as_double(a) / divisor));
    }
    can_panic("unsupported operand types for //");
    return can_nil();
}

CanValue can_mod(CanValue a, CanValue b) {
    if (a.tag == CAN_INT && b.tag == CAN_INT) {
        if (b.v.integer == 0) can_panic("division by zero");
        int64_t result = a.v.integer % b.v.integer;
        if (result != 0 && ((result < 0) != (b.v.integer < 0))) {
            result += b.v.integer;
        }
        return can_int(result);
    }
    if (can_is_number(a) && can_is_number(b)) {
        double divisor = can_as_double(b);
        if (divisor == 0.0) can_panic("division by zero");
        return can_float(fmod(can_as_double(a), divisor));
    }
    can_panic("unsupported operand types for %");
    return can_nil();
}

CanValue can_pow(CanValue a, CanValue b) {
    if (can_is_number(a) && can_is_number(b)) {
        double result = pow(can_as_double(a), can_as_double(b));
        if (a.tag == CAN_INT && b.tag == CAN_INT && b.v.integer >= 0) {
            return can_int((int64_t)result);
        }
        return can_float(result);
    }
    can_panic("unsupported operand types for **");
    return can_nil();
}

CanValue can_concat(CanValue a, CanValue b) {
    if (a.tag == CAN_STRING && b.tag == CAN_STRING) {
        size_t length = a.v.str->len + b.v.str->len;
        char *buffer = can_alloc(length + 1);
        memcpy(buffer, a.v.str->data, a.v.str->len);
        memcpy(buffer + a.v.str->len, b.v.str->data,
               b.v.str->len);
        buffer[length] = '\0';
        CanValue result = can_string_len(buffer, length);
        free(buffer);
        return result;
    }
    if (a.tag == CAN_LIST && b.tag == CAN_LIST) {
        return can_add(a, b);
    }
    can_panic("unsupported operand types for <->");
    return can_nil();
}

CanValue can_eq(CanValue a, CanValue b) { return can_bool(can_equal(a, b)); }

CanValue can_not(CanValue value) { return can_bool(!can_truthy(value)); }

CanValue can_neg(CanValue value) {
    if (value.tag == CAN_INT) return can_int(-value.v.integer);
    if (value.tag == CAN_FLOAT) return can_float(-value.v.floating);
    can_panic("unsupported operand type for unary -");
    return can_nil();
}

CanValue can_bit_not(CanValue value) {
    if (value.tag == CAN_INT) return can_int(~value.v.integer);
    can_panic("unsupported operand type for ~");
    return can_nil();
}

CanValue can_and(CanValue a, CanValue b) {
    return can_truthy(a) ? b : a;
}

CanValue can_or(CanValue a, CanValue b) {
    return can_truthy(a) ? a : b;
}

CanValue can_lt(CanValue a, CanValue b) { return can_bool(can_compare(a, b) < 0); }
CanValue can_le(CanValue a, CanValue b) { return can_bool(can_compare(a, b) <= 0); }
CanValue can_gt(CanValue a, CanValue b) { return can_bool(can_compare(a, b) > 0); }
CanValue can_ge(CanValue a, CanValue b) { return can_bool(can_compare(a, b) >= 0); }

static int64_t can_index_to_int(CanValue key, size_t length) {
    if (key.tag != CAN_INT) can_panic("sequence index must be an integer");
    
    int64_t index = key.v.integer;
    if (index < 0) index += (int64_t)length;
    if (index < 0 || (size_t)index >= length) can_panic("index out of range");
    return index;
}

CanValue can_index(CanValue container, CanValue key) {
    if (container.tag == CAN_LIST) {
        int64_t index = can_index_to_int(key, container.v.list->len);
        return container.v.list->items[index];
    }
    if (container.tag == CAN_STRING) {
        int64_t index = can_index_to_int(key, container.v.str->len);
        return can_string_len(container.v.str->data + index, 1);
    }
    if (container.tag == CAN_MAP) {
        for (size_t i = 0; i < container.v.map->len; i++) {
            if (can_equal(container.v.map->keys[i], key)) {
                return container.v.map->values[i];
            }
        }
        can_panic("key not found");
    }
    can_panic("value is not subscriptable");
    return can_nil();
}

void can_set_index(CanValue container, CanValue key, CanValue value) {
    if (container.tag == CAN_LIST) {
        int64_t index = can_index_to_int(key, container.v.list->len);
        container.v.list->items[index] = value;
        return;
    }
    if (container.tag == CAN_MAP) {
        CanMap *map = container.v.map;
        for (size_t i = 0; i < map->len; i++) {
            if (can_equal(map->keys[i], key)) {
                map->values[i] = value;
                return;
            }
        }
        if (map->len == map->capacity) {
            map->capacity = map->capacity == 0 ? 4 : map->capacity * 2;
            map->keys = can_realloc(map->keys, map->capacity * sizeof(CanValue));
            map->values =
                can_realloc(map->values, map->capacity * sizeof(CanValue));
        }
        map->keys[map->len] = key;
        map->values[map->len] = value;
        map->len++;
        return;
    }
    can_panic("value does not support item assignment");
}

CanValue can_attr(CanValue object, const char *name) {
    if (object.tag == CAN_INSTANCE) {
        CanValue key = can_string(name);
        for (size_t i = 0; i < object.v.instance->fields->len; i++) {
            if (can_equal(object.v.instance->fields->keys[i], key)) {
                return object.v.instance->fields->values[i];
            }
        }
        can_panic("attribute not found");
    }
    can_panic("value has no attributes");
    return can_nil();
}

void can_set_attr(CanValue object, const char *name, CanValue value) {
    if (object.tag == CAN_INSTANCE) {
        can_set_index(
            (CanValue){.tag = CAN_MAP, .v.map = object.v.instance->fields},
            can_string(name),
            value);
        return;
    }
    can_panic("value does not support attribute assignment");
}

/* ------------------------------------------------------------------------- */
/* I/O                                                                       */
/* ------------------------------------------------------------------------- */

static void can_print_string(CanString *string) {
    fwrite(string->data, 1, string->len, stdout);
}

void can_print_value(CanValue value) {
    switch (value.tag) {
        case CAN_NIL:
            fputs("None", stdout);
            break;
        case CAN_BOOL:
            fputs(value.v.boolean ? "True" : "False", stdout);
            break;
        case CAN_INT:
            printf("%lld", (long long)value.v.integer);
            break;
        case CAN_FLOAT:
            printf("%g", value.v.floating);
            break;
        case CAN_STRING:
            can_print_string(value.v.str);
            break;
        case CAN_LIST:
            fputc('[', stdout);
            for (size_t i = 0; i < value.v.list->len; i++) {
                if (i > 0) fputs(", ", stdout);
                can_print_value(value.v.list->items[i]);
            }
            fputc(']', stdout);
            break;
        case CAN_MAP:
            fputc('{', stdout);
            for (size_t i = 0; i < value.v.map->len; i++) {
                if (i > 0) fputs(", ", stdout);
                can_print_value(value.v.map->keys[i]);
                fputs(": ", stdout);
                can_print_value(value.v.map->values[i]);
            }
            fputc('}', stdout);
            break;
        case CAN_FN:
            printf("<function %s>", value.v.fn->name);
            break;
        case CAN_CLASS:
            printf("<class %s>", value.v.class_->name);
            break;
        case CAN_INSTANCE:
            printf("<instance %s>", value.v.instance->cls->name);
            break;
    }
}

void can_print_values(int count, const CanValue *values) {
    for (int i = 0; i < count; i++) {
        if (i > 0) fputc(' ', stdout);
        can_print_value(values[i]);
    }
    fputc('\n', stdout);
}

void can_exit(int status) { exit(status); }

void can_panic(const char *message) {
    fprintf(stderr, "Cantonese runtime error: %s\n", message);
    exit(1);
}

void can_env_init() {
    // TODO
}