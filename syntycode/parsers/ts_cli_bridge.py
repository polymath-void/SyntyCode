import subprocess
import shutil
import tempfile
import os

def parse_code_via_cli(code_string: str, lang: str) -> str:
    """Uses the native Termux `tree-sitter` binary to parse code into XML."""
    if not shutil.which("tree-sitter"):
        raise EnvironmentError("Native 'tree-sitter' CLI not installed. Run: pkg install tree-sitter")
        
    lib_path = f"/data/data/com.termux/files/usr/lib/libtree-sitter-{lang}.so"
    if not os.path.exists(lib_path):
        raise FileNotFoundError(f"Language library {lib_path} not found. Run: pkg install tree-sitter-{lang}")
        
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
