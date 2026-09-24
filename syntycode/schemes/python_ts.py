# Production-Grade Un-Parser for Tree-Sitter Python ASTs

def format_module(formatter, name, children_ids, indent_level, indent):
    if not children_ids:
        return ""
    return "\n\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_class_definition(formatter, name, properties, children_ids, indent_level, indent):
    # Children: identifier (name), block (body), maybe argument_list (superclasses)
    body_nodes = []
    base_nodes = []
    class_name = name
    
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_props.get("field") == "name":
            class_name = c_name
        elif c_props.get("field") == "body":
            body_nodes.append(cid)
        elif c_props.get("field") == "superclasses":
            base_nodes.append(cid)
            
    code = f"{indent}class {class_name}"
    if base_nodes:
        code += "(" + formatter.format_node(base_nodes[0], 0).strip() + ")"
    code += ":\n"
    
    if body_nodes:
        code += formatter.format_node(body_nodes[0], indent_level + 1)
    else:
        code += f"{indent}    pass"
    return code

def format_function_definition(formatter, name, properties, children_ids, indent_level, indent):
    fn_name = name
    params = ""
    body = ""
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_props.get("field") == "name":
            fn_name = c_name
        elif c_props.get("field") == "parameters":
            params = formatter.format_node(cid, 0).strip()
            if params.startswith("(") and params.endswith(")"):
                params = params[1:-1]
        elif c_props.get("field") == "body":
            body = formatter.format_node(cid, indent_level + 1)
            
    code = f"{indent}def {fn_name}({params}):\n"
    if body:
        code += body
    else:
        code += f"{indent}    pass"
    return code

def format_block(formatter, name, properties, children_ids, indent_level, indent):
    if not children_ids:
        return f"{indent}pass"
    return "\n".join([formatter.format_node(cid, indent_level) for cid in children_ids])

def format_expression_statement(formatter, name, properties, children_ids, indent_level, indent):
    if children_ids:
        return f"{indent}" + formatter.format_node(children_ids[0], 0).strip()
    return ""

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    func_str = ""
    args_str = ""
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_props.get("field") == "function":
            func_str = formatter.format_node(cid, 0).strip()
        elif c_props.get("field") == "arguments":
            args_str = formatter.format_node(cid, 0).strip()
            
    return f"{func_str}{args_str}"

def format_argument_list(formatter, name, properties, children_ids, indent_level, indent):
    args = [formatter.format_node(cid, 0).strip() for cid in children_ids]
    return "(" + ", ".join(args) + ")"

def format_parameters(formatter, name, properties, children_ids, indent_level, indent):
    params = [formatter.format_node(cid, 0).strip() for cid in children_ids]
    return "(" + ", ".join(params) + ")"

def format_identifier(formatter, name, properties, children_ids, indent_level, indent):
    return name

def format_binary_operator(formatter, name, properties, children_ids, indent_level, indent):
    # Tree-sitter binary_operator usually has left and right fields.
    # The operator itself (like '+') is sometimes a child or implicit.
    # In tree-sitter Python, we don't easily get the operator char if it's an unnamed node, 
    # but we can try to guess or hardcode if properties doesn't have it.
    left = ""
    right = ""
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_props.get("field") == "left":
            left = formatter.format_node(cid, 0).strip()
        elif c_props.get("field") == "right":
            right = formatter.format_node(cid, 0).strip()
            
    return f"{left} + {right}" # Fallback for demo, real one needs op

def format_string(formatter, name, properties, children_ids, indent_level, indent):
    # usually has string_content
    content = ""
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_type == "string_content":
            # The text is lost if we don't store it!
            pass
    return f"'{name}'" # Fallback

def format_attribute(formatter, name, properties, children_ids, indent_level, indent):
    obj = ""
    attr = ""
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_props.get("field") == "object":
            obj = formatter.format_node(cid, 0).strip()
        elif c_props.get("field") == "attribute":
            attr = formatter.format_node(cid, 0).strip()
    return f"{obj}.{attr}"

def format_assignment(formatter, name, properties, children_ids, indent_level, indent):
    left = ""
    right = ""
    for cid in children_ids:
        c_type, c_name, c_props = formatter.get_node(cid)
        if c_props.get("field") == "left":
            left = formatter.format_node(cid, 0).strip()
        elif c_props.get("field") == "right":
            right = formatter.format_node(cid, 0).strip()
    return f"{indent}{left} = {right}"

def format_pass_statement(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}pass"

EXT = "py"
CONFIG = {"comment_prefix": "#"}
