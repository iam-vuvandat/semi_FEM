import matplotlib.pyplot as plt
import numpy as np

# Giả sử bạn có mảng tọa độ tâm các phần tử
X = [1, 2, 3, 4] 
Y = [1, 1, 1, 1]

# Và mảng giá trị Bx, By tương ứng tại các phần tử đó
Bx = [0.1, 0.2, 0.1, -0.1]
By = [0.0, 0.1, 0.2, 0.5]

fig, ax = plt.subplots()

# Vẽ mũi tên
# scale: điều chỉnh độ dài mũi tên (càng lớn mũi tên càng ngắn lại)
# width: độ dày thân mũi tên
ax.quiver(X, Y, Bx, By, color='blue', scale=1, width=0.005)

plt.show()