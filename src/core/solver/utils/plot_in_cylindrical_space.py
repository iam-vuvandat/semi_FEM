import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def plot_in_cylindrical_space(r, phi, z, vr, vphi, vz, arrow_length=0.5):
    """
    Vẽ vector dựa trên các thành phần hệ trụ trực tiếp.
    """
    # 1. Tạo không gian vẽ 3D
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 2. Chuyển đổi vị trí điểm gốc P sang Descartes để hiển thị
    px = r * np.cos(phi)
    py = r * np.sin(phi)
    pz = z

    # 3. Chuyển đổi thành phần vector (vr, vphi, vz) sang (vx, vy, vz)
    # Đây là bước bắt buộc để "giao tiếp" với màn hình
    vx = vr * np.cos(phi) - vphi * np.sin(phi)
    vy = vr * np.sin(phi) + vphi * np.cos(phi)
    vz_cart = vz

    # 4. Vẽ các đường lưới hình trụ để định hướng (Cylindrical Grid)
    # Vẽ các vòng tròn đồng tâm tại cao độ z
    thetas = np.linspace(0, 2*np.pi, 100)
    for radius in [r, r*0.5, r*1.5]: # Vẽ vài vòng tròn tham chiếu
        ax.plot(radius * np.cos(thetas), radius * np.sin(thetas), pz, color='gray', alpha=0.3, linestyle='--')
    
    # Vẽ trục Z trung tâm
    ax.plot([0, 0], [0, 0], [pz-1, pz+1], color='black', linewidth=1)

    # 5. Vẽ vector chính (màu đỏ)
    ax.quiver(px, py, pz, vx, vy, vz_cart, 
              length=arrow_length, color='red', linewidth=2, label=f'Vector V(r={vr}, phi={vphi}, z={vz})')

    # 6. Vẽ các vector đơn vị tại điểm đó để tham chiếu (màu xanh)
    # r_hat
    ax.quiver(px, py, pz, np.cos(phi), np.sin(phi), 0, length=0.3, color='blue', alpha=0.5, label='r_hat')
    # phi_hat
    ax.quiver(px, py, pz, -np.sin(phi), np.cos(phi), 0, length=0.3, color='green', alpha=0.5, label='phi_hat')

    # Cấu hình hiển thị
    ax.set_xlabel('X (Descartes Reference)')
    ax.set_ylabel('Y (Descartes Reference)')
    ax.set_zlabel('Z (Axial)')
    ax.set_title('Cylindrical Vector Visualization')
    ax.legend()
    
    # Đảm bảo tỷ lệ các trục bằng nhau để không làm biến dạng vector
    limit = max(r * 1.5, abs(pz) + 1)
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(pz - limit/2, pz + limit/2)

    plt.show()

plot_in_cylindrical_space(r=2, phi=np.pi/4, z=1, vr=0, vphi=1, vz=0.5)