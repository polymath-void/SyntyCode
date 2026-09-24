import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _helpers import (translate_self_ref, strip_self_from_inputs, translate_constructor_name,
                      translate_super_call, translate_loop, translate_variable_value)

LANG = "ruby"

def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"module {name}\n"
    code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += "end"
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    raw_inputs = strip_self_from_inputs(properties.get("inputs", []))
    inputs = ", ".join(raw_inputs)
    fn_name = translate_constructor_name(name, "initialize")
    
    code = f"{indent}def {fn_name}({inputs})\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}end"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    # Ruby uses @ for instance variables
    if name.startswith("self."):
        clean_name = "@" + name[5:]
    else:
        clean_name = name
    val_code = translate_variable_value(properties, children_ids, formatter, "nil")
    return f"{indent}{clean_name} = {val_code}"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    if name.startswith("self."):
        clean_name = name[5:]
    else:
        clean_name = name
    clean_name = translate_super_call(clean_name, "super")
    args = ", ".join(properties.get("args", []))
    if args:
        return f"{indent}{clean_name}({args})"
    return f"{indent}{clean_name}"

def format_condition(formatter, name, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0)
        code += f"{indent}if {check_code}\n"
        code += formatter.format_node(children_ids[1], indent_level + 1) + "\n"
        if len(children_ids) >= 3:
            code += f"{indent}else\n"
            code += formatter.format_node(children_ids[2], indent_level + 1) + "\n"
        code += f"{indent}end"
    return code

def format_import(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}require \"{name}\""

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    if isinstance(inherits, list) and inherits:
        base = f" < {inherits[0]}"
    elif inherits:
        base = f" < {inherits}"
    else:
        base = ""
    
    code = f"{indent}class {name}{base}\n"
    if children_ids:
        code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    else:
        code += f"{indent}    # empty\n"
    code += f"{indent}end"
    return code

def format_loop(formatter, name, properties, children_ids, indent_level, indent):
    condition = properties.get("condition", "")
    header = translate_loop(name, condition, LANG)
    code = f"{indent}{header}\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}end"
    return code

def format_trycatch(formatter, name, properties, children_ids, indent_level, indent):
    exc_type = properties.get("exception_type", "StandardError")
    exc_var = properties.get("exception_var", "e") or "e"
    code = f"{indent}begin\n"
    if len(children_ids) > 0:
        code += formatter.format_node(children_ids[0], indent_level + 1) + "\n"
    code += f"{indent}rescue {exc_type} => {exc_var}\n"
    if len(children_ids) > 1:
        code += formatter.format_node(children_ids[1], indent_level + 1) + "\n"
    code += f"{indent}end"
    return code

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}# empty block"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}{name}"

EXT = "rb"
CONFIG = {"comment_prefix": "#"}
