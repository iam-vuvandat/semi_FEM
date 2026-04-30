import numpy as np
import sys
from collections import deque

def measure_memory(obj, seen=None):
    """
    Hàm đo dung lượng bộ nhớ cho đối tượng phức tạp.
    Tự động đệ quy vào các thuộc tính con và xử lý tham chiếu vòng.
    """
    # Khởi tạo tập hợp ghi nhớ ở lần gọi đầu tiên
    if seen is None:
        seen = set()
    
    obj_id = id(obj)
    # Nếu đối tượng đã được đếm rồi thì bỏ qua để tránh lặp vô hạn hoặc đếm trùng
    if obj_id in seen:
        return 0
    seen.add(obj_id)

    total_bytes = sys.getsizeof(obj)
    
    # 1. Xử lý mảng NumPy (Dữ liệu nặng nhất trong tính toán máy điện)
    if isinstance(obj, np.ndarray):
        return obj.nbytes
    
    # 2. Xử lý Dictionary (bao gồm cả __dict__ của class)
    if isinstance(obj, dict):
        total_bytes += sum(measure_memory(v, seen) for v in obj.values())
        total_bytes += sum(measure_memory(k, seen) for k in obj.keys())
        
    # 3. Xử lý List, Tuple, Set
    elif isinstance(obj, (list, tuple, set, deque)):
        total_bytes += sum(measure_memory(i, seen) for i in obj)
        
    # 4. Xử lý Class Instance (như motor, mesh, solver...)
    elif hasattr(obj, '__dict__'):
        total_bytes += measure_memory(obj.__dict__, seen)
        
    # 5. Xử lý Class sử dụng __slots__ (tối ưu hóa bộ nhớ)
    elif hasattr(obj, '__slots__'):
        slot_attrs = [getattr(obj, s) for s in obj.__slots__ if hasattr(obj, s)]
        total_bytes += sum(measure_memory(attr, seen) for attr in slot_attrs)

    # Chỉ in kết quả ở lần gọi gốc (root call)
    if len(seen) <= 1:
        obj_name = obj.__class__.__name__
        memory_mb = total_bytes / (1024 * 1024)
        print(f"\033[92m[Memory Check] {obj_name}: {memory_mb:.4f} MB\033[0m")
        return memory_mb
        
    return total_bytes

# --- CÁCH SỬ DỤNG ---
# Bạn chỉ cần truyền đối tượng cần đo vào, không cần truyền seen:
# total_ram = measure_memory(motor)