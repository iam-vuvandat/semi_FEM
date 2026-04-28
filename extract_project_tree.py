import os

def generate_tree(dir_path, prefix="", ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', '.vscode', '.idea', 'venv', '.venv', 'build', 'data', 'dist','Ansys_Projects'}
    
    try:
        items = sorted(os.listdir(dir_path))
    except PermissionError:
        return

    items = [item for item in items if item not in ignore_dirs]
    
    for i, item in enumerate(items):
        path = os.path.join(dir_path, item)
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        
        line = f"{prefix}{connector}{item}"
        print(line)
        with open("project_structure.txt", "a", encoding="utf-8") as f:
            f.write(line + "\n")
            
        if os.path.isdir(path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            generate_tree(path, new_prefix, ignore_dirs)

if __name__ == "__main__":
    root_dir = "."
    if os.path.exists("project_structure.txt"):
        os.remove("project_structure.txt")
        
    root_name = os.path.basename(os.path.abspath(root_dir))
    header = f"{root_name}/"
    print(header)
    with open("project_structure.txt", "a", encoding="utf-8") as f:
        f.write(header + "\n")
        
    generate_tree(root_dir)