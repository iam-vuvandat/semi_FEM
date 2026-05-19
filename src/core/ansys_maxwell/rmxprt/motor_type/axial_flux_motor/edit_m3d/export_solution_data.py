import os
import paths
import re

def export_solution_data(m3d,motor):
    setup_name = "Setup1"
    variations = ""
    file_name = "solution_data.prof"
    
    project_root = paths.configure_path()
    temp_dir = os.path.join(project_root, "data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    prof_path = os.path.join(temp_dir, file_name)
    
    if os.path.exists(prof_path):
        os.remove(prof_path)
    
    oDesign = m3d.odesign
    oDesign.ExportProfile(setup_name, variations, prof_path.replace("\\", "/"))
    
    total_time_sec = 0
    max_elements = 0
    max_matrix = 0
    max_memory_mb = 0.0
    
    if os.path.exists(prof_path):
        with open(prof_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            time_matches = re.findall(r"Solution Process.*Elapsed Time:\s*([\d:]+)", content)
            if time_matches:
                time_str = time_matches[-1]
                time_parts = time_str.split(':')
                if len(time_parts) == 3:
                    total_time_sec = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
            
            tetra_matches = re.findall(r"Tetrahedra:\s*(\d+)", content)
            if tetra_matches:
                max_elements = max([int(x) for x in tetra_matches])
            
            matrix_matches = re.findall(r"Matrix:\s*(\d+)", content)
            if matrix_matches:
                max_matrix = max([int(x) for x in matrix_matches])
            
            memory_matches = re.findall(r"(\d+\.\d+|\d+)\s*([KMG])\b", content)
            for val_str, unit in memory_matches:
                val = float(val_str)
                if unit == 'G':
                    val_mb = val * 1024.0
                elif unit == 'K':
                    val_mb = val / 1024.0
                else:
                    val_mb = val
                    
                if val_mb > max_memory_mb:
                    max_memory_mb = val_mb
                    
    print(f"\033[92mSolution Data Extracted - Elements: {max_elements} | Matrix: {max_matrix} | Memory: {max_memory_mb:.2f} MB\033[0m")

    
    if hasattr(motor.record,"total_elements_fem"):
        pass
    else:
        motor.record.total_elements_fem = max_elements

    if hasattr(motor.record,"matrix_size_fem"):
        pass
    else:
        motor.record.matrix_size_fem = max_matrix

    if hasattr(motor.record,"memory_used_fem"):
        pass
    else:
        motor.record.memory_used_fem = max_memory_mb
    return {
        "max_elements": max_elements,
        "max_matrix": max_matrix,
        "max_memory_mb": max_memory_mb
    }
