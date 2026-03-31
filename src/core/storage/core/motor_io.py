import pickle
import sys
import logging
import shutil
from pathlib import Path
import paths 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _get_data_dir() -> Path:
    data_dir = paths.path / "data" / "repo"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def _resolve_full_path(filename: str, filepath: str = None) -> Path:
    if not filename.endswith('.mbgrn'):
        filename += '.mbgrn'
    if filepath:
        p = Path(filepath)
        if p.suffix == '.mbgrn': return p
        p.mkdir(parents=True, exist_ok=True)
        return p / filename
    return _get_data_dir() / filename

def save_motor(motor_obj, filename: str, filepath: str = None, callback=None):
    """
    Lưu motor theo phương pháp Blacklist: Lưu tất cả trừ các thuộc tính trong danh sách loại trừ.
    """
    sys.setrecursionlimit(100000) 
    full_path = _resolve_full_path(filename, filepath)
    temp_path = full_path.with_suffix('.tmp')

    # Danh sách các thuộc tính KHÔNG muốn lưu (Blacklist)
    # Ví dụ: logger, các cache tính toán tạm thời, hoặc các đối tượng không thể pickle
    excluded_attributes = [
        'reluctance_network'
    ]

    if callback: callback(f"Filtering and preparing to save: {full_path.name}...")

    try:
        # Lấy toàn bộ dictionary của đối tượng và loại bỏ các phần tử trong blacklist
        full_state = motor_obj.__dict__.copy()
        for attr in excluded_attributes:
            if attr in full_state:
                full_state.pop(attr)
                logger.info(f"Excluded attribute: {attr}")

        # Lưu kèm theo thông tin về Class để phục hồi method khi load
        data_to_pickle = {
            "class_type": type(motor_obj), 
            "state": full_state
        }

        with open(temp_path, "wb") as f:
            pickle.dump(data_to_pickle, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        if temp_path.exists():
            shutil.move(str(temp_path), str(full_path))
        
        if callback: callback(f"Successfully saved: {full_path.name}")
        return True

    except Exception as e:
        logger.error(f"Save error: {e}")
        if callback: callback(f"Error while saving: {str(e)}")
        if temp_path.exists(): temp_path.unlink() 
        return False

def load_motor(filename: str, filepath: str = None, callback=None):
    """
    Nạp motor và khôi phục đầy đủ cả dữ liệu lẫn các Method của Class gốc.
    """
    sys.setrecursionlimit(1000000000)
    full_path = _resolve_full_path(filename, filepath)
    
    if not full_path.exists():
        if callback: callback(f"File not found: {full_path}")
        return None

    try:
        with open(full_path, "rb") as f:
            data = pickle.load(f)
        
        class_type = data.get("class_type")
        state = data.get("state")

        if class_type and state:
            # 1. Tạo một instance mới của Class gốc mà không gọi hàm __init__ 
            # (Tránh việc khởi tạo lại làm mất dữ liệu hoặc tốn thời gian)
            motor = class_type.__new__(class_type)
            
            # 2. Đổ toàn bộ dữ liệu vào instance này
            motor.__dict__.update(state)
            
            # 3. Khởi tạo lại các thuộc tính bị loại bỏ nếu cần (ví dụ logger)
            if hasattr(motor, 'init_logger'): 
                motor.init_logger()

            if callback: callback(f"Load completed with methods: {full_path.name}")
            return motor
        
        return None

    except Exception as e:
        logger.error(f"Load error: {e}")
        if callback: callback(f"Error while loading: {str(e)}")
        return None