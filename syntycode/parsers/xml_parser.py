import xml.etree.ElementTree as ET
from ..sdk import Node

def xml_to_node(element) -> Node:
    """Recursively converts a Tree-Sitter XML element to a SyntyCode Node."""
    node_type = element.tag
    name = "unknown"
    
    for child in element:
        if child.attrib.get("field") == "name":
            name = child.text
            break
            
    if node_type == "identifier":
        name = element.text
        
    # Heuristic for missing names (like import_statement)
    if not name or name.strip() == "" or name == "unknown":
        extracted = []
        for child in element:
            if child.tag in ("identifier", "dotted_name") and child.text:
                extracted.append(child.text.strip())
        if extracted:
            name = ".".join(extracted)
        
    synty_node = Node(node_type, name.strip() if name else "unknown")
    synty_node.properties = element.attrib
        
    for child in element:
        synty_node.add_child(xml_to_node(child))
        
    return synty_node

def parse_sexpr_to_graph(xml_string: str) -> list:
    try:
        root = ET.fromstring(xml_string)
        module_node = root.find(".//module")
        if module_node is None:
            module_node = root.find(".//program")
            if module_node is None:
                source = root.find(".//source")
                module_node = list(source)[0] if source is not None and len(source) > 0 else None
                
        if module_node is not None:
            return [xml_to_node(child) for child in module_node]
            
        return []
    except Exception as e:
        import traceback
        traceback.print_exc()
        return [Node("TextNode", "RawCode", {"error": str(e)})]
