import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Output:
    """
    Cấu trúc dữ liệu đầu ra cho tính toán Cogging Torque.
    - period_mech: Chu kỳ cơ khí tính bằng Radian (rad).
    """
    period_mech: float

def find_cogging_period(motor) -> Output:
    """
    Tính toán chu kỳ cơ khí của mô-men răng khía theo đơn vị Radian.
    
    Công thức:
    T_rad = 2 * pi / LCM(slots, poles)
    """
    slots = motor.geometry_data.stator.slot_number
    poles = motor.geometry_data.rotor.pole_number
    if slots <= 0 or poles <= 0:
        raise ValueError("Số rãnh (slots) và số cực (poles) phải là số nguyên dương.")

    # 1. Tính số xung cogging mỗi vòng quay cơ khí (Bội số chung nhỏ nhất)
    n_cog = math.lcm(slots, poles)
    
    # 2. Tính chu kỳ cơ khí theo Radian
    # Một vòng quay hoàn chỉnh là 2 * pi rad
    t_cog_rad = (2 * math.pi) / n_cog
    
    return Output(period_mech=t_cog_rad)

# --- Kiểm tra nhanh ---
if __name__ == "__main__":
    # Ví dụ: Động cơ 12 rãnh, 10 cực -> LCM = 60
    # Chu kỳ = 2 * pi / 60 = pi / 30 rad (~0.1047 rad)
    result = calculate_cogging_period(12, 10)
    print(f"Chu kỳ cơ khí: {result.period_mech:.6f} rad")