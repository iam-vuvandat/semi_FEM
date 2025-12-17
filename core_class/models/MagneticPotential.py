from dataclasses import dataclass
import numpy as np
from typing import Tuple

@dataclass
class Output:
    value: float
    valid: bool
    index: int  # Sửa từ float thành int

@dataclass
class Output2:
    three_dimension_index: Tuple[int, int, int]

class MagneticPotential:
    def __init__(self, data=None, periodic_boundary=True):
        self.data = data
        self.periodic_boundary = periodic_boundary

    def retrieve(self, position):
        i, j, k = position
        nr, nt, nz = self.data.shape

        # Kiểm tra biên cho chiều r (i) và z (k)
        if not (0 <= i < nr and 0 <= k < nz):
            return Output(value=0.0, valid=False, index=-1)

        # Xử lý biên chu kỳ cho chiều t (j)
        if self.periodic_boundary:
            j = j % nt
        elif not (0 <= j < nt):
            return Output(value=0.0, valid=False, index=-1)

        value = self.data[i, j, k]
        
        # SỬA LỖI: Công thức chuẩn cho Fortran Order (F)
        # i là chiều biến thiên nhanh nhất, sau đó đến j, rồi đến k
        flat_index = i + (j * nr) + (k * nr * nt)
        
        return Output(value=value.item(), valid=True, index=flat_index)
    
    def get_3D_index(self, position):
        nr, nt, nz = self.data.shape
        
        # Logic này đúng với Fortran Order, khớp với công thức sửa ở trên
        i = position % nr    
        position = position // nr
        j = position % nt  
        k = position // nt 
        
        return Output2(three_dimension_index=(i, j, k))

if __name__ == "__main__":
    # Tạo dữ liệu ngẫu nhiên với thứ tự F (Fortran)
    data = np.array(np.random.random((2, 3, 4)), order='F')
    
    magnetic_potential = MagneticPotential(data=data, periodic_boundary=True)
    
    # Test thử một điểm
    test_pos = (1, 2, 3) # (i=1, j=2, k=3)
    
    # Lấy index phẳng từ hàm retrieve
    output1 = magnetic_potential.retrieve(test_pos)
    print(f"Giá trị tại {test_pos}: {output1.value:.4f}")
    print(f"Flat Index tính được: {output1.index}")
    
    # Kiểm tra ngược lại bằng get_3D_index
    output2 = magnetic_potential.get_3D_index(output1.index)
    print(f"Tọa độ khôi phục từ index: {output2.three_dimension_index}")
    
    # Kiểm chứng sự nhất quán
    assert output2.three_dimension_index == test_pos, "Lỗi: Index đi và về không khớp!"
    print(">> Kiểm tra Logic thành công!")