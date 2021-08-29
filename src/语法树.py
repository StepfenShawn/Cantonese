"""
    AST node for the Token List
"""
def node_print_new(Node : list, arg) -> None:
    """
        Node_print
            |
           arg
    """
    Node.append(["node_print", arg])

def node_sleep_new(Node : list, arg) -> None:
    """
        Node_sleep
            |
           arg
    """
    Node.append(["node_sleep", arg])

def node_break_new(Node : list) -> None:
    Node.append(["node_break"])

def node_exit_new(Node : list) -> None:
    """
        Node_exit
            |
           arg
    """
    Node.append(["node_exit"])

def node_let_new(Node : list, key ,value) -> None:
    """
        Node_let
          /  \
        key   value
    """
    Node.append(["node_let", key, value])

def node_if_new(Node : list, cond, stmt) -> None:
    """
        Node_if
          /  \
        cond  stmt
    """
    Node.append(["node_if", cond, stmt])

def node_elif_new(Node : list, cond, stmt) -> None:
    """
        Node_elif
          /  \
        cond  stmt
    """
    Node.append(["node_elif", cond, stmt])

def node_else_new(Node : list, stmt) -> None:
    """
        Node_else
            |
           stmt
    """
    Node.append(["node_else", stmt])

def node_loop_new(Node : list, cond, stmt) -> None:
    """
        Node_loop
          /  \
        cond  stmt
    """
    Node.append(["node_loop", cond, stmt])

def node_func_new(Node : list, func_name, args, body) -> None:
    """
        Node_fundef
         /  |  \
       name args body
    """
    Node.append(["node_fundef", func_name, args, body])

def node_call_new(Node : list, func_name) -> None:
    """
        Node_call
            |
           name
    """
    Node.append(["node_call", func_name])

def node_build_in_func_call_new(Node : list, var, func_name, args) -> None:
    """
        Node_bcall
          /  \
        name  args
    """
    Node.append(["node_bcall", var, func_name, args])

def node_import_new(Node : list, name) -> None:
    """
        Node_import
            |
           name
    """
    Node.append(["node_import", name])

def node_return_new(Node : list, v) -> None:
    """
        Node_return
            |
          value
    """
    Node.append(["node_return", v])

def node_try_new(Node : list, try_part) -> None:
    """
        Node_try
           |
          stmt
    """
    Node.append(["node_try", try_part])

def node_except_new(Node : list, _except, except_part) -> None:
    """
        Node_except
          /  \
     exception  stmt
    """
    Node.append(["node_except", _except, except_part])

def node_finally_new(Node : list, finally_part) -> None:
    """
        Node_finally
            |
           stmt
    """
    Node.append(["node_finally", finally_part])

def node_raise_new(Node : list, execption) -> None:
    """
        Node_raise
            |
          exception
    """
    Node.append(["node_raise", execption])

def node_for_new(Node : list, iterating_var, sequence, stmt_part) -> None:
    """
        Node_for
         /  |  \
        iter seq stmt
    """
    Node.append(["node_for", iterating_var, sequence, stmt_part])

def node_turtle_new(Node : list, instruction) -> None:
    Node.append(["node_turtle", instruction])

def node_assert_new(Node : list, args) -> None:
    Node.append(["node_assert", args])

def node_model_new(Node : list, model, datatest) -> None:
    """
        Node_model
          /  \
         model dataset
    """
    Node.append(["node_model", model, datatest])

def node_gettype_new(Node : list, value) -> None:
    Node.append(["node_gettype", value])

def node_class_new(Node : list, name, extend, method) -> None:
    """
        Node_class
          / | \
        name extend method
    """
    Node.append(["node_class", name, extend, method])

def node_attribute_new(Node : list, attr_list) -> None:
    Node.append(["node_attr", attr_list])

def node_method_new(Node : list, name, args, stmt) -> None:
    """
        Node_method
         / | \
        name args stmt
    """
    Node.append(["node_method", name, args, stmt])

def node_cmd_new(Node : list, cmd) -> None:
    """
        Node_cmd
            |
        conmmand
    """
    Node.append(["node_cmd", cmd])

def node_list_new(Node : list, name, list) -> None:
    """
        Node_list
          /  \
        name list
    """
    Node.append(["node_list", name, list])

def node_stack_new(Node : list, name) -> None:
    """
        Node_stack
            |
           name
    """
    Node.append(["node_stack", name])
