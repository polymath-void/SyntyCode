import json
from .parsers.ts_cli_bridge import parse_code_via_cli
from .parsers.xml_parser import parse_sexpr_to_graph
from .sdk import GraphContext, Node

def ingest_architect_json(filepath: str):
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    module_name = data["module_name"]
    
    with GraphContext(module_name) as ctx:
        for file_data in data.get("files", []):
            # Store the pristine, user/AI-edited raw code directly on the file node!
            file_node = Node("FileNode", file_data["file_name"], {"raw_code": file_data["code"]})
            
            lang = file_data.get("language", "python").lower()
            try:
                xml_output = parse_code_via_cli(file_data["code"], lang)
                parsed_nodes = parse_sexpr_to_graph(xml_output)
                
                for p_node in parsed_nodes:
                    file_node.add_child(p_node)
            except Exception as e:
                print(f"Fallback due to parser error: {e}")
                file_node.add_child(Node("TextNode", "RawCode", {"code": file_data["code"]}))
                    
            ctx.add_node(file_node)
            
    return module_name
