def format_module(formatter, name, children_ids, indent_level, indent):
    return "\n\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    inputs = properties.get("inputs", [])
    
    # Handle normalized semantics
    if properties.get("is_method"):
        if "self" not in inputs:
            inputs.insert(0, "self")
            
    fn_name = "__init__" if properties.get("is_constructor") else name
    
    inputs_str = ", ".join(inputs)
    code = f"{indent}def {fn_name}({inputs_str}):\n"
    if not children_ids:
        code += f"{indent}    pass"
    else:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids])
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    var_name = name
    # Handle normalized semantics
    if properties.get("scope") == "instance":
        var_name = f"self.{properties.get('field_name', name)}"
        
    if "raw_value" in properties and properties["raw_value"] is not None:
        val_code = repr(properties["raw_value"])
    elif "raw_value" in properties and properties["raw_value"] is None and not children_ids:
        val_code = "None"
    else:
        val_code = formatter.format_node(children_ids[0], 0) if children_ids else "None"
        
    return f"{indent}{var_name} = {val_code}"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    call_name = name
    
    # Handle normalized semantics
    if properties.get("call_type") == "super_call":
        call_name = "super().__init__"
    elif properties.get("call_type") == "instance_method":
        call_name = f"self.{properties.get('method_name', name)}"
        
    args = ", ".join(properties.get("args", []))
    return f"{indent}{call_name}({args})"

def format_condition(formatter, name, properties, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0)
        code += f"{indent}if {check_code}:\n"
        code += formatter.format_node(children_ids[1], indent_level + 1)
        if len(children_ids) >= 3:
            code += f"\n{indent}else:\n"
            code += formatter.format_node(children_ids[2], indent_level + 1)
    return code

def format_import(formatter, name, properties, children_ids, indent_level, indent):
    names = properties.get("names", [])
    if names:
        return f"{indent}from {name} import {', '.join(names)}"
    return f"{indent}import {name}"

def format_class(formatter, name, properties, children_ids, indent_level, indent):
    inherits = properties.get("inherits")
    if isinstance(inherits, list):
        base = f"({', '.join(inherits)})"
    elif inherits:
        base = f"({inherits})"
    else:
        base = ""
        
    code = f"{indent}class {name}{base}:\n"
    if not children_ids:
        code += f"{indent}    pass"
    else:
        code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids])
    return code

def format_loop(formatter, name, properties, children_ids, indent_level, indent):
    # Handle normalized semantics
    if "iterator" in properties and "iterable" in properties:
        condition_code = f"{properties['iterator']} in {properties['iterable']}"
        code = f"{indent}for {condition_code}:\n"
    else:
        condition = properties.get("condition", "")
        code = f"{indent}{name} {condition}:\n"
        
    if not children_ids:
        code += f"{indent}    pass"
    else:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids])
    return code

def format_trycatch(formatter, name, properties, children_ids, indent_level, indent):
    exc_type = properties.get("exception_type", "Exception")
    if isinstance(exc_type, list):
        exc_type = f"({', '.join(exc_type)})"
        
    exc_var = properties.get("exception_var")
    
    code = f"{indent}try:\n"
    if len(children_ids) > 0:
        code += formatter.format_node(children_ids[0], indent_level + 1)
    else:
        code += f"{indent}    pass\n"
        
    if exc_var:
        code += f"\n{indent}except {exc_type} as {exc_var}:\n"
    else:
        code += f"\n{indent}except {exc_type}:\n"
    
    if len(children_ids) > 1:
        code += formatter.format_node(children_ids[1], indent_level + 1)
    else:
        code += f"{indent}    pass"
        
    return code

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}pass"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}{name}"

# --- NEW NODE TYPES ---

def format_return(formatter, name, properties, children_ids, indent_level, indent):
    if children_ids:
        val = formatter.format_node(children_ids[0], 0)
        return f"{indent}return {val}"
    return f"{indent}return"

def format_binaryop(formatter, name, properties, children_ids, indent_level, indent):
    op = properties.get('operator', '+')
    left = formatter.format_node(children_ids[0], 0) if len(children_ids) > 0 else ''
    right = formatter.format_node(children_ids[1], 0) if len(children_ids) > 1 else ''
    return f"{indent}{left} {op} {right}"

def format_unaryop(formatter, name, properties, children_ids, indent_level, indent):
    op = properties.get('operator', 'not')
    operand = formatter.format_node(children_ids[0], 0) if children_ids else ''
    return f"{indent}{op} {operand}"

def format_comparison(formatter, name, properties, children_ids, indent_level, indent):
    op = properties.get('operator', '==')
    left = formatter.format_node(children_ids[0], 0) if len(children_ids) > 0 else ''
    right = formatter.format_node(children_ids[1], 0) if len(children_ids) > 1 else ''
    return f"{indent}{left} {op} {right}"

def format_enum(formatter, name, properties, children_ids, indent_level, indent):
    members = properties.get('members', [])
    code = f"{indent}class {name}(Enum):\n"
    if members:
        for i, m in enumerate(members):
            code += f"{indent}    {m} = {i}\n"
    else:
        code += f"{indent}    pass\n"
    return code.rstrip('\n')

def format_interface(formatter, name, properties, children_ids, indent_level, indent):
    code = f"{indent}class {name}(ABC):\n"
    if children_ids:
        code += "\n\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids])
    else:
        code += f"{indent}    pass"
    return code

def format_decorator(formatter, name, properties, children_ids, indent_level, indent):
    args = properties.get('args', [])
    if args:
        return f"{indent}@{name}({', '.join(args)})"
    return f"{indent}@{name}"

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
    obj = formatter.format_node(children_ids[0], 0).strip() if children_ids else "self"
    member = properties.get('member', name)
    return f"{indent}{obj}.{member}"

def format_index_access(formatter, name, properties, children_ids, indent_level, indent):
    if len(children_ids) >= 2:
        arr = formatter.format_node(children_ids[0], 0).strip()
        idx = formatter.format_node(children_ids[1], 0).strip()
        if properties.get("safe", False):
            return f"{indent}{arr}.get({idx})"
        return f"{indent}{arr}[{idx}]"
    return f"{indent}{name}[0] # Error: IndexAccess missing children"

def format_throw(formatter, name, properties, children_ids, indent_level, indent):
    exc = formatter.format_node(children_ids[0], 0).strip() if children_ids else name
    return f"{indent}raise {exc}"
EXT = "py"
CONFIG = {"comment_prefix": "#"}
