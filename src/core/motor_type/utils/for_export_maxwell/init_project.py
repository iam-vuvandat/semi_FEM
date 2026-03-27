from typing import Any
import os
import paths
from ansys.aedt.core import Maxwell3d
from dataclasses import dataclass
import time

def init_project(project_name = "pyaedt_test", solution_type = "Transient", motor= None) :

    version = motor.maxwell_export_option.ansys_electronic_version

    m3d = Maxwell3d(version= version, new_desktop=True, non_graphical=False)
    project_root = paths.configure_path()
    save_path = os.path.join(project_root, "Ansys_Projects")
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if not project_name.endswith(".aedt"):
        project_name += ".aedt"

    project_name = os.path.join(save_path, project_name)
    m3d.save_project(project_name)

    time.sleep(1)
    m3d.solution_type = solution_type
    m3d.change_material_override(True)

    return m3d