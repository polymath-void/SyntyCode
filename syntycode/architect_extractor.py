import json
from .decoder import DynamicFormatter, load_schemes

def extract_architect_context(module_name: str, target_lang: str = "python") -> str:
    schemes = load_schemes()
    if target_lang not in schemes:
        raise ValueError(f"Scheme for {target_lang} not found.")
        
    formatter = DynamicFormatter(schemes[target_lang])
    
    formatter.cursor.execute("""
        SELECT m.module_id, n.node_id 
        FROM ast_nodes n
        JOIN modules m ON n.module_id = m.module_id
        WHERE n.node_type = 'Module' AND n.name = ?
        ORDER BY m.last_updated DESC LIMIT 1
    """, (module_name,))
    
    row = formatter.cursor.fetchone()
    if not row:
        return json.dumps({"error": f"Module '{module_name}' not found."})
        
    module_db_id = row[0]
    module_node_id = row[1]
    formatter.preload_module(module_db_id)
    
    children = formatter.get_children(module_node_id)
    file_nodes = [cid for cid in children if formatter.get_node(cid)[0] == 'FileNode']
    
    architect_schema = {
        "module_name": module_name,
        "files": []
    }
    
    if file_nodes:
        for file_id in file_nodes:
            _, file_name, _ = formatter.get_node(file_id)
            file_content = formatter.format_node(file_id, 0)
            
            architect_schema["files"].append({
                "file_name": file_name,
                "language": target_lang,
                "code": file_content
            })
    else:
        # Monolith without FileNodes
        file_content = formatter.format_node(module_node_id, 0)
        architect_schema["files"].append({
            "file_name": module_name.lower(),
            "language": target_lang,
            "code": file_content
        })
        
    return json.dumps(architect_schema, indent=2)
