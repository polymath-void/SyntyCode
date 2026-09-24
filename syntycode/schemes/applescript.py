def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"-- AppleScript Module: {name}\n\n"
    code += "\n\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    inputs = ", ".join(properties.get("inputs", []))
    code = f"{indent}on {name}({inputs})\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}end {name}"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    val_code = formatter.format_node(children_ids[0], 0) if children_ids else '""'
    return f"{indent}set {name} to {val_code}"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    args = ", ".join(properties.get("args", []))
    return f"{indent}{name}({args})"

def format_condition(formatter, name, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0)
        code += f"{indent}if {check_code} then\n"
        code += formatter.format_node(children_ids[1], indent_level + 1) + "\n"
        if len(children_ids) >= 3:
            code += f"{indent}else\n"
            code += formatter.format_node(children_ids[2], indent_level + 1) + "\n"
        code += f"{indent}end if"
    return code


def format_import(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}# import {name}"

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    if isinstance(inherits, list) and inherits: inherits = inherits[0]
    body = "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) if children_ids else ""
    return f"{indent}# class {name}\n{body}"

def format_loop(formatter, name, properties, children_ids, indent_level, indent):
    condition = properties.get("condition", "true")
    body = "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) if children_ids else f"{indent}    // empty"
    return f"{indent}# loop {condition}\n{body}"

def format_trycatch(formatter, name, properties, children_ids, indent_level, indent):
    exc_type = properties.get("exception_type", "Exception")
    if isinstance(exc_type, list) and exc_type: exc_type = exc_type[0]
    exc_var = properties.get("exception_var", "e")
    
    try_body = formatter.format_node(children_ids[0], indent_level + 1) if len(children_ids) > 0 else f"{indent}    // empty"
    catch_body = formatter.format_node(children_ids[1], indent_level + 1) if len(children_ids) > 1 else f"{indent}    // empty"
    return f"{indent}# try\n{try_body}\n{indent}# catch\n{catch_body}"

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids: return f"{indent}// empty block"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}{name}"
