---
name: syntycode-engine
description: Standard Operating Procedure for Zero-Syntax Graph Engineering via SyntyJSON. Instructs agents on how to construct complex software architectures by generating declarative AST JSON files.
version: 1.1.0
---

# SyntyCode Engine: Agent Operating Procedure

**Core Philosophy:** You are a Zero-Syntax Graph Engineer. You do NOT write `.py`, `.ts`, or `.rs` files directly. You define logic natively by creating a structured `SyntyJSON` file. The engine ingests this file into a relational SQLite graph and mathematically guarantees 100% flawless cross-language transpilation.

## 1. The SyntyJSON Workflow
Instead of writing tedious Python scripts or raw SQL transactions, you must author a declarative JSON file (e.g., `architecture.json`) representing the Abstract Syntax Tree (AST).

```json
{
  "module": "MyProject",
  "nodes": [
    {
      "node_type": "FileNode",
      "name": "main",
      "children": [
        {
          "node_type": "ClassNode",
          "name": "User",
          "children": [
            {
              "node_type": "Function",
              "name": "login",
              "properties": { "inputs": ["self"], "is_method": true },
              "children": [
                {
                  "node_type": "Call",
                  "name": "print",
                  "properties": { "args": ["Success"] }
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

## 2. Ingestion & Transpilation
Once the JSON file is generated, execute the following CLI commands:
```bash
# 1. Ingest the JSON into the SQLite graph
syntycode ingest architecture.json

# 2. Decode the graph into physical codebase files
syntycode decode MyProject python --out-dir src_py
syntycode decode MyProject typescript --out-dir src_ts
```

## 3. Node Vocabulary & Properties
Use the following `node_type` declarations carefully:
*   **Architecture Nodes:** `FileNode`, `ClassNode`, `Function`
    *   *Function Properties:* `{"inputs": ["arg1"], "is_method": true}`
*   **Logic Nodes:** `Condition`, `Loop`, `Block`, `Return`, `ThrowNode`
*   **Variable Nodes:** `Variable` (Left-hand side assignment)
*   **Expression Nodes:** `Call`, `BinaryOp`, `Identifier`
    *   *Call Properties:* `{"args": ["arg1"]}`
    *   *BinaryOp Properties:* `{"operator": "=="}`
*   **Data Structures:** `DictNode`, `ArrayNode`
    *   *DictNode Properties:* `{"keys": ["key1"]}`
*   **Access Nodes:** `MemberAccess`, `IndexAccess`
    *   *IndexAccess Safety:* Pass `{"safe": true}` to gracefully handle missing dictionary keys in strict languages (transpiles to `.get()`).

## Critical Anti-Patterns
❌ **NEVER** write code strings manually (e.g., do not write `def hello():` into the `name` field).
❌ **NEVER** attempt to write raw SQL to the database unless the JSON ingestor is unavailable.
❌ **NEVER** forget to nest nodes inside the `children` array to establish hierarchy.
