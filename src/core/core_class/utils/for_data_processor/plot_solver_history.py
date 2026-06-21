import os
import paths
import numpy as np
import matplotlib.pyplot as plt

def plot_solver_history(data_processor, 
                        step_index = 0, 
                        plot_residual = True, 
                        plot_relaxation_factor = True, 
                        plot_relaxation_decay = True, 
                        plot = False,
                        plot_convergence_threshold = True):
    
    root_dir = paths.configure_path()
    figure_dir = os.path.join(root_dir, "data", "repo", "figures")
    if not os.path.exists(figure_dir):
        os.makedirs(figure_dir)

    record = data_processor.motor.record
    s = data_processor.plot_style

    max_relative_residual = data_processor.motor.calculation_data.convergence_settings.max_relative_residual
    convergence_threshold = max_relative_residual * 100

    if not hasattr(record, 'solver_history') or len(record.solver_history) == 0:
        print("\033[93mWarning: No solver history data found.\033[0m")
        return None
    
    if isinstance(step_index, (int, np.integer)):
        step_indices = [step_index]
    else:
        step_indices = list(step_index)
        
    requested_matrices = []
    fig_width = 14
    fig_height = fig_width / 1.618
    
    valid_indices = []
    for idx in step_indices:
        if idx >= len(record.solver_history) or idx < -len(record.solver_history):
            continue
        valid_indices.append(idx)
        requested_matrices.append(record.solver_history[idx])
        
    if len(requested_matrices) == 0:
        return None

    if plot_residual or plot_relaxation_factor or plot_relaxation_decay:
        fig = plt.figure(figsize=(fig_width, fig_height))
        ax1 = plt.gca()
        ax2 = None
        
        lines = []
        
        colors_res_pool = ['#1F4E79', '#2E75B6', '#BDD7EE', '#1F497D', '#002060']
        colors_relax_pool = ['#B22222', '#FF0000', '#FFC000', '#C00000', '#E2EFDA']
        colors_decay_pool = ['#595959', '#7F7F7F', '#A6A6A6', '#D9D9D9', '#262626']
        
        if not plot_residual:
            ax1.set_xlabel('Iteration', fontsize=s.label_size, color='k')
            ax1.tick_params(axis='x', labelcolor='k', colors='k', labelsize=s.legend_size)
            ax1.tick_params(axis='y', labelcolor='k', colors='k', labelsize=s.legend_size)
            ax1.grid(True, which="both", linestyle="-", linewidth=s.grid_linewidth)
            
        if (plot_relaxation_factor or plot_relaxation_decay) and (ax2 is None):
            ax2 = ax1.twinx()
            
            if plot_relaxation_factor and plot_relaxation_decay:
                y2_label = 'Material Relaxation & Decay Factor'
            elif plot_relaxation_factor:
                y2_label = 'Material Relaxation Factor'
            else:
                y2_label = 'Material Relaxation Decay Factor'
                
            ax2.set_ylabel(y2_label, fontsize=s.label_size, color='k')
            ax2.set_ylim(bottom=0)
            ax2.tick_params(axis='y', labelcolor='k', colors='k', labelsize=s.legend_size)
            
            ax2.spines['left'].set_color('k')
            ax2.spines['right'].set_color('k')
            ax2.spines['top'].set_color('k')
            ax2.spines['bottom'].set_color('k')

        for i, (idx, matrix) in enumerate(zip(valid_indices, requested_matrices)):
            iterations = matrix[:, 0]
            display_idx = idx if idx >= 0 else len(record.solver_history) + idx
            
            if plot_residual:
                residuals = matrix[:, 1] * 100
                color_res = colors_res_pool[i % len(colors_res_pool)]
                
                if i == 0:
                    ax1.set_xlabel('Iteration', fontsize=s.label_size, color='k')
                    ax1.set_ylabel('Relative Residual (%)', fontsize=s.label_size, color='k')
                    ax1.set_yscale('log')
                    ax1.tick_params(axis='y', labelcolor='k', colors='k', labelsize=s.legend_size)
                    ax1.tick_params(axis='x', labelcolor='k', colors='k', labelsize=s.legend_size)
                    ax1.grid(True, which="both", linestyle="-", linewidth=s.grid_linewidth)
                    
                    if plot_convergence_threshold and convergence_threshold is not None:
                        line_thresh = ax1.axhline(y=convergence_threshold, color='#FF0000', linestyle=':', linewidth=1.5, label='Conv. Threshold')
                        lines.append(line_thresh)
                    
                line1 = ax1.plot(iterations, residuals, marker='o', linestyle='-', color=color_res, linewidth=1.8, label=f'Res. Step {display_idx + 1}')
                lines.extend(line1)
                
            if plot_relaxation_factor:
                relax_factors = matrix[:, 2]
                color_relax = colors_relax_pool[i % len(colors_relax_pool)]
                line2 = ax2.plot(iterations, relax_factors, marker='s', linestyle='--', color=color_relax, linewidth=1.8, label=f'Relax Step {display_idx + 1}')
                lines.extend(line2)
                
            if plot_relaxation_decay:
                decays = matrix[:, 3]
                color_decay = colors_decay_pool[i % len(colors_decay_pool)]
                line3 = ax2.plot(iterations, decays, marker='^', linestyle=':', color=color_decay, linewidth=1.8, label=f'Decay Step {display_idx + 1}')
                lines.extend(line3)
                
        ax1.spines['left'].set_color('k')
        ax1.spines['right'].set_color('k')
        ax1.spines['top'].set_color('k')
        ax1.spines['bottom'].set_color('k')
        ax1.margins(x=0)
        
        if len(lines) > 0:
            labels = [l.get_label() for l in lines]
            ax1.legend(lines, labels, frameon=True, loc='upper right', fontsize=s.legend_size)
            
        plt.title('Solver Convergence & Relaxation Control History', fontsize=s.label_size)
        plt.tight_layout()
        
        steps_str = "_".join([str(x if x >= 0 else len(record.solver_history) + x + 1) for x in valid_indices])
        history_path = os.path.join(figure_dir, f"solver_history_steps_{steps_str}.png")
        fig.savefig(history_path, bbox_inches='tight', dpi=300)
        
        print("\033[94mIn function plot_solver_history: \033[0m")
        print("\033[94m{\033[0m")
        print(f"\033[94mSolver history plot has been saved to [{history_path}]\033[0m")
        print("\033[94m}\033[0m")
        print("\033[94m\033[0m")
        
        if plot:
            plt.show()
            
    if isinstance(step_index, (int, np.integer)):
        return requested_matrices[0] if len(requested_matrices) > 0 else None
    return requested_matrices