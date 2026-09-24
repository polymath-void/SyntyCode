from ..sdk import Node

def ts_node_to_synty(ts_node, source_code: bytes) -> Node:
    """Recursively maps tree-sitter nodes to SyntyCode Graph Nodes."""
    node_type = ts_node.type
    
    if node_type == 'class_declaration' or node_type == 'class_definition':
        name_node = ts_node.child_by_field_name('name')
        name = name_node.text.decode('utf-8') if name_node else "unknown_class"
        synty_node = Node("ClassNode", name)
        
        body = ts_node.child_by_field_name('body')
        if body:
            for child in body.children:
                child_synty = ts_node_to_synty(child, source_code)
                if child_synty:
                    synty_node.add_child(child_synty)
        return synty_node
        
    elif node_type in ('function_definition', 'method_declaration', 'arrow_function', 'function_declaration'):
        name_node = ts_node.child_by_field_name('name')
        name = name_node.text.decode('utf-8') if name_node else "anonymous_func"
        
        synty_node = Node("Function", name)
        
        body = ts_node.child_by_field_name('body')
        if body:
            for child in body.children:
                child_synty = ts_node_to_synty(child, source_code)
                if child_synty:
                    synty_node.add_child(child_synty)
        return synty_node
        
    elif node_type in ('assignment', 'variable_declarator', 'assignment_expression', 'variable_declaration'):
        name_node = ts_node.child_by_field_name('left') or ts_node.child_by_field_name('name')
        name = name_node.text.decode('utf-8') if name_node else "unknown_var"
        synty_node = Node("Variable", name)
        
        value_node = ts_node.child_by_field_name('right') or ts_node.child_by_field_name('value')
        if value_node:
            val_synty = ts_node_to_synty(value_node, source_code)
            if val_synty:
                synty_node.add_child(val_synty)
        return synty_node
        
    elif node_type == 'call_expression':
        func_node = ts_node.child_by_field_name('function')
        func_name = func_node.text.decode('utf-8') if func_node else "call"
        return Node("Call", func_name)
        
    elif node_type == 'expression_statement':
        if len(ts_node.children) > 0:
            return ts_node_to_synty(ts_node.children[0], source_code)
            
    return None

def parse_code_universal(code: str, language: str) -> list:
    try:
        from tree_sitter import Language, Parser
        import importlib
        
        lang_module_name = f"tree_sitter_{language}"
        lang_module = importlib.import_module(lang_module_name)
        
        # New style for tree-sitter python bindings
        lang = Language(lang_module.language())
        parser = Parser(lang)
        
        source_bytes = code.encode('utf-8')
        tree = parser.parse(source_bytes)
        
        nodes = []
        for child in tree.root_node.children:
            synty = ts_node_to_synty(child, source_bytes)
            if synty:
                nodes.append(synty)
        return nodes
    except Exception as e:
        import traceback; traceback.print_exc()
        return [Node("TextNode", "RawCode", {"code": code})]
