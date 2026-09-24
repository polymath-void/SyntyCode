import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _helpers import (translate_self_ref, strip_self_from_inputs, translate_constructor_name,
                      translate_super_call, translate_loop, translate_variable_value)

LANG = "rust"

def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"pub mod {name.lower()} {{\n"
    code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += "}"
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    raw_inputs = strip_self_from_inputs(properties.get("inputs", []))
    fn_name = translate_constructor_name(name, "new")
    
    if fn_name == "new":
        inputs = ", ".join([f"{inp}: &str" for inp in raw_inputs])
        code = f"{indent}pub fn new({inputs}) -> Self {{\n"
    else:
        all_inputs = ["&self"] + [f"{inp}: &str" for inp in raw_inputs]
        code = f"{indent}pub fn {fn_name}({', '.join(all_inputs)}) {{\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "self", ".")
    val_code = translate_variable_value(properties, children_ids, formatter, "None")
    if clean_name.startswith("self."):
        return f"{indent}{clean_name} = {val_code};"
    return f"{indent}let {clean_name} = {val_code};"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = translate_self_ref(name, "self", ".")
    # Rust has no super() — comment it out
    if "super()" in name:
        return f"{indent}// Rust: no native super call"
    args = ", ".join(properties.get("args", []))
    return f"{indent}{clean_name}({args});"

def format_condition(formatter, name, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0).rstrip(';')
        code += f"{indent}if {check_code} {{\n"
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
        return f"{indent}use {name}::{{{', '.join(names)}}};"
    return f"{indent}use {name};"

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    
    # Rust: struct + impl block (no inheritance, use traits)
    code = f"{indent}pub struct {name} {{\n"
    code += f"{indent}    // fields\n"
    code += f"{indent}}}\n\n"
    
    if inherits:
        code += f"{indent}// Implements trait from: {inherits}\n"
    
    code += f"{indent}impl {name} {{\n"
    if children_ids:
        code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}}}"
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
    # Rust uses Result<T, E> pattern, not try/catch
    code = f"{indent}// Rust: using Result<T, E> pattern\n"
    code += f"{indent}match (|| -> Result<(), Box<dyn std::error::Error>> {{\n"
    if len(children_ids) > 0:
        code += formatter.format_node(children_ids[0], indent_level + 1) + "\n"
    code += f"{indent}    Ok(())\n"
    code += f"{indent}}})() {{\n"
    code += f"{indent}    Ok(_) => {{}},\n"
    exc_var = properties.get("exception_var", "e") or "e"
    code += f"{indent}    Err({exc_var}) => {{\n"
    if len(children_ids) > 1:
        code += formatter.format_node(children_ids[1], indent_level + 2) + "\n"
    code += f"{indent}    }}\n"
    code += f"{indent}}}"
    return code

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}// empty block"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    clean_name = name
    if clean_name == "True":
        clean_name = "true"
    elif clean_name == "False":
        clean_name = "false"
    return f"{indent}{clean_name}"

def format_return(formatter, name, properties, children_ids, indent_level, indent):
    if children_ids:
        val = formatter.format_node(children_ids[0], 0).strip().rstrip(';')
        return f"{indent}return {val};"
    return f"{indent}return;"

def format_binaryop(formatter, name, properties, children_ids, indent_level, indent):
    if len(children_ids) >= 2:
        left = formatter.format_node(children_ids[0], 0).strip().rstrip(';')
        right = formatter.format_node(children_ids[1], 0).strip().rstrip(';')
        op = properties.get("operator", "+")
        return f"{indent}{left} {op} {right}"
    return f"{indent}// BinaryOp missing children"

def format_array(formatter, name, properties, children_ids, indent_level, indent):
    elements = [formatter.format_node(cid, 0).strip() for cid in children_ids]
    return f"{indent}vec![" + ", ".join(elements) + "]"

def format_dict(formatter, name, properties, children_ids, indent_level, indent):
    keys = properties.get('keys', [])
    pairs = []
    for i, cid in enumerate(children_ids):
        val = formatter.format_node(cid, 0).strip()
        k = f'"{keys[i]}"' if isinstance(keys[i], str) else str(keys[i])
        pairs.append(f"({k}, {val})")
    return f"{indent}HashMap::from([" + ", ".join(pairs) + "])"

def format_throw(formatter, name, properties, children_ids, indent_level, indent):
    exc = formatter.format_node(children_ids[0], 0).strip().rstrip(';') if children_ids else name
    return f"{indent}panic!({exc});"

def format_member_access(formatter, name, properties, children_ids, indent_level, indent):
    obj = formatter.format_node(children_ids[0], 0).strip() if children_ids else "self"
    member = properties.get('member', name)
    return f"{indent}{obj}.{member}"

def format_index_access(formatter, name, properties, children_ids, indent_level, indent):
    if len(children_ids) >= 2:
        arr = formatter.format_node(children_ids[0], 0).strip()
        idx = formatter.format_node(children_ids[1], 0).strip()
        return f"{indent}{arr}[{idx}]"
    return f"{indent}{name}[0]"
EXT = "rs"
