import importlib
import subprocess
import sys

def install_library():
    packages = {
        'numpy': 'numpy',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'sklearn': 'scikit-learn',
        'trimesh': 'trimesh',
        'shapely': 'shapely',
        'pyvista': 'pyvista',
        'pyglet': 'pyglet<2',
        'manifold3d': 'manifold3d',
        'rtree': 'rtree',
        'tqdm': 'tqdm',
        'imageio': 'imageio',
        'pympler': 'pympler',
        'win32com.client': 'pywin32',
        'ansys.motorcad.core': 'ansys-motorcad-core',
        'pyamg': 'pyamg',
        'pyvistaqt': 'pyvistaqt',
        'PyQt5': 'PyQt5'
    }

    installed_modules = []
    print("Checking libraries...")

    for module, package in packages.items():
        try:
            importlib.import_module(module)
            installed_modules.append(module)
        except ImportError:
            print(f"[-] '{module}' not found. Installing '{package}'...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"[+] Successfully installed '{package}'.")
                installed_modules.append(module)
            except subprocess.CalledProcessError as e:
                print(f"[!] WARNING: Installation of '{package}' FAILED with code {e.returncode}. Skipping.")
                continue

    print("\nAll library checks completed.")
    return installed_modules

if __name__ == "__main__":
    install_library()