-- SyntyCode Native Database Schema (schema.sql)
-- Allows direct ingestion of code via raw SQL, eliminating JSON and Python SDK intermediaries.

PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

-- Drop legacy tables
DROP TABLE IF EXISTS edges;
DROP TABLE IF EXISTS nodes;

-- 1. Modules / Files
CREATE TABLE IF NOT EXISTS modules (
    module_id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT NOT NULL UNIQUE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. AST Nodes
-- Uses INTEGER PRIMARY KEY for ultra-fast B-Tree clustering and native AI integer binding.
CREATE TABLE IF NOT EXISTS ast_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_id INTEGER NOT NULL REFERENCES modules(module_id) ON DELETE CASCADE,
    node_type TEXT NOT NULL,         
    name TEXT NOT NULL,              
    scope_path TEXT,                 
    properties TEXT DEFAULT '{}'     -- JSON dictionary of node-specific attributes
);

-- 3. AST Edges
-- Sequence Index allows deterministic ordering (e.g. args in Call, statements in Block).
CREATE TABLE IF NOT EXISTS ast_edges (
    source_id INTEGER NOT NULL REFERENCES ast_nodes(node_id) ON DELETE CASCADE,
    target_id INTEGER NOT NULL REFERENCES ast_nodes(node_id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,     
    sequence_index INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (source_id, target_id, relation_type, sequence_index)
);

-- Fast Traversal Indexes
CREATE INDEX IF NOT EXISTS idx_ast_nodes_lookup ON ast_nodes(module_id, scope_path);
CREATE INDEX IF NOT EXISTS idx_ast_edges_traversal ON ast_edges(source_id, relation_type, sequence_index);
CREATE INDEX IF NOT EXISTS idx_ast_edges_reverse ON ast_edges(target_id, relation_type);
