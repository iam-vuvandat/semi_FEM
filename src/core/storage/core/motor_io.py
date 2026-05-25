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

    motor_obj.prepare_to_save()

    sys.setrecursionlimit(1000) 
    full_path = _resolve_full_path(filename, filepath)
    temp_path = full_path.with_suffix('.tmp')

    print(f"\033[94mIn function save_motor: {full_path.name}\033[0m")
    print("\033[94m{\033[0m")
    if callback: callback(f"Starting save: {full_path.name}")

    excluded_attributes = [
        'reluctance_network','geometry'
    ]

    try:
        print(f"\033[94m    Step 1: Filtering attributes (Blacklist: {excluded_attributes})...\033[0m")
        if callback: callback(f"Filtering and preparing to save: {full_path.name}...")
        
        full_state = motor_obj.__dict__.copy()
        for attr in excluded_attributes:
            if attr in full_state:
                full_state.pop(attr)
                logger.info(f"Excluded attribute: {attr}")

        data_to_pickle = {
            "class_type": type(motor_obj), 
            "state": full_state
        }

        print(f"\033[94m    Step 2: Serializing data to temporary file...\033[0m")
        with open(temp_path, "wb") as f:
            pickle.dump(data_to_pickle, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        print(f"\033[94m    Step 3: Moving temporary file to final destination...\033[0m")
        if temp_path.exists():
            shutil.move(str(temp_path), str(full_path))
        
        print(f"\033[94m    Success: Motor saved at {full_path}\033[0m")
        print("\033[94m}\033[0m\n")
        if callback: callback(f"Successfully saved: {full_path.name}")
        return True

    except Exception as e:
        print(f"\033[94m    Failed: Save error - {str(e)}\033[0m")
        print("\033[94m}\033[0m\n")
        logger.error(f"Save error: {e}")
        if callback: callback(f"Error while saving: {str(e)}")
        if temp_path.exists(): temp_path.unlink() 
        return False

def load_motor(filename: str, filepath: str = None, callback=None):
    """
    Nạp motor và khôi phục đầy đủ cả dữ liệu lẫn các Method của Class gốc.
    """
    sys.setrecursionlimit(1000)
    full_path = _resolve_full_path(filename, filepath)
    
    print(f"\033[94mIn function load_motor: {full_path.name}\033[0m")
    print("\033[94m{\033[0m")
    if callback: callback(f"Starting load: {full_path.name}")

    if not full_path.exists():
        print(f"\033[94m    Failed: File not found at {full_path}\033[0m")
        print("\033[94m}\033[0m\n")
        if callback: callback(f"File not found: {full_path}")
        return None

    try:
        print(f"\033[94m    Step 1: Reading and unpickling data from file...\033[0m")
        with open(full_path, "rb") as f:
            data = pickle.load(f)
        
        class_type = data.get("class_type")
        state = data.get("state")

        if class_type and state:
            print(f"\033[94m    Step 2: Reconstructing {class_type.__name__} instance...\033[0m")
            motor = class_type.__new__(class_type)
            
            print(f"\033[94m    Step 3: Updating instance dictionary with loaded state...\033[0m")
            motor.__dict__.update(state)
            
            if hasattr(motor, 'init_logger'): 
                print(f"\033[94m    Step 4: Re-initializing logger...\033[0m")
                motor.init_logger()

            print(f"\033[94m    Success: Motor loaded from {full_path}\033[0m")
            print("\033[94m}\033[0m\n")
            if callback: callback(f"Load completed with methods: {full_path.name}")
            return motor
        
        print("\033[94m    Failed: Invalid data structure in file.\033[0m")
        print("\033[94m}\033[0m\n")
        return None

    except Exception as e:
        print(f"\033[94m    Failed: Load error - {str(e)}\033[0m")
        print("\033[94m}\033[0m\n")
        logger.error(f"Load error: {e}")
        if callback: callback(f"Error while loading: {str(e)}")
        return None