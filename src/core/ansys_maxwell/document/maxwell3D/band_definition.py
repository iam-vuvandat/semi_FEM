import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# ==========================================
# THÔNG SỐ KỸ THUẬT (Giống hệt Script Ansys)
# ==========================================
# Radial Dimensions
R_ROTOR = 1.0
R_MAGNET = 0.9
R_STATOR = 1.0       # Bằng Rotor
R_BAND = 1.02        # Lớn hơn 2% để bao bọc lưới

# Z-Axis Dimensions
Z_ROTOR_BOT = -0.1
Z_ROTOR_TOP = 0.0
Z_MAG_TOP   = 0.1

# Band bao trùm: Thấp hơn đáy Rotor một chút, cao đến giữa khe hở
Z_BAND_BOT  = -0.12
Z_BAND_TOP  = 0.125  # (Khe hở là 0.1 -> 0.15, điểm giữa là 0.125)

# Stator: Bắt đầu từ 0.15
Z_STATOR_BOT = 0.15
Z_STATOR_TOP = 0.25

# ==========================================
# HÀM VẼ TRỤ 3D
# ==========================================
def plot_cylinder(ax, r, z_min, z_max, color, alpha, label):
    z = np.linspace(z_min, z_max, 20)
    theta = np.linspace(0, 2*np.pi, 50)
    theta_grid, z_grid = np.meshgrid(theta, z)
    x_grid = r * np.cos(theta_grid)
    y_grid = r * np.sin(theta_grid)
    
    surf = ax.plot_surface(x_grid, y_grid, z_grid, color=color, alpha=alpha)
    # Hack để tạo legend cho surface
    surf._facecolors2d = surf._facecolor3d
    surf._edgecolors2d = surf._edgecolor3d
    return surf

# ==========================================
# MAIN PLOT
# ==========================================
fig = plt.figure(figsize=(14, 7))

# --- PLOT 1: 3D OVERVIEW ---
ax3d = fig.add_subplot(121, projection='3d')
ax3d.set_title("Mô hình 3D: Cấu trúc lồng ghép")

# 1. Rotor Yoke (Xám)
plot_cylinder(ax3d, R_ROTOR, Z_ROTOR_BOT, Z_ROTOR_TOP, 'gray', 0.8, 'Rotor Yoke')

# 2. Magnet (Đỏ)
plot_cylinder(ax3d, R_MAGNET, Z_ROTOR_TOP, Z_MAG_TOP, 'red', 0.8, 'Magnet')

# 3. Moving Band (Xanh Cyan - Trong suốt)
# Đây là "Lồng khí" bao quanh Rotor và Magnet
plot_cylinder(ax3d, R_BAND, Z_BAND_BOT, Z_BAND_TOP, 'cyan', 0.2, 'Moving Band')

# 4. Stator (Xanh Lá)
plot_cylinder(ax3d, R_STATOR, Z_STATOR_BOT, Z_STATOR_TOP, 'green', 0.6, 'Stator')

# Chỉnh trục
ax3d.set_xlabel('X (mm)')
ax3d.set_ylabel('Y (mm)')
ax3d.set_zlabel('Z (mm)')
ax3d.set_zlim(-0.2, 0.3)
# Tạo proxy artists cho legend
proxy_rotor = patches.Patch(color='gray', label='Rotor (R=1.0)')
proxy_mag   = patches.Patch(color='red', label='Magnet (R=0.9)')
proxy_band  = patches.Patch(color='cyan', alpha=0.3, label='Band (R=1.02)')
proxy_stat  = patches.Patch(color='green', label='Stator (R=1.0)')
ax3d.legend(handles=[proxy_rotor, proxy_mag, proxy_band, proxy_stat])


# --- PLOT 2: 2D CROSS-SECTION (ZOOM) ---
# Mặt cắt trục Z-R để kiểm tra khe hở an toàn
ax2d = fig.add_subplot(122)
ax2d.set_title("Mặt cắt 2D: Kiểm tra khe hở (Gap Check)")

# Vẽ các khối bằng hình chữ nhật (Radius, Height)
# Rotor
ax2d.add_patch(patches.Rectangle((0, Z_ROTOR_BOT), R_ROTOR, Z_ROTOR_TOP - Z_ROTOR_BOT, 
                                 facecolor='gray', edgecolor='black', label='Rotor'))
# Magnet
ax2d.add_patch(patches.Rectangle((0, Z_ROTOR_TOP), R_MAGNET, Z_MAG_TOP - Z_ROTOR_TOP, 
                                 facecolor='red', edgecolor='black', label='Magnet'))
# Band
ax2d.add_patch(patches.Rectangle((0, Z_BAND_BOT), R_BAND, Z_BAND_TOP - Z_BAND_BOT, 
                                 facecolor='cyan', alpha=0.3, edgecolor='blue', linestyle='--', label='Band'))
# Stator
ax2d.add_patch(patches.Rectangle((0, Z_STATOR_BOT), R_STATOR, Z_STATOR_TOP - Z_STATOR_BOT, 
                                 facecolor='green', edgecolor='black', label='Stator'))

# ANNOTATIONS (CHÚ THÍCH KHE HỞ)
# 1. Radial Gap
ax2d.annotate(f'Radial Gap\nR={R_BAND} vs {R_STATOR}', 
              xy=(R_BAND, 0.05), xytext=(R_BAND + 0.3, 0.05),
              arrowprops=dict(facecolor='black', arrowstyle='->'))

# 2. Axial Gap (Z Gap)
ax2d.annotate(f'Axial Gap\nBand Top={Z_BAND_TOP}\nStator Bot={Z_STATOR_BOT}', 
              xy=(0.5, Z_BAND_TOP), xytext=(1.2, 0.13),
              arrowprops=dict(facecolor='black', arrowstyle='->'))

ax2d.set_xlim(0, 1.8)
ax2d.set_ylim(-0.2, 0.3)
ax2d.set_xlabel('Radius (mm)')
ax2d.set_ylabel('Z Position (mm)')
ax2d.grid(True, linestyle=':', alpha=0.6)
ax2d.legend()

plt.tight_layout()
plt.show()