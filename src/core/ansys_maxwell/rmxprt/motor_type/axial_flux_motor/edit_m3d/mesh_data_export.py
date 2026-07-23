import os
import re
from types import SimpleNamespace
import paths

def mesh_data_export(motor, m3d):
    print("\033[94mIn function mesh_data_export.\033[0m")
    print("\033[94m{\033[0m")

    project_root = paths.configure_path()
    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)

    mstat_path = os.path.join(temp_dir, "Mesh_Statistics_FEM.mstat")
    formatted_path = mstat_path.replace("\\", "/")

    oDesign = m3d.odesign
    oDesign.ExportMeshStats("Setup1", "", formatted_path)

    motor.record.mesh_data_fem = SimpleNamespace(
        total_elements=0,
        max_element_length=0.0,
        min_element_length=float('inf'),
        unit="mm"
    )

    if not os.path.exists(mstat_path):
        print(f"\033[94mIn function mesh_data_export: Mesh stats file not found at {mstat_path}\033[0m")
        print("\033[94m}\033[0m")
        print("\033[94m\033[0m")
        return

    with open(mstat_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    min_edge_idx, max_edge_idx = -1, -1
    in_table = False

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        if "Total number of mesh elements:" in line_str:
            match = re.search(r"Total number of mesh elements:\s*(\d+)", line_str)
            if match:
                motor.record.mesh_data_fem.total_elements = int(match.group(1))
            continue

        if "Num Tets" in line_str and "Min edge length" in line_str:
            headers = [h.strip() for h in line_str.split('|') if h.strip()]
            for idx, h in enumerate(headers):
                if "Min edge length" in h:
                    min_edge_idx = idx
                elif "Max edge length" in h:
                    max_edge_idx = idx
            in_table = True
            continue

        if in_table and '|' in line_str and min_edge_idx != -1 and max_edge_idx != -1:
            parts = [p.strip() for p in line_str.split('|')]
            values = parts[1:]

            if len(values) > max(min_edge_idx, max_edge_idx):
                try:
                    current_min = float(values[min_edge_idx])
                    current_max = float(values[max_edge_idx])

                    if current_min < motor.record.mesh_data_fem.min_element_length:
                        motor.record.mesh_data_fem.min_element_length = current_min

                    if current_max > motor.record.mesh_data_fem.max_element_length:
                        motor.record.mesh_data_fem.max_element_length = current_max
                except ValueError:
                    pass

    if motor.record.mesh_data_fem.min_element_length == float('inf'):
        motor.record.mesh_data_fem.min_element_length = 0.0

    print(f"\033[94mIn function mesh_data_export: Successfully exported mesh statistics.\033[0m")
    print("\033[94m}\033[0m")
    print("\033[94m\033[0m")