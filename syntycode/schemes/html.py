def format_module(formatter, name, children_ids, indent_level, indent):
    code = f"<!-- Module: {name} -->\n<html>\n<body>\n"
    code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids])
    code += "\n</body>\n</html>"
    return code

def format_function(formatter, name, properties, children_ids, indent_level, indent):
    code = f"{indent}<div id=\"{name}\" class=\"function-block\">\n"
    if children_ids:
        code += "\n".join([formatter.format_node(cid, indent_level + 1) for cid in children_ids]) + "\n"
    code += f"{indent}</div>"
    return code

def format_variable(formatter, name, properties, children_ids, indent_level, indent):
    val_code = formatter.format_node(children_ids[0], 0) if children_ids else ""
    return f"{indent}<span class=\"variable\" data-name=\"{name}\">{val_code}</span>"

def format_call(formatter, name, properties, children_ids, indent_level, indent):
    args = ", ".join(properties.get("args", []))
    return f"{indent}<button onclick=\"{name}({args})\">Call {name}</button>"

def format_condition(formatter, name, children_ids, indent_level, indent):
    code = ""
    if len(children_ids) >= 2:
        check_code = formatter.format_node(children_ids[0], 0)
        code += f"{indent}<div class=\"condition-block\">\n"
        code += f"{indent}    <div class=\"check\">If: {check_code}</div>\n"
        code += f"{indent}    <div class=\"true-branch\">\n"
        code += formatter.format_node(children_ids[1], indent_level + 2) + "\n"
        code += f"{indent}    </div>\n"
        if len(children_ids) >= 3:
            code += f"{indent}    <div class=\"false-branch\">\n"
            code += formatter.format_node(children_ids[2], indent_level + 2) + "\n"
            code += f"{indent}    </div>\n"
        code += f"{indent}</div>"
    return code


def format_import(formatter, name, properties, children_ids, indent_level, indent):
    return f"{indent}<!-- import {name} -->"

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

EXT = "html"
CONFIG = {"comment_prefix": "<!--"}
