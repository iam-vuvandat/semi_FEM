def continuous_permeability(iron):
    """
    Khôi phục đường cong B-H về trạng thái liên tục từ bản sao lưu.
    Giúp tinh chỉnh nghiệm đạt độ chính xác cao sau khi đã ổn định bằng bậc thang.
    """
    if iron.backup_B_H_curve is not None:
        iron.B_H_curve["B_data"] = iron.backup_B_H_curve["B_data"].copy()
        iron.B_H_curve["H_data"] = iron.backup_B_H_curve["H_data"].copy()
