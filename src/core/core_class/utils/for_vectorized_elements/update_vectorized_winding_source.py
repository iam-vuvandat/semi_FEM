import numpy as np

def update_vectorized_winding_source(vectorized_elements):
    current = vectorized_elements.winding_current
    winding_vector = vectorized_elements.element_winding_vector
    
    # Su dung np.dot de tinh tong MMF (F) cho tat ca phan tu cung luc
    # Day la phep nhan vo huong (dot product), khong phai tich co huong (cross product)
    F = np.dot(current, winding_vector)
    
    # Khoi tao mang nguon 6 huong (r-in, t-left, z-bot, r-out, t-right, z-top)
    winding_source = np.zeros_like(vectorized_elements.winding_source)
    
    # Gan truc tiep vao huong z (index 2 la z-bot, index 5 la z-top)
    # Tuong ung voi logic F/2 trong ham find_winding_source cua ban
    winding_source[2, :] = F / 2
    winding_source[5, :] = F / 2
    
    vectorized_elements.winding_source = winding_source