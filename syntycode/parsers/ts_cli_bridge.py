import subprocess
import shutil
import tempfile
import os
import platform

def find_library_path(lang: str) -> str:
    system = platform.system()
    lib_name = f"libtree-sitter-{lang}.so"
    if system == "Darwin":
        lib_name = f"libtree-sitter-{lang}.dylib"
    elif system == "Windows":
        lib_name = f"tree-sitter-{lang}.dll"
        
    search_dirs = [
        os.environ.get("TREE_SITTER_LIB_DIR"),
        "/data/data/com.termux/files/usr/lib",
        "/usr/lib",
        "/usr/local/lib",
        "/opt/homebrew/lib",
        "/usr/lib/x86_64-linux-gnu",
        "/usr/lib/aarch64-linux-gnu"
    ]
    
    for d in search_dirs:
        if d and os.path.exists(os.path.join(d, lib_name)):
            return os.path.join(d, lib_name)
            
    # Fallback for Mac where it might be compiled as .so anyway
    if system == "Darwin":
        for d in search_dirs:
            if d and os.path.exists(os.path.join(d, f"libtree-sitter-{lang}.so")):
                return os.path.join(d, f"libtree-sitter-{lang}.so")
                
    return None

def parse_code_via_cli(code_string: str, lang: str) -> str:
    """Uses the native Tree-sitter binary to parse code into XML."""
    if not shutil.which("tree-sitter"):
        raise EnvironmentError("Native 'tree-sitter' CLI not installed in PATH.")
        
    lib_path = find_library_path(lang)
    
    if not lib_path:
        raise FileNotFoundError(
            f"Language library for '{lang}' not found in standard directories.\n"
            f"Please ensure it is installed or set TREE_SITTER_LIB_DIR environment variable."
        )
        
    # Write temp file for the CLI
    fd, tmp_file = tempfile.mkstemp(suffix=f".{lang}")
    with os.fdopen(fd, 'w') as f:
        f.write(code_string)
        
    try:
        # Execute raw parse and output as XML
        result = subprocess.run(
            ["tree-sitter", "parse", "-l", lib_path, "--lang-name", lang, "-x", tmp_file], 
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Tree-sitter parse failed: {result.stderr}")
            
        return result.stdout
    finally:
        os.remove(tmp_file)
