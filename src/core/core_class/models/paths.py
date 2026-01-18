import sys
from pathlib import Path

def configure_path(marker_file='.project_root', levels_up=10000):
    current_path = Path(__file__).resolve().parent
    root_path = None
    scan_path = current_path

    for _ in range(levels_up):
        if (scan_path / marker_file).exists():
            root_path = scan_path
            break
        if scan_path.parent == scan_path:
            break
        scan_path = scan_path.parent

    if root_path:
        root_str = str(root_path)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
    else:
        print(f"Warning: '{marker_file}' not found.")

    return root_path

configure_path()