import numpy as np
import matplotlib.pyplot as plt

def decompose_harmonics(signal, n_harmonics=20):
    """
    Phân tích một tín hiệu tuần hoàn thành các thành phần sóng hài (biên độ và pha).
    """
    n = len(signal)
    yf = np.fft.rfft(signal)
    
    # Chuẩn hóa biên độ về giá trị đỉnh (Peak Amplitude)
    amplitudes = np.abs(yf) * 2 / n
    amplitudes[0] = amplitudes[0] / 2
    
    phases = np.angle(yf)
    limit = min(len(amplitudes), n_harmonics + 1)
    
    return amplitudes[:limit], phases[:limit]

if __name__ == "__main__":
    # Thiết lập cấu hình đồ thị chuyên nghiệp
    plt.rcParams.update({
        'font.size': 16,
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'axes.grid': True,
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
        'mathtext.fontset': 'stix'
    })

    # Tạo tín hiệu test: Sóng cơ bản (10) + Bậc 3 (5) + Bậc 5 (2)
    n_point = 1000
    theta = np.linspace(0, 2*np.pi, n_point, endpoint=False)
    test_signal = (10 * np.sin(theta) + 
                   5  * np.sin(3 * theta + np.pi/4) + 
                   2  * np.sin(5 * theta))

    # Phân tích 10 bậc sóng hài đầu tiên
    max_h = 10
    amps, phases = decompose_harmonics(test_signal, n_harmonics=max_h)
    harmonic_orders = np.arange(len(amps))

    # Vẽ đồ thị
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Đồ thị miền thời gian/vị trí
    ax1.plot(theta, test_signal, color='#0072BD', linewidth=2.0, label='Original Signal')
    ax1.set_xlabel('Position [rad]')
    ax1.set_ylabel('Amplitude')
    ax1.legend(loc='upper right')
    ax1.set_title('Time Domain Signal')

    # Đồ thị phổ sóng hài (Bar chart)
    bars = ax2.bar(harmonic_orders, amps, color='#D95319', alpha=0.8, width=0.5, label='Harmonic Content')
    ax2.set_xlabel('Harmonic Order')
    ax2.set_ylabel('Amplitude')
    ax2.set_xticks(harmonic_orders)
    ax2.set_title('Harmonic Spectrum')

    # Hiển thị giá trị trên đỉnh các cột
    for bar in bars:
        height = bar.get_height()
        if height > 0.1:
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                     f'{height:.1f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.show()