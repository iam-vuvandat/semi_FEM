import numpy as np
import matplotlib.pyplot as plt

def function_nonlinear_load(load_step, order=2):
    x = np.linspace(0, 1, load_step + 1)[1:]
    return (1 - np.exp(-order * x)) / (1 - np.exp(-order))


def nonlinear_conjugate_gradient(reluctance_network,
                                 max_iteration=100,
                                 max_relative_residual=1e-4,
                                 load_step=10,
                                 line_search_max=8,
                                 debug=True):

    reluctance_network.set_reluctance_at_zero()
    magnetic_potential_shape = reluctance_network.magnetic_potential.data.shape

    load_queue = list(function_nonlinear_load(load_step, order=2))
    residual_history = []
    load_step_indices = []

    last_step_checkpoint = reluctance_network.magnetic_potential.data.copy()
    last_converged_load = 0.0

    GREEN, RED, WHITE, YELLOW, CYAN, RESET = \
        "\033[92m", "\033[91m", "\033[97m", "\033[93m", "\033[96m", "\033[0m"

    while load_queue:
        current_load = load_queue.pop(0)
        reluctance_network.magnetic_potential.data = last_step_checkpoint.copy()
        reluctance_network.update_reluctance_network(
            magnetic_potential=reluctance_network.magnetic_potential
        )

        comp = reluctance_network.create_magnetic_potential_equation(
            load_factor=current_load, debug=False
        )
        G, J = comp.G, comp.J
        norm_J = np.linalg.norm(J) + 1e-12

        x = reluctance_network.magnetic_potential.data.flatten(order='F')
        g = G.dot(x[:-1]) - J
        g_full = np.append(g, 0.0)
        d = -g_full

        converged_this_step = False

        for k in range(max_iteration):
            if k == 0:
                load_step_indices.append(len(residual_history))

            alpha = 1.0
            phi0 = np.linalg.norm(g) ** 2

            for _ in range(line_search_max):
                x_trial = x + alpha * d
                reluctance_network.magnetic_potential.data = \
                    x_trial.reshape(magnetic_potential_shape, order='F')
                reluctance_network.update_reluctance_network(
                    magnetic_potential=reluctance_network.magnetic_potential
                )

                comp_new = reluctance_network.create_magnetic_potential_equation(
                    load_factor=current_load, debug=False
                )
                g_new = comp_new.G.dot(x_trial[:-1]) - comp_new.J
                if np.linalg.norm(g_new) ** 2 <= phi0 * (1 - 1e-4 * alpha):
                    break
                alpha *= 0.5

            res_val = np.linalg.norm(g_new) / norm_J
            residual_history.append(res_val)

            if debug:
                color = WHITE if k == 0 else (GREEN if res_val < residual_history[-2] else RED)
                print(f"{color}Load {current_load:.4f}, Iter {k+1}: "
                      f"Alpha = {alpha:.3e}, Res = {res_val*100:.4f}%{RESET}")

            if res_val < max_relative_residual:
                last_step_checkpoint = \
                    x_trial.reshape(magnetic_potential_shape, order='F')
                last_converged_load = current_load
                converged_this_step = True
                break

            beta = max(
                np.dot(g_new, g_new - g) / (np.dot(g, g) + 1e-14),
                0.0
            )

            g = g_new
            g_full = np.append(g, 0.0)
            d = -g_full + beta * d
            if np.dot(d[:-1], g) >= 0:
                d = -g_full

            x = x_trial

        if not converged_this_step:
            mid_load = 0.5 * (last_converged_load + current_load)
            if abs(current_load - last_converged_load) > 1e-5:
                load_queue.insert(0, current_load)
                load_queue.insert(0, mid_load)
                if debug:
                    print(f"{YELLOW}[!!] Load {current_load:.4f} failed, "
                          f"sub-stepping to {mid_load:.4f}{RESET}")
            else:
                if debug:
                    print(f"{RED}[!!!] FATAL: convergence failed at "
                          f"{current_load:.4f}{RESET}")
                break

    reluctance_network.add_elements_lite()

    if debug and residual_history:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        ax.plot(residual_history, marker='o', markersize=2)
        for idx in load_step_indices:
            ax.axvline(x=idx, color='red', linestyle='--', alpha=0.15)
        ax.set_yscale('log')
        ax.set_xlabel("Total Iterations")
        ax.set_ylabel("Relative Residual")
        ax.set_title("3D MBGRN: Nonlinear Conjugate Gradient Convergence")
        ax.grid(True, which="both", alpha=0.2)
        plt.show()

    return reluctance_network.magnetic_potential.data
