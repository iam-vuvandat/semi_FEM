import sys
from pathlib import Path

def configure_path(marker_file='.project_root', levels_up=10000):
    # 1. Ưu tiên logic đóng gói (App)
    if getattr(sys, 'frozen', False):
        if hasattr(sys, '_MEIPASS'):
            root_path = Path(sys._MEIPASS).resolve()
        else:
            root_path = Path(sys.executable).parent.resolve()
        
        root_str = str(root_path)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        return root_path

    # 2. Logic cho môi trường phát triển (VS Code/Terminal)
    # Tìm file marker (.project_root) bằng cách quét ngược lên từ chính vị trí tệp paths.py này
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
        return root_path 
    else:
        # Nếu không thấy marker, coi thư mục hiện tại của tệp này là root tạm thời
        return current_path

path = configure_path()