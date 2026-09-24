# SyntyCode: Raw Tree-Sitter Architect Engine

SyntyCode is an advanced, language-agnostic software architecture engine built specifically for autonomous AI agents. It leverages the raw analytical power of the **Tree-Sitter** ontology inside an optimized SQLite Graph Database (`agy_nodeos.db`), providing models with unparalleled semantic search, relational architecture querying, and 100% loss-less transpilation across 50+ programming languages.

## 🚀 The Production-Grade Edge (v2.0)

1. **Zero-Translation Fidelity**
   SyntyCode caches the exact, pristine `raw_code` inside SQLite `FileNode` containers. When decoding the graph back to disk, the Engine mathematically guarantees zero translation loss or formatting destruction. AI format preservation is 100% perfect.
2. **Native Termux Binary Bypass**
   Relying on Python `pip` C-bindings to compile AST parsers in mobile/ARM64 environments frequently crashes (`dlopen` failures). SyntyCode bypasses this entirely by hooking into Termux's flawlessly pre-compiled, native `tree-sitter parse -x` CLI binaries for seamless XML extraction.
3. **The Ultimate Raw Ontology**
   SyntyCode does not abstract languages into generic nodes (like `ClassNode`). It embraces the true Tree-Sitter schema, dumping literal `class_definition`, `expression_statement`, and `binary_operator` dependencies straight into the relational graph.

## 📦 Dependencies

SyntyCode is engineered to run universally in restricted environments (like Android Termux).
- **Python 3.8+** (For the Decoder & CLI)
- **SQLite3** (For the Relational Graph DB)
- **Termux Tree-Sitter Core**: `pkg install tree-sitter tree-sitter-parsers`
- *Zero third-party `pip` C-compiler dependencies needed!*

## 🤖 The AI Read/Write Loop (Architect Schema)

AI Agents manipulate the codebase via the **Architect Schema JSON**. This provides a perfectly constrained sandbox for LLMs to safely alter architecture without directly breaking complex file systems.

### 1. Extract Context
Extract the physical database context into a clean JSON for the AI.
```bash
syntycode context MyProject > architecture.json
```

### 2. AI Mutates JSON (Example)
```json
{
  "module_name": "MyProject",
  "files": [
    {
      "file_name": "main",
      "language": "python",
      "code": "print('Hello Production-Grade SyntyCode!')"
    }
  ]
}
```

### 3. Ingest Logic (Tree-Sitter XML Mapping)
The engine reads the JSON, stores the pristine code string securely, and automatically queries the native Tree-Sitter CLI to extract and map every structural dependency (classes, logic, variables) natively into SQLite.
```bash
syntycode ingest-architect architecture.json
```

### 4. Decode the Codebase
Restore the modified database module back to the physical file system.
```bash
syntycode decode MyProject python -o ./src_output
```
