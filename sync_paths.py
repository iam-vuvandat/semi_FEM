import os
import shutil
from pathlib import Path

def sync_paths():
    root_dir = Path(__file__).parent.resolve()
    source_file = root_dir / "paths.py"

    if not source_file.exists():
        print(f"Error: {source_file} not found at root.")
        return

    exclude_dirs = {'.git', '__pycache__', '.venv', '.idea', '.vscode', 'build', 'dist'}

    for item in root_dir.rglob('*'):
        if item.is_dir():
            if any(part.startswith('.') or part in exclude_dirs for part in item.parts):
                continue
            
            target_file = item / "paths.py"
            
            if item != root_dir:
                # Logic xóa tệp cũ nếu tồn tại
                if target_file.exists():
                    try:
                        os.remove(target_file)
                        print(f"Removed old: {target_file}")
                    except Exception as e:
                        print(f"Failed to delete {target_file}: {e}")
                
                # Sao chép tệp mới từ gốc
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"Synced: {target_file}")
                except Exception as e:
                    print(f"Failed to copy to {target_file}: {e}")

if __name__ == "__main__":
    sync_paths()