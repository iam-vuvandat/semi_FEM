import os
import paths
from ansys.aedt.core import Rmxprt
import time

def init_rmxprt(project_name = "rmxprt_test", motor = None):

    version = motor.maxwell_export_option.ansys_electronic_version

    rmxprt = Rmxprt(version=version, new_desktop=True, non_graphical=False)
    
    project_root = paths.configure_path()
    save_path = os.path.join(project_root, "data","temp")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if not project_name.endswith(".aedt"):
        project_name += ".aedt"

    project_name = os.path.join(save_path, project_name)
    rmxprt.save_project(project_name)

    time.sleep(1)

    print(f"\033[93minit_rmxprt return: {rmxprt}\033[0m")
    return rmxprt