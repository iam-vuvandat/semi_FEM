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
        if scan_path.parent == scan_path: # Chạm đến ổ đĩa gốc (C:\ hoặc /)
            break
        scan_path = scan_path.parent

    if root_path:
        root_str = str(root_path)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        return root_path # Trả về đối tượng Path để dùng cho việc lưu file
    else:
        # Nếu không tìm thấy, mặc định trả về folder chứa file đang chạy làm fallback
        print(f"⚠️ Không tìm thấy '{marker_file}'! Sử dụng thư mục hiện hành.")
        return current_path

path = configure_path()