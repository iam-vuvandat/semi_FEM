import numpy as np

def find_relaxation_decay(solver):
    history = solver.convergence_settings.relaxation_history
    conv_set = solver.convergence_settings
    G_c, RESET = "\033[92m", "\033[0m"
    
    # 1. Kiem tra va thu cac gia tri trong bo ba trung tam (0.5, 0.4, 0.6)
    if history[1, 4] == 0:
        conv_set.relaxation_decay = history[0, 4]
        
    elif history[1, 3] == 0:
        conv_set.relaxation_decay = history[0, 3]
        
    elif history[1, 5] == 0:
        conv_set.relaxation_decay = history[0, 5]

    else:
        # 2. Xac dinh huong hoi tu sau khi da co du ket qua bo ba
        i3, i4, i5 = history[1, 3], history[1, 4], history[1, 5]

        if i5 < i4 and i5 <= i3:
            # Huong tot la TANG (0.6 -> 1.0)
            target_idx = 5
            for idx in range(6, 10):
                if history[1, idx] == 0:
                    target_idx = idx
                    break
                if history[1, idx] > history[1, idx - 1]:
                    target_idx = idx - 1
                    break
                target_idx = idx
            conv_set.relaxation_decay = history[0, target_idx]
            
        elif i3 < i4 and i3 <= i5:
            # Huong tot la GIAM (0.4 -> 0.1)
            target_idx = 3
            for idx in range(2, -1, -1):
                if history[1, idx] == 0:
                    target_idx = idx
                    break
                if history[1, idx] > history[1, idx + 1]:
                    target_idx = idx + 1
                    break
                target_idx = idx
            conv_set.relaxation_decay = history[0, target_idx]
            
        else:
            # 0.5 la diem toi uu nhat trong bo ba
            conv_set.relaxation_decay = history[0, 4]

    # Mac dinh in ra, khong phu thuoc vao bien debug
    print(f"{G_c}relaxation decay updated to {conv_set.relaxation_decay}{RESET}")