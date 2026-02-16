import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
try:
    # Thu vien chuyen dung cho may dien
    from pyleecan.Classes.Winding import Winding
    from pyleecan.Classes.LamSlotWind import LamSlotWind
except ImportError:
    print("Lỗi: Vui lòng cài đặt pyleecan: 'pip install pyleecan'")
    exit()

def plot_winding_layout(Zs, p, qs, Nlayer):
    """
    Hàm tính toán và vẽ sơ đồ trải dây quấn.
    
    Args:
        Zs (int): Tổng số rãnh Stator.
        p (int): Số cặp cực (pole pairs).
        qs (int): Số pha (thường là 3).
        Nlayer (int): Số lớp dây quấn (1 hoặc 2).
    """
    print(f"--- Đang tính toán sơ đồ dây quấn cho: Zs={Zs}, p={p} ({2*p} cực), {qs} pha, {Nlayer} lớp ---")

    # --- BƯỚC 1: SỬ DỤNG PYLEECAN ĐỂ TÍNH MA TRẬN DÂY QUẤN ---
    # 1. Tạo đối tượng Stator (Lamination) ảo để chứa dây quấn
    stator = LamSlotWind(Zs=Zs, is_stator=True)
    
    # 2. Định nghĩa đối tượng Winding với các tham số đầu vào
    # pyleecan tự động chọn kiểu quấn tối ưu dựa trên Zs và p
    winding = Winding(qs=qs, p=p, Nlayer=Nlayer)
    stator.winding = winding

    # 3. Tính toán ma trận kết nối
    # Kết quả là mảng 4 chiều: [N_rad, N_tan, Zs, qs]
    # Với dây quấn thông thường, ta quan tâm 3 chiều cuối: [Số lớp, Số rãnh, Số pha]
    wind_mat_raw = winding.comp_connection_mat(Zs)
    
    # Rút gọn ma trận để dễ xử lý: [Layer index, Slot index, Phase index]
    # Giá trị trong ma trận: 1 (Dương), -1 (Âm), 0 (Không có dây)
    wind_mat = wind_mat_raw[0, :, :, :] 

    # Tính hệ số dây quấn cơ bản để kiểm tra
    kw1 = winding.comp_kw()[0]
    print(f"-> Tính toán hoàn tất. Hệ số dây quấn cơ bản kw1 = {kw1:.4f}")


    # --- BƯỚC 2: VẼ SƠ ĐỒ TRẢI BẰNG MATPLOTLIB ---
    
    fig, ax = plt.subplots(figsize=(Zs * 0.8, Nlayer * 2 + 1))
    
    # Cấu hình màu sắc cho các pha (A: Đỏ, B: Xanh lá, C: Xanh dương)
    phase_colors = ['red', 'green', 'blue']
    phase_names = ['A', 'B', 'C']
    
    # Vẽ khung các rãnh
    for s in range(Zs):
        # Vẽ vách ngăn rãnh
        ax.axvline(x=s + 0.5, color='gray', linestyle='--', alpha=0.5)
        # Đánh số rãnh
        ax.text(s + 1, -0.3, str(s + 1), ha='center', fontsize=10, fontweight='bold')

    # Duyệt qua ma trận để vẽ các cạnh tác dụng
    # wind_mat shape: [Nlayer, Zs, qs]
    for layer_idx in range(Nlayer):
        y_pos = layer_idx + 1 # Tọa độ Y cho lớp (Lớp 1 ở dưới, Lớp 2 ở trên)
        
        for slot_idx in range(Zs):
            x_pos = slot_idx + 1 # Tọa độ X cho rãnh
            
            # Tìm xem tại rãnh này, lớp này là pha nào và cực tính gì
            coil_drawn = False
            for phase_idx in range(qs):
                polarity = wind_mat[layer_idx, slot_idx, phase_idx]
                
                if polarity != 0:
                    color = phase_colors[phase_idx]
                    
                    # Vẽ mũi tên chỉ hướng dòng điện
                    if polarity == 1: # Cực tính Dương (+) -> Đi lên
                        arrow_style = patches.ArrowStyle("->", head_length=0.4, head_width=0.3)
                        marker_text = "+"
                        xy_start = (x_pos, y_pos - 0.25)
                        xy_end = (x_pos, y_pos + 0.25)
                    else: # Cực tính Âm (-) -> Đi xuống
                        arrow_style = patches.ArrowStyle("<-", head_length=0.4, head_width=0.3)
                        marker_text = "-"
                        xy_start = (x_pos, y_pos - 0.25)
                        xy_end = (x_pos, y_pos + 0.25)

                    arrow = patches.FancyArrowPatch(xy_start, xy_end, arrowstyle=arrow_style, 
                                                    color=color, linewidth=2)
                    ax.add_patch(arrow)

                    # Ghi nhãn Pha (VD: A+, B-)
                    label = f"{phase_names[phase_idx]}{marker_text}"
                    ax.text(x_pos, y_pos + 0.4, label, ha='center', color=color, fontweight='bold')
                    coil_drawn = True
                    break # Đã tìm thấy pha cho vị trí này, chuyển sang rãnh tiếp theo
            
            # Nếu vị trí này không có dây (ví dụ quấn răng lược)
            if not coil_drawn:
                 ax.text(x_pos, y_pos, "X", ha='center', color='gray', alpha=0.3)

    # Cấu hình trục và tiêu đề
    ax.set_xlim(0.5, Zs + 0.5)
    ax.set_ylim(0, Nlayer + 1)
    
    # Ẩn trục Y số, thay bằng nhãn lớp
    ax.set_yticks(np.arange(1, Nlayer + 1))
    layer_labels = [f"Lớp {i+1} (Đáy)" if i==0 else f"Lớp {i+1} (Đỉnh)" for i in range(Nlayer)]
    ax.set_yticklabels(layer_labels)
    
    # Ẩn trục X số, chỉ giữ lại nhãn rãnh đã vẽ thủ công
    ax.set_xticks([]) 

    ax.set_xlabel("Số thứ tự rãnh Stator", fontsize=12, labelpad=20)
    ax.set_title(f"Sơ đồ trải dây quấn: Zs={Zs}, 2p={2*p}, {Nlayer} Lớp", fontsize=14, pad=20)
    
    # Tạo chú thích (Legend) thủ công
    legend_elements = [
        patches.Patch(facecolor='red', label='Pha A'),
        patches.Patch(facecolor='green', label='Pha B'),
        patches.Patch(facecolor='blue', label='Pha C'),
        patches.ArrowPatch((0,0), (0,1), arrowstyle="->", color='black', label='Dòng đi VÀO (+)'),
        patches.ArrowPatch((0,1), (0,0), arrowstyle="<-", color='black', label='Dòng đi RA (-)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))

    plt.grid(True, axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()
    print("--- Đã vẽ xong biểu đồ. ---")
    plt.show()

# ==============================================================================
# CHẠY THỬ NGHIỆM (TEST CASE)
# ==============================================================================

# --- Trường hợp 1: Động cơ dọc trục điển hình (Dây quấn tập trung) ---
# 12 rãnh, 10 cực (p=5), 3 pha, 2 lớp dây (Double Layer Concentrated)
# Đây là cấu hình rất phổ biến cho mô-men xoắn cao.
plot_winding_layout(Zs=12, p=5, qs=3, Nlayer=2)

# --- Trường hợp 2: Dây quấn tập trung đơn giản nhất (Single Layer) ---
# 6 rãnh, 4 cực (p=2), 3 pha, 1 lớp dây. 
# Mỗi rãnh chỉ chứa 1 cạnh cuộn dây.
# plot_winding_layout(Zs=6, p=2, qs=3, Nlayer=1)

# --- Trường hợp 3: Dây quấn rải (Distributed Winding) ---
# 24 rãnh, 4 cực (p=2), 3 pha, 1 lớp.
# q = Zs / (2p * m) = 24 / (4 * 3) = 2 (số rãnh trên mỗi cực trên mỗi pha là số nguyên)
# plot_winding_layout(Zs=24, p=2, qs=3, Nlayer=1)