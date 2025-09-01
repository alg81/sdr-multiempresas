import os
import ast

CORE_DIR = "core"

def get_defined_functions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        node = ast.parse(f.read(), filename=file_path)
    return {n.name for n in ast.walk(node) if isinstance(n, ast.FunctionDef)}

def get_imported_functions(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        node = ast.parse(f.read(), filename=file_path)
    imports = []
    for n in ast.walk(node):
        if isinstance(n, ast.ImportFrom) and n.module and n.module.startswith("core"):
            for name in n.names:
                imports.append((n.module.replace("core.", ""), name.name, file_path))
    return imports

def validate_imports():
    errors = []
    core_files = {
        f.replace(".py", ""): os.path.join(CORE_DIR, f)
        for f in os.listdir(CORE_DIR) if f.endswith(".py")
    }

    all_defs = {
        module: get_defined_functions(path)
        for module, path in core_files.items()
    }

    for module, path in core_files.items():
        imports = get_imported_functions(path)
        for imported_module, func_name, file_origin in imports:
            if imported_module not in all_defs:
                errors.append(f"[IMPORT ERROR] Module 'core.{imported_module}' not found (imported in {file_origin})")
            elif func_name not in all_defs[imported_module]:
                errors.append(
                    f"[FUNCTION ERROR] Function '{func_name}' not found in 'core.{imported_module}' (imported in {file_origin})"
                )

    if errors:
        print("### INCONSISTÊNCIAS DETECTADAS ###\n")
        for e in errors:
            print(e)
    else:
        print("✅ Todos os imports estão consistentes!")

if __name__ == "__main__":
    validate_imports()
