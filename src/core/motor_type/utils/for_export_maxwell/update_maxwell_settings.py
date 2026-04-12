import math
import numpy as np
import matplotlib.pyplot as plt

def update_maxwell_settings(motor):
    motor.require("mechanical")
    
    winding_data = motor.winding_data
    geometry_data = motor.geometry_data
    mechanical_data = motor.mechanical_data
    drive_data = motor.drive_data
    
    slot_number = geometry_data.stator.slot_number
    pole_number = geometry_data.rotor.pole_number
    pole_pairs = pole_number // 2
    
    slot_arc = 360.0 / slot_number
    pole_arc = 360.0 / pole_number
    delta_mech = slot_arc - (pole_arc / 2.0)
    delta_elec_rad = math.radians(delta_mech * pole_pairs)
    
    i_peak = drive_data.i_rms * math.sqrt(2)
    shaft_speed = getattr(mechanical_data, 'shaft_speed', 3000)
    omega_e = (shaft_speed * 2 * math.pi / 60) * pole_pairs
    beta_rad = math.radians(drive_data.phase_advanced)
    
    functions_m3d = []
    functions_rmxprt = []

    for k in range(int(winding_data.phase)):
        angle_shift = (2 * math.pi * k) / winding_data.phase
        
        # Logic current_function giu nguyen 100%
        phi_m3d = -angle_shift + beta_rad
        
        # current_function_for_rmxprt_export cham pha hon
        phi_rmxprt = phi_m3d - delta_elec_rad
        
        f_m3d = f"-{round(i_peak, 4)} * sin({round(omega_e, 4)} * Time + ({round(phi_m3d, 4)}))"
        f_rmxprt = f"-{round(i_peak, 4)} * sin({round(omega_e, 4)} * Time + ({round(phi_rmxprt, 4)}))"
        
        functions_m3d.append(f_m3d)
        functions_rmxprt.append(f_rmxprt)
        
    motor.maxwell_export_option.current_function = functions_m3d
    motor.maxwell_export_option.current_function_for_rmxprt_export = functions_rmxprt

    # Debug hien thi mau luc
    print("\033[92m" + "="*80)
    print(f"DEBUG: PHASE SYNC (RMxprt is {delta_mech:.3f} deg mech slower than M3D)")
    print("-" * 80)
    for i in range(len(functions_m3d)):
        print(f"Phase {i} | Maxwell 3D (Ref): {functions_m3d[i]}")
        print(f"Phase {i} | RMxprt (Delayed): {functions_rmxprt[i]}")
    print("=" * 80 + "\033[0m")

if __name__ == "__main__":
    from types import SimpleNamespace
    
    class MockMotor:
        def __init__(self):
            self.winding_data = SimpleNamespace(phase=3)
            self.geometry_data = SimpleNamespace(
                stator=SimpleNamespace(slot_number=15),
                rotor=SimpleNamespace(pole_number=10)
            )
            self.mechanical_data = SimpleNamespace(shaft_speed=3000)
            self.drive_data = SimpleNamespace(i_rms=20.0, phase_advanced=30.0)
            self.maxwell_export_option = SimpleNamespace(
                current_function=None,
                current_function_for_rmxprt_export=None
            )
        def require(self, name):
            pass

    motor_test = MockMotor()
    update_maxwell_settings(motor_test)
    
    # Logic plot kiem tra
    p = motor_test.geometry_data.rotor.pole_number // 2
    i_peak = motor_test.drive_data.i_rms * math.sqrt(2)
    omega_e = (motor_test.mechanical_data.shaft_speed * 2 * math.pi / 60) * p
    
    slot_arc = 360.0 / motor_test.geometry_data.stator.slot_number
    pole_arc = 360.0 / motor_test.geometry_data.rotor.pole_number
    delta_elec_rad = math.radians((slot_arc - pole_arc/2) * p)
    
    t_plot = np.linspace(0, (2 * math.pi / omega_e), 1000)
    plt.figure(figsize=(12, 6))
    colors = ['r', 'g', 'b']
    
    for k in range(3):
        angle_shift = (2 * math.pi * k) / 3
        beta_rad = math.radians(motor_test.drive_data.phase_advanced)
        
        phi_m3d = -angle_shift + beta_rad
        phi_rmxprt = phi_m3d - delta_elec_rad
        
        y_m3d = -i_peak * np.sin(omega_e * t_plot + phi_m3d)
        y_rmxprt = -i_peak * np.sin(omega_e * t_plot + phi_rmxprt)
        
        plt.plot(t_plot * 1000, y_m3d, color=colors[k], linestyle='-', label=f'M3D Ph{k}' if k==0 else "")
        plt.plot(t_plot * 1000, y_rmxprt, color=colors[k], linestyle='--', alpha=0.5, label=f'RMxprt Ph{k}' if k==0 else "")

    plt.title("Current Comparison: RMxprt (Delayed) vs Maxwell 3D (Reference)")
    plt.xlabel("Time (ms)")
    plt.ylabel("Current (A)")
    plt.legend()
    plt.grid(True)
    plt.show()