import pickle
import sys
import logging
from pathlib import Path
import paths # Đảm bảo file paths.py định nghĩa đúng thư mục gốc dự án

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_data_dir() -> Path:
    """Trả về thư mục data mặc định của dự án."""
    data_dir = paths.path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def _resolve_full_path(filename: str, filepath: str = None) -> Path:
    """
    Xác định đường dẫn tuyệt đối.
    Hỗ trợ cả việc truyền vào một thư mục hoặc một đường dẫn file đầy đủ.
    """
    if not filename.endswith('.mbgrn'):
        filename += '.mbgrn'

    if filepath:
        p = Path(filepath)
        # Nếu filepath là một file (có đuôi .mbgrn), dùng luôn nó
        if p.suffix == '.mbgrn':
            return p
        # Nếu filepath là thư mục, kết hợp với filename
        p.mkdir(parents=True, exist_ok=True)
        return p / filename
    
    # Mặc định: thư mục data của dự án
    return _get_data_dir() / filename

def save_motor(motor_obj, filename: str, filepath: str = None):
    """Lưu motor, hỗ trợ truyền filepath từ QFileDialog."""
    sys.setrecursionlimit(50000)
    full_path = _resolve_full_path(filename, filepath)
    
    try:
        with open(full_path, "wb") as f:
            pickle.dump({"motor": motor_obj}, f, protocol=pickle.HIGHEST_PROTOCOL)
        logger.info(f"Đã lưu tại: {full_path}")
        return True
    except Exception as e:
        logger.error(f"Lỗi lưu file: {e}")
        return False

def load_motor(filename: str, filepath: str = None):
    """Nạp motor, hỗ trợ truyền filepath từ QFileDialog."""
    sys.setrecursionlimit(50000)
    full_path = _resolve_full_path(filename, filepath)
    
    if not full_path.exists():
        logger.warning(f"File không tồn tại: {full_path}")
        return None

    try:
        with open(full_path, "rb") as f:
            data = pickle.load(f)
        return data.get("motor")
    except Exception as e:
        logger.error(f"Lỗi nạp file: {e}")
        return None