"""
Scheme Helpers: Shared utility functions for language scheme formatters.
These handle the translation of Python-isms stored in the AST graph
into language-native equivalents.
"""

def translate_self_ref(name, keyword="this", separator="."):
    """Translate self.X to the native instance reference."""
    if name.startswith("self."):
        return f"{keyword}{separator}{name[5:]}"
    return name

def strip_self_from_inputs(inputs):
    """Remove 'self' from the inputs list (for non-Python OOP languages)."""
    return [inp for inp in inputs if inp != "self"]

def translate_constructor_name(name, target_name="constructor"):
    """Translate __init__ to the target language constructor name."""
    if name == "__init__":
        return target_name
    return name

def translate_super_call(name, replacement="super()"):
    """Translate super().__init__() to the native super call."""
    if name == "super().__init__" or name == "super().__init__()":
        return replacement
    if name.startswith("super()."):
        method = name[8:]
        return f"super.{method}"
    return name

def translate_loop(name, condition, lang="typescript"):
    """Parse loop condition and return native loop header."""
    parts = condition.split(" in ", 1) if " in " in condition else None
    
    if name == "for" and parts and len(parts) == 2:
        iterator, iterable = parts[0].strip(), parts[1].strip()
        
        if lang == "typescript" or lang == "javascript":
            return f"for (const {iterator} of {iterable})"
        elif lang == "java":
            return f"for (Object {iterator} : {iterable})"
        elif lang == "csharp":
            return f"foreach (var {iterator} in {iterable})"
        elif lang == "cpp":
            return f"for (auto {iterator} : {iterable})"
        elif lang == "kotlin":
            return f"for ({iterator} in {iterable})"
        elif lang == "swift":
            return f"for {iterator} in {iterable}"
        elif lang == "dart":
            return f"for (var {iterator} in {iterable})"
        elif lang == "rust":
            return f"for {iterator} in {iterable}"
        elif lang == "go":
            return f"for _, {iterator} := range {iterable}"
        elif lang == "ruby":
            return f"{iterable}.each do |{iterator}|"
        elif lang == "php":
            return f"foreach (${iterable} as ${iterator})"
        elif lang == "lua":
            return f"for _, {iterator} in ipairs({iterable}) do"
    
    # Fallback: while-style
    return f"while ({condition})" if lang not in ("ruby", "lua", "python") else f"while {condition}"

def translate_args(args, old_self="self", new_self="this", separator="."):
    """Replaces self. with the language specific prefix in arguments"""
    if not args:
        return []
    res = []
    for a in args:
        if a.startswith(f"{old_self}."):
            prefix_len = len(old_self) + 1
            res.append(f"{new_self}{separator}{a[prefix_len:]}")
        else:
            res.append(a)
    return res

def translate_variable_value(properties, children_ids, formatter, null_keyword="null"):
    """Get the formatted value for a variable assignment."""
    if "raw_value" in properties and properties["raw_value"] is not None:
        raw = properties["raw_value"]
        if isinstance(raw, bool):
            return "true" if raw else "false"
        elif isinstance(raw, str):
            return repr(raw)
        elif isinstance(raw, dict):
            # Language-specific dict formatting would go here
            # For now, use JSON-like representation
            pairs = ", ".join([f'"{k}": "{v}"' if isinstance(v, str) else f'"{k}": {v}' for k, v in raw.items()])
            return "{" + pairs + "}"
        elif isinstance(raw, list):
            return "[" + ", ".join([repr(x) if isinstance(x, str) else str(x) for x in raw]) + "]"
        return str(raw)
    elif children_ids:
        return formatter.format_node(children_ids[0], 0)
    return null_keyword
