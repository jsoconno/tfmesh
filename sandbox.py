import operator

def version_tuple(version):
    """
    Turns a semantic version value into a tuple used for version comparison operations.
    """
    return tuple(map(int, (version.split("."))))

def compare_versions(a, op, b):
    """
    Takes two tuples and compares them based on valid operations.
    """
    ops = {
        "<": operator.lt,
        "<=": operator.le,
        "=": operator.eq,
        "!=": operator.ne,
        ">=": operator.ge,
        ">": operator.gt,
    }

    if op == "~>":
        if len(b) == 2:
            result = ops[">="](a, b) and ops["<"](a, (b[0]+1, 0, 0))
        elif len(b) == 3:
            result = ops[">="](a, b) and ops["<"](a, (b[0], b[1]+1, 0))
        else:
            raise ValueError("When using a pessimistic version constraint, the version value must only have two or three parts (e.g. 1.0, 1.1.0).")
    else:
        result = ops[op](a, b)

    return result