import pickle
import sys
import logging
import shutil
from pathlib import Path
import paths 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_data_dir() -> Path:
    data_dir = paths.path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def _resolve_full_path(filename: str, filepath: str = None) -> Path:
    if not filename.endswith('.mbgrn'):
        filename += '.mbgrn'

    if filepath:
        p = Path(filepath)
        if p.suffix == '.mbgrn':
            return p
        p.mkdir(parents=True, exist_ok=True)
        return p / filename
    
    return _get_data_dir() / filename

def save_motor(motor_obj, filename: str, filepath: str = None, callback=None):
    """
    Lưu motor an toàn với callback thông báo trạng thái.
    Chiến thuật: Ghi vào file .tmp trước, sau đó mới đổi tên thành .mbgrn chính thức.
    """
    sys.setrecursionlimit(100000) # Tăng giới hạn đệ quy cho các mesh phức tạp
    full_path = _resolve_full_path(filename, filepath)
    temp_path = full_path.with_suffix('.tmp')

    if callback: callback(f"Preparing to save: {full_path.name}...")

    try:
        # 1. Ghi vào file tạm (.tmp)
        with open(temp_path, "wb") as f:
            pickle.dump({"motor": motor_obj}, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        if callback: callback("Finalizing file structure...")

        # 2. Ghi đè file chính thức (Atomic operation)
        if temp_path.exists():
            shutil.move(str(temp_path), str(full_path))
        
        logger.info(f"Successfully saved to: {full_path}")
        if callback: callback(f"Successfully saved: {full_path.name}")
        return True

    except Exception as e:
        logger.error(f"Save error: {e}")
        if callback: callback(f"Error while saving: {str(e)}")
        if temp_path.exists():
            temp_path.unlink() # Xóa file tạm bị hỏng
        return False

def load_motor(filename: str, filepath: str = None, callback=None):
    """Nạp motor và thông báo trạng thái qua callback."""
    sys.setrecursionlimit(1000000000)
    full_path = _resolve_full_path(filename, filepath)
    
    if not full_path.exists():
        msg = f"File not found: {full_path}"
        logger.warning(msg)
        if callback: callback(msg)
        return None

    if callback: callback(f"Loading data from {full_path.name}...")

    try:
        with open(full_path, "rb") as f:
            data = pickle.load(f)
        
        motor = data.get("motor")
        if motor:
            if callback: callback(f"Load completed: {full_path.name}")
            return motor
        else:
            if callback: callback("Error: File contains no motor data.")
            return None

    except Exception as e:
        logger.error(f"Load error: {e}")
        if callback: callback(f"Error while loading: {str(e)}")
        return None