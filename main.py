import os
print(os.environ.get("ANSYSEM_ROOT231"))

# Sử dụng thư viện mới theo khuyến nghị của thông báo Warning
from ansys.aedt.core import Desktop, Maxwell2d

# Khởi tạo phiên làm việc Desktop trước
# version="2023.1" tương ứng với bản 2023 R1 bạn vừa cài
with Desktop(version="2023.1", non_graphical=False, new_session=True):
    # Khởi tạo Maxwell2d bên trong khối with Desktop
    m2d = Maxwell2d()
    
    # Kiểm tra phiên bản
    print(f"Đã kết nối thành công với Maxwell phiên bản: {m2d.aedt_version_id}")
    
    # Chèn một thiết kế mới để test
    m2d.insert_design("Motor_Simulation_Test")
    
    # Mã của bạn sẽ tiếp tục ở đây...
    
# Khi thoát khỏi khối 'with', Desktop sẽ tự động được giải phóng (release)