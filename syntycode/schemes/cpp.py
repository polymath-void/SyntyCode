import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _helpers import (translate_self_ref, strip_self_from_inputs, translate_constructor_name,
                      translate_super_call, translate_loop, translate_variable_value)

LANG = "cpp"

def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"#include <iostream>\n#include <string>\n#include <vector>\n\nnamespace {name} {{\n"
    code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += "}"
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    raw_inputs = strip_self_from_inputs(properties.get("inputs", []))
    inputs = ", ".join([f"auto {inp}" for inp in raw_inputs])
    fn_name = translate_constructor_name(name, "__CLASS__")
    
    code = f"{indent}void {fn_name}({inputs}) {{\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "this", "->")
    val_code = translate_variable_value(properties, children_ids, formatter, "nullptr")
    if not clean_name.startswith("this->"):
        return f"{indent}auto {clean_name} = {val_code};"
    return f"{indent}{clean_name} = {val_code};"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "this", "->")
    clean_name = translate_super_call(clean_name, "Base")
    args = ", ".join(properties.get("args", []))
    return f"{indent}{clean_name}({args});"

def format_condition(formatter, name, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0).rstrip(';')
        code += f"{indent}if ({check_code}) {{\n"
        code += formatter.format_node(children_ids[1], indent_level + 1) + "\n"
        code += f"{indent}}}"
        if len(children_ids) >= 3:
            code += f" else {{\n"
            code += formatter.format_node(children_ids[2], indent_level + 1) + "\n"
            code += f"{indent}}}"
    return code

def format_import(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}#include <{name}>"

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    if isinstance(inherits, list) and inherits:
        base = " : " + ", ".join([f"public {b}" for b in inherits])
    elif inherits:
        base = f" : public {inherits}"
    else:
        base = ""
    
    code = f"{indent}class {name}{base} {{\npublic:\n"
    if children_ids:
        parts = []
        for cid in children_ids:
            rendered = formatter.format_node(cid, indent_level + 1)
            # Replace __init__ with class name for C++ constructors
            rendered = rendered.replace(f"void __CLASS__", f"{name}")
            rendered = rendered.replace(f"void __init__", f"{name}")
            parts.append(rendered)
        code += "\n\n".join(parts) + "\n"
    else:
        code += f"{indent}    // empty\n"
    code += f"{indent}}};"
    return code

def format_loop(formatter, name, properties, children_ids, indent_level, indent):
    condition = properties.get("condition", "true")
    header = translate_loop(name, condition, LANG)
    code = f"{indent}{header} {{\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
    return code

def format_trycatch(formatter, name, properties, children_ids, indent_level, indent):
    exc_type = properties.get("exception_type", "std::exception")
    exc_var = properties.get("exception_var", "e") or "e"
    
    try_body = formatter.format_node(children_ids[0], indent_level + 1) if len(children_ids) > 0 else f"{indent}    // empty"
    catch_body = formatter.format_node(children_ids[1], indent_level + 1) if len(children_ids) > 1 else f"{indent}    // empty"
    return f"{indent}try {{\n{try_body}\n{indent}}} catch ({exc_type}& {exc_var}) {{\n{catch_body}\n{indent}}}"

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}// empty block"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}{name}"

EXT = "cpp"
CONFIG = {"comment_prefix": "//"}
