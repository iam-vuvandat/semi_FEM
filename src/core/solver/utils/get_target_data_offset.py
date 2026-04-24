import numpy as np
import matplotlib.pyplot as plt

def get_target_data_offset(ref_data, target_data, half_open_interval = True, apply_on_target_data = True):
    # Trích xuất dữ liệu dựa trên khoảng hở/đóng để tính toán tương quan
    if half_open_interval:
        sig_ref_val = ref_data[0, :-1]
        sig_target_val = target_data[0, :-1]
    else:
        sig_ref_val = ref_data[0, :]
        sig_target_val = target_data[0, :]
    
    # Khử trung bình để tập trung hoàn toàn vào biến thiên dạng sóng (trend)
    sig_ref_centered = sig_ref_val - np.mean(sig_ref_val)
    sig_target_centered = sig_target_val - np.mean(sig_target_val)
    
    # Cross-correlation tìm vị trí mà sự tương đồng về hình dạng là lớn nhất
    correlation = np.correlate(sig_ref_centered, sig_target_centered, mode='full')
    lags = np.arange(-len(sig_ref_centered) + 1, len(sig_ref_centered))
    lag_steps = lags[np.argmax(correlation)]
    
    physical_data = target_data[:-1, :]
    position_axis = target_data[-1, :]
    
    # Dịch chuyển dữ liệu vật lý (Data) trong khi giữ cố định tọa độ (Position)
    shifted_physical_data = np.roll(physical_data, shift=lag_steps, axis=1)
    
    if apply_on_target_data:
        target_data[:-1, :] = shifted_physical_data
    
    target_data_offset = np.vstack((shifted_physical_data, position_axis))
    
    return target_data_offset

if __name__ == "__main__":
    # TẠO TEST CASE: Tín hiệu có biên độ lệch nhau nhưng cùng tính tương quan
    n_points = 400
    theta = np.linspace(0, 4*np.pi, n_points) # 2 chu kỳ
    
    # SF (Reference): Tín hiệu chuẩn
    y_ref = 10 * np.sin(theta) + 2 * np.cos(3 * theta)
    ref_data = np.vstack((y_ref, theta))
    
    # FEM (Target): Biên độ nhỏ hơn, có DC offset, và bị lệch pha 50 bước
    # Chúng ta muốn khớp "xu hướng" của FEM về với SF
    y_target_raw = 0.7 * (10 * np.sin(theta) + 2 * np.cos(3 * theta)) + 5.0 
    y_target_shifted = np.roll(y_target_raw, shift=50)
    target_data = np.vstack((y_target_shifted, theta))
    
    y_before = target_data[0, :].copy()

    # THỰC HIỆN KHỚP
    get_target_data_offset(ref_data, target_data, apply_on_target_data=True)

    # TÍNH TOÁN ĐỘ TƯƠNG QUAN (PEARSON R)
    # r = 1: Đồng biến hoàn toàn | r = -1: Nghịch biến hoàn toàn
    r_matrix = np.corrcoef(ref_data[0, :], target_data[0, :])
    pearson_r = r_matrix[0, 1]

    print(f"--- Correlation Alignment Test ---")
    print(f"Pearson Correlation Coefficient (r): {pearson_r:.6f}")

    # VẼ ĐỒ THỊ QUAN SÁT
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Đồ thị 1: So sánh biên độ (Thấy rõ sự lệch về độ lớn nhưng khớp về pha)
    ax1.plot(theta, ref_data[0, :], 'k-', label='SF (Ref)')
    ax1.plot(theta, target_data[0, :], 'r--', label='FEM (Aligned)')
    ax1.set_ylabel("Amplitude")
    ax1.legend()
    ax1.set_title("Amplitude View: Notice the shift matches trend despite scale difference")

    # Đồ thị 2: Chuẩn hóa về cùng dải [0, 1] để thấy rõ tính "đồng biến/nghịch biến"
    def normalize(v): return (v - v.min()) / (v.max() - v.min())
    ax2.plot(theta, normalize(ref_data[0, :]), 'k-', alpha=0.8, label='SF Normalized')
    ax2.plot(theta, normalize(target_data[0, :]), 'r:', linewidth=2, label='FEM Normalized')
    ax2.set_ylabel("Normalized Scale")
    ax2.set_xlabel("Rotor Position (rad)")
    ax2.legend()
    ax2.set_title(f"Trend View: Pearson r = {pearson_r:.4f} (Perfect overlap in trend)")

    plt.tight_layout()
    plt.show()

    if pearson_r > 0.99:
        print("\033[92mSUCCESS: Signals are perfectly synchronized in trend (Sync by Correlation).\033[0m")