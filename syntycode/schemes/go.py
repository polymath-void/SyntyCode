import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _helpers import (translate_self_ref, strip_self_from_inputs, translate_constructor_name,
                      translate_super_call, translate_loop, translate_variable_value)

LANG = "go"

def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"package {name.lower()}\n\n"
    code += "\n\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    raw_inputs = strip_self_from_inputs(properties.get("inputs", []))
    inputs = ", ".join([f"{inp} interface{{}}" for inp in raw_inputs])
    fn_name = translate_constructor_name(name, "__NEW__")
    
    code = f"{indent}func {fn_name}({inputs}) {{\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "s", ".")
    val_code = translate_variable_value(properties, children_ids, formatter, "nil")
    if clean_name.startswith("s."):
        return f"{indent}{clean_name} = {val_code}"
    return f"{indent}{clean_name} := {val_code}"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "s", ".")
    # Go has no super
    if "super()" in name:
        return f"{indent}// Go: no native super call"
    args = ", ".join(properties.get("args", []))
    return f"{indent}{clean_name}({args})"

def format_condition(formatter, name, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0)
        code += f"{indent}if {check_code} {{\n"
        code += formatter.format_node(children_ids[1], indent_level + 1) + "\n"
        code += f"{indent}}}"
        if len(children_ids) >= 3:
            code += f" else {{\n"
            code += formatter.format_node(children_ids[2], indent_level + 1) + "\n"
            code += f"{indent}}}"
    return code

def format_import(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}import \"{name}\""

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    
    # Go: struct + receiver methods (no classes)
    code = f"{indent}type {name} struct {{\n"
    if inherits:
        if isinstance(inherits, list):
            for b in inherits:
                code += f"{indent}    {b}  // embedded struct\n"
        else:
            code += f"{indent}    {inherits}  // embedded struct\n"
    code += f"{indent}}}\n"
    
    if children_ids:
        for cid in children_ids:
            rendered = formatter.format_node(cid, indent_level)
            # Convert func __NEW__ to func New<ClassName>
            rendered = rendered.replace("func __NEW__", f"func New{name}")
            # Convert regular funcs to receiver methods
            if "func New" not in rendered and rendered.strip().startswith("func "):
                fn_part = rendered.strip()[5:]  # strip "func "
                rendered = f"{indent}func (s *{name}) {fn_part}"
            code += "\n" + rendered
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
    # Go uses explicit error handling
    exc_var = properties.get("exception_var", "err") or "err"
    code = f"{indent}// Go: explicit error handling pattern\n"
    if len(children_ids) > 0:
        code += formatter.format_node(children_ids[0], indent_level) + "\n"
    code += f"{indent}if {exc_var} != nil {{\n"
    if len(children_ids) > 1:
        code += formatter.format_node(children_ids[1], indent_level + 1) + "\n"
    code += f"{indent}}}"
    return code

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}// empty block"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}{name}"

def format_return(formatter, name, properties, children_ids, indent_level, indent):
    if children_ids:
        val = formatter.format_node(children_ids[0], 0).strip().rstrip(';')
        return f"{indent}return {val}"
    return f"{indent}return"

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = name
    if clean_name == "True":
        clean_name = "true"
    elif clean_name == "False":
        clean_name = "false"
    return f"{indent}{clean_name}"
EXT = "go"
