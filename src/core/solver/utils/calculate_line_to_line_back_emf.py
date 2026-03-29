import numpy as np
import matplotlib.pyplot as plt

def calculate_line_to_line_back_emf(data_numpy):
    n_phase = data_numpy.shape[0] - 1
    angle_row = data_numpy[-1, :]
    phase_emf = data_numpy[:-1, :]
    
    line_emf_list = []
    
    for i in range(n_phase):
        phase_current = phase_emf[i, :]
        phase_next = phase_emf[(i + 1) % n_phase, :]
        
        line_voltage = phase_current - phase_next
        line_emf_list.append(line_voltage)
    
    line_emf_array = np.vstack(line_emf_list)
    result = np.vstack((line_emf_array, angle_row))
    
    return result

if __name__ == "__main__":
    n = 3
    points = 500
    theta = np.linspace(0, 2 * np.pi, points)
    
    phase_a = 100 * np.sin(theta)
    phase_b = 100 * np.sin(theta - 2 * np.pi / 3)
    phase_c = 100 * np.sin(theta - 4 * np.pi / 3)
    
    test_data = np.vstack((phase_a, phase_b, phase_c, np.degrees(theta)))
    
    line_data = calculate_line_to_line_back_emf(test_data)
    
    plt.figure(figsize=(10, 6))
    
    for i in range(n):
        plt.plot(test_data[-1, :], test_data[i, :], '--', label=f'Phase EMF {i+1}')
    
    for i in range(n):
        plt.plot(line_data[-1, :], line_data[i, :], '-', linewidth=2, label=f'Line EMF {i+1}-{(i+1)%n + 1}')
    
    plt.grid(True)
    plt.legend()
    plt.xlabel('Angle [degree]')
    plt.ylabel('Voltage [V]')
    plt.title('Phase vs Line-to-Line Back EMF')
    plt.show()