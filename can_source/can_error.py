import re


def error_stdout(ty, info):
    if ty == "NameError":
        return re.sub(r"name '(.*)' is not defined", r"唔知`\1`係咩", info)
    return f"{ty}:{info}"
