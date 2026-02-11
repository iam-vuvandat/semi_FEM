import os
from ansys.aedt.core import Maxwell3d

class Maxwell3DService:
    def __init__(self, project_dir, project_name="Log_Testing_V2", version="2023.1"):
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        self.project_path = os.path.join(project_dir, project_name + ".aedt")
        
        self.m3d = Maxwell3d(
            project=self.project_path,
            design="Log_Design",
            solution_type="Transient",
            version=version,
            new_desktop=True,
            non_graphical=False
        )
        self.m3d.modeler.model_units = "mm"

    def create_geometry(self):
        # Sử dụng tên vật liệu chuẩn trong thư viện 2023 R1
        mat_name = "ndfeb35" 
        
        # Vẽ nam châm
        self.magnet = self.m3d.modeler.create_box(
            origin=[-10, -10, -10], 
            sizes=[20, 20, 20], 
            name="PM", 
            material=mat_name
        )
        
        # Tạo vùng không khí (Phải đủ rộng để từ trường khép vòng)
        self.m3d.modeler.create_air_region(100, 100, 100, 100, 100, 100)

    def setup_physics(self):
        setup = self.m3d.create_setup(name="MySetup")
        setup.props["StopTime"] = "0.01s"
        setup.props["TimeStep"] = "0.001s"
        setup.update()

    def run_and_display(self):
        self.m3d.save_project()
        print("--- Đang bắt đầu giải bài toán... ---")
        
        # Chạy mô phỏng
        status = self.m3d.analyze_setup("MySetup")
        
        if not status:
            print("\n[!] PHÁT HIỆN LỖI TỪ MAXWELL - CHI TIẾT LOG:")
            # Sửa lỗi AttributeError bằng cách dùng self.m3d.logger
            msgs = self.m3d.logger.get_messages(self.m3d.project_name, self.m3d.design_name)
            for m in msgs:
                print(f" >>> {m}")
        else:
            print("--- Giải thành công! ---")
            self.m3d.post.create_fieldplot_surface(
                assignment=self.m3d.modeler.get_object_faces("PM"),
                quantity="Mag_B"
            )
            self.m3d.modeler.fit_all()

if __name__ == "__main__":
    work_dir = r"C:\Users\Surface\semi_FEM\Ansys_Projects"
    service = Maxwell3DService(project_dir=work_dir)
    service.create_geometry()
    service.setup_physics()
    service.run_and_display()