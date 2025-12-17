import os
import pickle
import sys 

# Tên file dữ liệu (nằm cùng thư mục với file script này)
DATA_FILE_NAME = "workspace.pkl"

def _get_data_path():
    """
    Trả về đường dẫn tuyệt đối của file workspace.pkl
    Logic: Lấy đường dẫn của file code này -> ghép với tên file pkl
    """
    # Lấy đường dẫn thư mục hiện tại (thư mục 'core')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(current_dir, DATA_FILE_NAME)

def save(**kwargs):
    """
    Lưu biến vào workspace.pkl
    Ví dụ: workspace.save(x=10, data=[1,2])
    """
    sys.setrecursionlimit(1000000000)
    filepath = _get_data_path()
    data = {}
    
    # Load dữ liệu cũ để không bị mất
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
        except:
            data = {} # Nếu file lỗi thì reset
            
    data.update(kwargs)
    
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

def load(*varnames):
    """
    Load biến từ workspace.pkl
    Ví dụ: 
        val = workspace.load("x")
        x, y = workspace.load("x", "y")
    """
    filepath = _get_data_path()
    
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
    except:
        return None
        
    if len(varnames) == 1:
        return data.get(varnames[0])
    elif varnames:
        return tuple(data.get(k) for k in varnames)
    return data

def clear():
    """Xóa sạch dữ liệu"""
    filepath = _get_data_path()
    if os.path.exists(filepath):
        with open(filepath, "wb") as f:
            pickle.dump({}, f)