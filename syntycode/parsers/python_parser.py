import ast
from ..sdk import Node

def py_ast_to_synty(node) -> Node:
    """Recursively maps Python ast nodes to SyntyCode Graph Nodes."""
    if isinstance(node, ast.ClassDef):
        synty_node = Node("ClassNode", node.name)
        for child in node.body:
            child_node = py_ast_to_synty(child)
            if child_node:
                synty_node.add_child(child_node)
        return synty_node
        
    elif isinstance(node, ast.FunctionDef):
        inputs = [a.arg for a in node.args.args]
        is_method = len(inputs) > 0 and inputs[0] == "self"
        synty_node = Node("Function", node.name, {"inputs": inputs, "is_method": is_method})
        for child in node.body:
            child_node = py_ast_to_synty(child)
            if child_node:
                synty_node.add_child(child_node)
        return synty_node

    elif isinstance(node, ast.Assign):
        if not node.targets:
            return None
        target = node.targets[0]
        name = ""
        if isinstance(target, ast.Name):
            name = target.id
        elif isinstance(target, ast.Attribute):
            if isinstance(target.value, ast.Name):
                name = f"{target.value.id}.{target.attr}"
        if not name:
            name = "unknown_var"
            
        synty_node = Node("Variable", name)
        # Attempt to parse value
        val_node = py_ast_to_synty(node.value)
        if val_node:
            synty_node.add_child(val_node)
        return synty_node
        
    elif isinstance(node, ast.Expr):
        return py_ast_to_synty(node.value)
        
    elif isinstance(node, ast.Call):
        func_name = "call"
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
                
        # args handling
        args_strs = []
        for a in node.args:
            if isinstance(a, ast.Constant):
                args_strs.append(repr(a.value))
            elif isinstance(a, ast.Name):
                args_strs.append(a.id)
        
        return Node("Call", func_name, {"args": args_strs})

    elif isinstance(node, ast.Dict):
        return Node("DictNode", "dict", {"keys": []})
        
    elif isinstance(node, ast.List):
        return Node("ArrayNode", "list")
        
    elif isinstance(node, ast.Pass):
        return Node("Call", "pass")

    return None

def parse_code(code: str) -> list:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    nodes = []
    for body_node in tree.body:
        synty = py_ast_to_synty(body_node)
        if synty:
            nodes.append(synty)
    return nodes
