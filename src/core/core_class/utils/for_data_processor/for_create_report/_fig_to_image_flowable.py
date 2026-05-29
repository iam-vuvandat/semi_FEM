import io
import matplotlib.pyplot as plt
from reportlab.platypus import Image

def _fig_to_image_flowable(fig, width=480, height=None):
    """Converts a Matplotlib figure into a ReportLab Image Flowable with aspect ratio protection."""
    if fig is None:
        return None
    
    fig_w, fig_h = fig.get_size_inches()
    aspect_ratio = fig_h / fig_w
    
    if height is None:
        height = width * aspect_ratio
    
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png', dpi=300)
    img_buf.seek(0)
    plt.close(fig)
    
    return Image(img_buf, width=width, height=height)