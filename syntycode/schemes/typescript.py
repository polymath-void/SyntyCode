import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _helpers import (translate_self_ref, strip_self_from_inputs, translate_constructor_name,
                      translate_super_call, translate_loop, translate_variable_value)

LANG = "typescript"

def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"// Module: {name}\n"
    code += "\n\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    raw_inputs = strip_self_from_inputs(properties.get("inputs", []))
    inputs = ", ".join([f"{inp}: any" for inp in raw_inputs])
    fn_name = translate_constructor_name(name, "constructor")
    
    if fn_name == "constructor":
        code = f"{indent}{fn_name}({inputs}) {{\n"
    else:
        code = f"{indent}function {fn_name}({inputs}) {{\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "this", ".")
    val_code = translate_variable_value(properties, children_ids, formatter, "null").strip().rstrip(';')
    
    if not clean_name.startswith("this."):
        vtype = properties.get("value_type", "")
        type_str = f": {vtype}" if vtype else ""
        return f"{indent}let {clean_name}{type_str} = {val_code};"
    return f"{indent}{clean_name} = {val_code};"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "this", ".")
    clean_name = translate_super_call(clean_name, "super")
    
    # Translate arguments as well
    from _helpers import translate_args
    raw_args = properties.get("args", [])
    args = ", ".join(translate_args(raw_args, "self", "this", "."))
    
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
    names = properties.get("names", [])
    if names:
        return f"{indent}import {{ {', '.join(names)} }} from \"{name}\";"
    return f"{indent}import \"{name}\";"

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    if isinstance(inherits, list) and inherits:
        base = f" extends {inherits[0]}"
    elif inherits:
        base = f" extends {inherits}"
    else:
        base = ""
    
    code = f"{indent}class {name}{base} {{\n"
    if children_ids:
        # For TS, methods inside a class don't need 'function' keyword
        parts = []
        for cid in children_ids:
            rendered = formatter.format_node(cid, indent_level + 1)
            # Strip 'function ' prefix for class methods (but not constructor)
            if rendered.strip().startswith("function "):
                rendered = rendered.replace("function ", "", 1)
            parts.append(rendered)
        code += "\n".join(parts) + "\n"
    else:
        code += f"{indent}    // empty\n"
    code += f"{indent}}}"
    return code

def format_loop(formatter, name, properties, children_ids, indent_level, indent):
    condition = properties.get("condition", "true").replace("self.", "this.")
    header = translate_loop(name, condition, LANG)
    code = f"{indent}{header} {{\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
    return code

def format_trycatch(formatter, name, properties, children_ids, indent_level, indent):
    exc_var = properties.get("exception_var", "e") or "e"
    
    try_body = formatter.format_node(children_ids[0], indent_level + 1) if len(children_ids) > 0 else f"{indent}    // empty"
    catch_body = formatter.format_node(children_ids[1], indent_level + 1) if len(children_ids) > 1 else f"{indent}    // empty"
    return f"{indent}try {{\n{try_body}\n{indent}}} catch ({exc_var}) {{\n{catch_body}\n{indent}}}"

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}// empty block"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    # Identifiers often contain raw expressions like `self.chain[i]`
    from _helpers import translate_self_ref
    clean_name = name.replace("self.", "this.")
    if clean_name == "False":
        clean_name = "false"
    elif clean_name == "True":
        clean_name = "true"
    return f"{indent}{clean_name}"

def format_return(formatter, name, properties, children_ids, indent_level, indent):
    if children_ids:
        val = formatter.format_node(children_ids[0], 0).strip().rstrip(';')
        return f"{indent}return {val};"
    return f"{indent}return;"

def format_binaryop(formatter, name, properties, children_ids, indent_level, indent):
    op = properties.get('operator', '+')
    left = formatter.format_node(children_ids[0], 0) if len(children_ids) > 0 else ''
    right = formatter.format_node(children_ids[1], 0) if len(children_ids) > 1 else ''
    return f"{indent}{left} {op} {right}"

def format_unaryop(formatter, name, properties, children_ids, indent_level, indent):
    op = properties.get('operator', '!')
    operand = formatter.format_node(children_ids[0], 0) if children_ids else ''
    return f"{indent}{op}{operand}"

def format_comparison(formatter, name, properties, children_ids, indent_level, indent):
    op = properties.get('operator', '===')
    left = formatter.format_node(children_ids[0], 0) if len(children_ids) > 0 else ''
    right = formatter.format_node(children_ids[1], 0) if len(children_ids) > 1 else ''
    return f"{indent}{left} {op} {right}"

def format_array(formatter, name, properties, children_ids, indent_level, indent):
    elements = [formatter.format_node(cid, 0).strip() for cid in children_ids]
    return f"{indent}[" + ", ".join(elements) + "]"

def format_dict(formatter, name, properties, children_ids, indent_level, indent):
    keys = properties.get('keys', [])
    pairs = []
    for i, cid in enumerate(children_ids):
        val = formatter.format_node(cid, 0).strip()
        k = f"'{keys[i]}'" if isinstance(keys[i], str) else str(keys[i])
        pairs.append(f"{k}: {val}")
    return f"{indent}{{{', '.join(pairs)}}}"

def format_member_access(formatter, name, properties, children_ids, indent_level, indent):
    obj = formatter.format_node(children_ids[0], 0).strip() if children_ids else "this"
    if obj == "self":
        obj = "this"
    member = properties.get('member', name)
    return f"{indent}{obj}.{member}"

def format_index_access(formatter, name, properties, children_ids, indent_level, indent):
    if len(children_ids) >= 2:
        arr = formatter.format_node(children_ids[0], 0).strip()
        if arr == "self":
            arr = "this"
        idx = formatter.format_node(children_ids[1], 0).strip()
        return f"{indent}{arr}[{idx}]"
    return f"{indent}{name}[0] // Error: IndexAccess missing children"

def format_throw(formatter, name, properties, children_ids, indent_level, indent):
    exc = formatter.format_node(children_ids[0], 0).strip().rstrip(';') if children_ids else name
    return f"{indent}throw {exc};"
EXT = "ts"
