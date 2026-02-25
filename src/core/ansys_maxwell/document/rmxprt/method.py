import os
import glob
import time
import inspect
from pyaedt import Rmxprt

os.system("taskkill /F /IM ansysedt.exe /T")
os.system("taskkill /F /IM AnsysGRPC.exe /T")
ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
    try: os.remove(f)
    except: pass
time.sleep(2)

rmxprt = Rmxprt(version="2023.1", new_desktop=True, non_graphical=False)

def list_all_members(obj, obj_name, file_handle, limit_depth=9999):
    file_handle.write(f"\n{'='*20} METHODS OF {obj_name} {'='*20}\n")
    
    for member in dir(obj):
        if member.startswith("_"):
            continue
        try:
            attr = getattr(obj, member)
            if callable(attr):
                sig = inspect.signature(attr)
                file_handle.write(f"{obj_name}.{member}{sig}\n")
        except Exception:
            continue

    if limit_depth > 0:
        try:
            # Cac doi tuong con dac thu cua RMxprt trong PyAEDT
            children = {
                "modeler": obj.modeler,
                "post": obj.post
            }
            
            if obj_name == "rmxprt":
                for child_name, child_obj in children.items():
                    list_all_members(child_obj, f"rmxprt.{child_name}", file_handle, limit_depth - 1)
        except AttributeError:
            pass

output_path = os.path.join(os.getcwd(), "rmxprt_full_methods_report.txt")
with open(output_path, "w", encoding="utf-8") as f:
    list_all_members(rmxprt, "rmxprt", f)

print(f"Hoan thanh. Ket qua da duoc ghi vao: {output_path}")

# rmxprt.release_desktop()