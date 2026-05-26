import matplotlib.pyplot as plt
import scienceplots
from types import SimpleNamespace

def apply_journal_style():
    plt.style.use(['science', 'no-latex'])
    
    config = {
        'font.size': 20,
        'axes.titlesize': 30,
        'axes.labelsize': 25,
        'xtick.labelsize': 18,
        'ytick.labelsize': 18,
        'legend.fontsize': 18,
        'mathtext.fontset': 'stix',
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'axes.grid': True,
        'grid.linestyle': '-',
        'grid.linewidth': 0.005,
        'xtick.direction': 'in',
        'ytick.direction': 'in',
    }
    
    plt.rcParams.update(config)

    colors = [
        '#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#AA3377', '#BBBBBB',
        '#0072BD', '#D95319', '#EDB120', '#7E2F8E', '#77AC30', '#4DBEEE', '#A2142F'
    ]
    phase_colors = [colors[7], colors[8], colors[10]]
    markers = ['o', 's', '^', 'v', 'D', 'X']
    linestyles = ['-', '--', ':']

    # Đảm bảo trả về đầy đủ các thuộc tính mà các hàm plot đang yêu cầu
    return SimpleNamespace(
        colors=colors,
        phase_colors=phase_colors,
        markers=markers,
        linestyles=linestyles,
        font_size=config['font.size'],
        title_size=config['axes.titlesize'],
        label_size=config['axes.labelsize'],  
        tick_size=config['xtick.labelsize'],
        legend_size=config['legend.fontsize'],
        font_family=config['font.serif'][0],
        grid_linewidth=config['grid.linewidth']
    )