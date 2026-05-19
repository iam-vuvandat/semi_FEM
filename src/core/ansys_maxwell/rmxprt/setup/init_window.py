import os
import glob
import time

def init_window():
    os.system("taskkill /F /IM ansysedt.exe /T")
    os.system("taskkill /F /IM AnsysGRPC.exe /T")

    ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
    for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
        try: os.remove(f)
        except: pass
    time.sleep(1)

if __name__ == "__main__":
    init_window()
    

