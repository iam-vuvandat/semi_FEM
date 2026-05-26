import io
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_complex_math_pdf(filename="complex_math_report.pdf"):
    # 1. Define your complex mathematical formula using standard LaTeX syntax
    # (Example: A Fourier series expansion or matrix transformation)
    complex_formula = r"f(x) = a_0 + \sum_{n=1}^{\infty} \left( a_n \cos\frac{n\pi x}{L} + b_n \sin\frac{n\pi x}{L} \right)"
    
    # Create a clean figure with no background axes
    fig = plt.figure(figsize=(5, 0.8), dpi=300)
    plt.text(0.5, 0.5, f"${complex_formula}$", size=12, ha="center", va="center")
    plt.axis("off")
    
    # Save the rendered equation directly to an in-memory binary stream
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight', pad_inches=0.02, transparent=True)
    img_buf.seek(0)
    plt.close(fig)

    # 2. Build the ReportLab flowable pipeline
    doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=54, rightMargin=54)
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], spaceAfter=12, fontSize=10, leading=14)
    
    story = []
    story.append(Paragraph("<b>Section 1.1: Analytical Approximation</b>", styles['Heading3']))
    story.append(Paragraph(
        "The spatial distribution of the magnetic fields can be represented by resolving "
        "the boundary conditions into a standard Fourier series expansion:", body_style
    ))
    story.append(Spacer(1, 5))
    
    # 3. Add the rendered equation block into your PDF story
    # Adjust width/height in points to keep the image crisp and proportional
    equation_flowable = Image(img_buf, width=320, height=51)
    story.append(equation_flowable)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Where coefficients are evaluated across the airgap region.", body_style))
    
    # Compile the final document
    doc.build(story)
    img_buf.close()

if __name__ == "__main__":
    generate_complex_math_pdf()