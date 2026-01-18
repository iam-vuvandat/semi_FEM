import os
import pickle
import sys 
import paths
from pathlib import Path

paths.configure_path()

DATA_FILE_NAME = "workspace.pkl"

def _get_data_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, DATA_FILE_NAME)

def save(**kwargs):
    sys.setrecursionlimit(1000000000)
    filepath = _get_data_path()
    data = {}
    
    if os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
        except:
            data = {}
            
    data.update(kwargs)
    
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

def load(*varnames):
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
    filepath = _get_data_path()
    if os.path.exists(filepath):
        with open(filepath, "wb") as f:
            pickle.dump({}, f)