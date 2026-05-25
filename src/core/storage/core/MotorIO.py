import pickle
import sys
import logging
import shutil
from pathlib import Path
from types import SimpleNamespace
import paths 

from src.core.storage.utils.for_motor_io.for_load.read_mbgrn_to_parameter import read_mbgrn_to_parameter

from src.core.storage.utils.for_motor_io.for_save.save_axial_flux_motor_type_1 import save_axial_flux_motor_type_1

from src.core.storage.utils.for_motor_io.for_load.load_axial_flux_motor_type_1 import load_axial_flux_motor_type_1

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MotorIO:
    def __init__(self):
        self.motor_parameter = SimpleNamespace()

    def _resolve_full_path(self, path=None):
        data_dir = paths.path / "data" / "repo"
        data_dir.mkdir(parents=True, exist_ok=True)
        
        if path is None:
            filename = "default_motor.mbgrn"
        else:
            filename = path
            
        p = Path(filename)
        if not p.suffix == '.mbgrn':
            p = p.with_suffix('.mbgrn')
        
        if not p.is_absolute():
            return data_dir / p
        return p

    def save(self, motor, path=None):
        full_path = self._resolve_full_path(path)
        print(f"\033[94mIn function MotorIO.save: {full_path.name}\033[0m")
        print("\033[94m{\033[0m")

        if motor.motor_type == "axial_flux_motor_type_1":
            print(f"\033[94m    Step 1: Routing save to save_axial_flux_motor_type_1...\033[0m")
            result = save_axial_flux_motor_type_1(motor_io=self, motor=motor, path=path)
            print(f"\033[94m    Success: Completed MotorIO.save flow.\033[0m")
            print("\033[94m}\033[0m\n")
            return result
        
        print("\033[94m    Failed: Unsupported motor type.\033[0m")
        print("\033[94m}\033[0m\n")
        return None
        
    def load(self, path=None):
        full_path = self._resolve_full_path(path)
        print(f"\033[94mIn function MotorIO.load: {full_path.name}\033[0m")
        print("\033[94m{\033[0m")

        print(f"\033[94m    Step 1: Executing read_mbgrn_to_parameter...\033[0m")
        read_mbgrn_to_parameter(motor_io=self, path=path)
        
        if self.motor_parameter.motor_type == "axial_flux_motor_type_1":
            print(f"\033[94m    Step 2: Routing load to load_axial_flux_motor_type_1...\033[0m")
            result = load_axial_flux_motor_type_1(motor_io=self)
            print(f"\033[94m    Success: Completed MotorIO.load flow.\033[0m")
            print("\033[94m}\033[0m\n")
            return result
        
        print("\033[94m    Failed: Unsupported motor type in loaded parameters.\033[0m")
        print("\033[94m}\033[0m\n")
        return None