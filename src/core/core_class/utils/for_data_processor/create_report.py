import io
import os
import paths
import numpy as np
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def _fig_to_image_flowable(fig, width=480, height=280):
    """
    Helper function to convert a Matplotlib figure object into a 
    ReportLab Flowable Image using an in-memory binary stream.
    """
    if fig is None:
        return None
    
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=300)
    img_buf.seek(0)
    plt.close(fig)  # Clear memory allocations
    
    return Image(img_buf, width=width, height=height)

def create_report(data_processor):
    """
    Generates a comprehensive electrical machine simulation report containing
    motor specifications, geometric data, winding layouts, and analysis graphs.
    """
    # Configure path destinations
    root_dir = paths.configure_path()
    report_dir = os.path.join(root_dir, "data", "repo", "report")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        
    filename = os.path.join(report_dir, "Motor_Simulation_Report.pdf")

    motor = data_processor.motor
    record = motor.record

    # 1. Setup Document Layout Template
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,  # 0.75 in margins
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    # 2. Typography Styles (Muted Classic Palette)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=colors.HexColor('#1F4E79'), alignment=0, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSub', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=10, leading=14,
        textColor=colors.HexColor('#595959'), spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'SectionH1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor('#1F4E79'), spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SubSectionH2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=colors.HexColor('#B22222'), spaceBefore=10, spaceAfter=6, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'ReportBody', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5,
        textColor=colors.HexColor('#222222'), spaceAfter=6
    )
    table_text = ParagraphStyle(
        'TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=12
    )
    table_header = ParagraphStyle(
        'TableHeader', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=12,
        textColor=colors.HexColor('#1F4E79')
    )

    # Universal Table Styling Rule
    base_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F2F2F2')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FAFAFA')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.2, colors.HexColor('#1F4E79')),
    ])

    story = []

    # ==========================================
    # HEADER / TITLE SECTION
    # ==========================================
    story.append(Paragraph("Axial Flux Electrical Machine Design Report", title_style))
    story.append(Paragraph("Automated Design Summary Generated via Python Simulation Suite", subtitle_style))
    story.append(Spacer(1, 10))

    # ==========================================
    # SECTION 1: DESIGN SPECIFICATIONS & MATERIALS
    # ==========================================
    story.append(Paragraph("1. General Specifications & Materials", h1_style))
    
    speed_val = f"{motor.mechanical_data.shaft_speed} RPM" if hasattr(motor, 'mechanical_data') else "N/A"
    i_rms_val = f"{motor.drive_data.i_rms} A" if hasattr(motor, 'drive_data') else "N/A"
    adv_ang = f"{motor.drive_data.phase_advanced}°" if hasattr(motor, 'drive_data') else "N/A"

    spec_data = [
        [Paragraph("<b>Parameter Description</b>", table_header), Paragraph("<b>Value / Assignment</b>", table_header)],
        [Paragraph("Machine Topology Classification", table_text), Paragraph(str(motor.motor_type), table_text)],
        [Paragraph("Operational Shaft Rotor Speed", table_text), Paragraph(str(speed_val), table_text)],
        [Paragraph("Stator Winding Excitation (I RMS)", table_text), Paragraph(str(i_rms_val), table_text)],
        [Paragraph("Current Advance Angle", table_text), Paragraph(str(adv_ang), table_text)],
        [Paragraph("Core Stator Iron Material", table_text), Paragraph(str(motor.material_data.iron_type), table_text)],
        [Paragraph("Rotor Permanent Magnet Grade", table_text), Paragraph(str(motor.material_data.magnet_type), table_text)]
    ]
    
    t_spec = Table(spec_data, colWidths=[250, 254])
    t_spec.setStyle(base_table_style)
    story.append(t_spec)
    story.append(Spacer(1, 12))

    # ==========================================
    # SECTION 2: MOTOR GEOMETRY DATA
    # ==========================================
    story.append(Paragraph("2. Machine Core Geometry Parameters", h1_style))
    
    geo_stator = motor.geometry_data.stator
    geo_rotor = motor.geometry_data.rotor

    geometry_rows = [
        [Paragraph("<b>Geometric Attribute (Stator)</b>", table_header), Paragraph("<b>Value</b>", table_header),
         Paragraph("<b>Geometric Attribute (Rotor)</b>", table_header), Paragraph("<b>Value</b>", table_header)],
        
        [Paragraph("Stator Armature Outer Diameter", table_text), Paragraph(f"{geo_stator.stator_lam_dia * 1e3:.1f} mm", table_text),
         Paragraph("Rotor Outer Diameter", table_text), Paragraph(f"{geo_rotor.rotor_lam_dia * 1e3:.1f} mm", table_text)],
        
        [Paragraph("Stator Bore Internal Diameter", table_text), Paragraph(f"{geo_stator.stator_bore_dia * 1e3:.1f} mm", table_text),
         Paragraph("Main Operational Airgap Length", table_text), Paragraph(f"{geo_rotor.airgap * 1e3:.2f} mm", table_text)],
        
        [Paragraph("Total Slots Count", table_text), Paragraph(str(geo_stator.slot_number), table_text),
         Paragraph("Total Pole Count", table_text), Paragraph(str(geo_rotor.pole_number), table_text)],
        
        [Paragraph("Armature Slot Width / Depth", table_text), Paragraph(f"{geo_stator.slot_width*1e3:.1f} / {geo_stator.slot_depth*1e3:.1f} mm", table_text),
         Paragraph("Permanent Magnet Arc", table_text), Paragraph(f"{geo_rotor.magnet_arc}° mechanical", table_text)],
        
        [Paragraph("Slot Opening Width", table_text), Paragraph(f"{geo_stator.slot_opening * 1e3:.1f} mm", table_text),
         Paragraph("Permanent Magnet Axial Length", table_text), Paragraph(f"{geo_rotor.magnet_length * 1e3:.1f} mm", table_text)],
         
        [Paragraph("Active Axial Stator Core Length", table_text), Paragraph(f"{geo_stator.stator_length * 1e3:.1f} mm", table_text),
         Paragraph("Rotor Yoke Structural Backing Length", table_text), Paragraph(f"{geo_rotor.rotor_length * 1e3:.1f} mm", table_text)]
    ]

    t_geo = Table(geometry_rows, colWidths=[160, 92, 160, 92])
    t_geo.setStyle(base_table_style)
    story.append(t_geo)
    story.append(Spacer(1, 12))

    # ==========================================
    # SECTION 3: WINDING CONSTRAINTS & LAYOUT
    # ==========================================
    story.append(Paragraph("3. Armature Winding Configuration", h1_style))
    
    wdg = motor.winding_data
    wdg_rows = [
        [Paragraph("<b>Winding Specification</b>", table_header), Paragraph("<b>Configuration Setting</b>", table_header)],
        [Paragraph("Number of Phases ($m$)", table_text), Paragraph(str(wdg.phase), table_text)],
        [Paragraph("Total Series Turns Per Coil", table_text), Paragraph(str(wdg.turns), table_text)],
        [Paragraph("Coil Throw Interval (Slots)", table_text), Paragraph(str(wdg.throw), table_text)],
        [Paragraph("Winding Layer Assignment Count", table_text), Paragraph(str(wdg.winding_layer), table_text)],
        [Paragraph("Parallel Circuit Paths Count", table_text), Paragraph(str(wdg.parallel_path), table_text)]
    ]
    t_wdg = Table(wdg_rows, colWidths=[250, 254])
    t_wdg.setStyle(base_table_style)
    story.append(t_wdg)
    story.append(Spacer(1, 10))

    # Append Winding Layout Diagram if available in memory
    if hasattr(wdg, 'fig_layout') and wdg.fig_layout is not None:
        story.append(Paragraph("3.1 Armature Structural Coil Layout Matrix", h2_style))
        img_wdg = _fig_to_image_flowable(wdg.fig_layout, width=480, height=130)
        if img_wdg:
            story.append(img_wdg)

    story.append(PageBreak())

    # ==========================================
    # SECTION 4: SIMULATION SOLVER KPIS
    # ==========================================
    story.append(Paragraph("4. Performance Metrics Validation Summary", h1_style))
    story.append(Paragraph("Integral average values computed across a complete steady-state verification cycle:", body_style))
    
    mbgrn_pow = f"{record.average_mechanical_power:.2f} W" if hasattr(record, "average_mechanical_power") else "N/A"
    fem_pow = f"{record.average_mechanical_power_fem:.2f} W" if hasattr(record, "average_mechanical_power_fem") else "N/A"
    
    mbgrn_force = f"{np.mean(record.axial_force[0, :]):.2f} N" if hasattr(record, "axial_force") else "N/A"
    fem_force = f"{record.average_axial_force_fem:.2f} N" if hasattr(record, "average_axial_force_fem") else "N/A"

    kpi_rows = [
        [Paragraph("<b>Performance Metric Summary</b>", table_header), 
         Paragraph("<b>MBGRN Solver</b>", table_header), 
         Paragraph("<b>FEM Reference</b>", table_header)],
        [Paragraph("Average Mechanical Output Power", table_text), Paragraph(mbgrn_pow, table_text), Paragraph(fem_pow, table_text)],
        [Paragraph("Mean Static Axial Z-Force Load", table_text), Paragraph(mbgrn_force, table_text), Paragraph(fem_force, table_text)]
    ]
    t_kpi = Table(kpi_rows, colWidths=[204, 150, 150])
    t_kpi.setStyle(base_table_style)
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # ==========================================
    # SECTION 5: WAVEFORMS AND PLOT VISUALIZATIONS
    # ==========================================
    story.append(Paragraph("5. Quantitative Performance Waveforms", h1_style))
    
    # 5.1 Output Torque
    story.append(Paragraph("5.1 Output Electromagnetic Torque Ripple", h2_style))
    fig_torque = data_processor.plot_torque(plot=False)
    img_torque = _fig_to_image_flowable(fig_torque, width=450, height=220)
    if img_torque:
        story.append(img_torque)
        story.append(Spacer(1, 10))

    # 5.2 Cogging Torque
    story.append(Paragraph("5.2 Standalone Open-Circuit Cogging Torque Profile", h2_style))
    fig_cogging = data_processor.plot_cogging_torque(plot=False)
    img_cogging = _fig_to_image_flowable(fig_cogging, width=450, height=220)
    if img_cogging:
        story.append(img_cogging)

    story.append(PageBreak())

    # 5.3 Flux Linkage
    story.append(Paragraph("5.3 Core Winding Flux Linkage Transient Waveforms", h2_style))
    fig_flux_wave, fig_flux_harm = data_processor.plot_flux_linkage(plot=False)
    img_flux_wave = _fig_to_image_flowable(fig_flux_wave, width=450, height=220)
    if img_flux_wave:
        story.append(img_flux_wave)
        story.append(Spacer(1, 8))
        
    img_flux_harm = _fig_to_image_flowable(fig_flux_harm, width=450, height=220)
    if img_flux_harm:
        story.append(img_flux_harm)

    story.append(PageBreak())

    # 5.4 Back EMF
    story.append(Paragraph("5.4 Phase Inductive Back Electromotive Force (EMF)", h2_style))
    fig_emf_wave, fig_emf_harm = data_processor.plot_back_emf(plot=False)
    img_emf_wave = _fig_to_image_flowable(fig_emf_wave, width=450, height=220)
    if img_emf_wave:
        story.append(img_emf_wave)
        story.append(Spacer(1, 8))
        
    img_emf_harm = _fig_to_image_flowable(fig_emf_harm, width=450, height=220)
    if img_emf_harm:
        story.append(img_emf_harm)

    story.append(PageBreak())

    # 5.5 Loaded Airgap Flux Density
    story.append(Paragraph("5.5 Airgap Flux Density Spatial Distribution (On-Load Component)", h2_style))
    fig_bg_wave, fig_bg_harm = data_processor.plot_airgap_flux_density(plot=False)
    img_bg_wave = _fig_to_image_flowable(fig_bg_wave, width=450, height=220)
    if img_bg_wave:
        story.append(img_bg_wave)
        story.append(Spacer(1, 10))
        
    img_bg_harm = _fig_to_image_flowable(fig_bg_harm, width=450, height=440)  # Taller layout for stacked multi-axes graphs
    if img_bg_harm:
        story.append(img_bg_harm)

    # 6. Compile Document Pipeline
    doc.build(story)
    return filename