import os
import pickle
import sys
import paths
from pathlib import Path

paths.configure_path()

def _get_data_dir():
    data_dir = paths.path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def save_motor(motor_obj, filename):
    sys.setrecursionlimit(1000000000)
    
    if not filename.endswith('.mbgrn'):
        filename += '.mbgrn'
        
    filepath = _get_data_dir() / filename
    
    data = {"motor": motor_obj}
    
    try:
        with open(filepath, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        return True
    except:
        return False

def load_motor(filename):
    sys.setrecursionlimit(1000000000)
    
    if not filename.endswith('.mbgrn'):
        filename += '.mbgrn'
        
    filepath = _get_data_dir() / filename
    
    if not filepath.exists():
        return None

    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        return data.get("motor")
    except:
        return None

def delete_motor(filename):
    if not filename.endswith('.mbgrn'):
        filename += '.mbgrn'
    filepath = _get_data_dir() / filename
    if filepath.exists():
        os.remove(filepath)