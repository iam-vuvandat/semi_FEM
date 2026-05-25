import os
import glob
import time

def init_window():
    print("\033[94m\033[0m")
    print("\033[94mIn function init_window.\033[0m")
    print("\033[94m{\033[0m")

    os.system("taskkill /F /IM ansysedt.exe /T")
    os.system("taskkill /F /IM AnsysGRPC.exe /T")
    ansoft_dir = r"C:\Users\Surface\Documents\Ansoft"
    for f in glob.glob(os.path.join(ansoft_dir, "*.aedt.auto")):
        try: os.remove(f)
        except: pass
    time.sleep(1)

    print("\033[94mIn function init_window: Successfully killed Ansys tasks.\033[0m")
    print("\033[94m}\033[0m")
    print("\033[94m\033[0m")

if __name__ == "__main__":
    init_window()