from reportlab.platypus import Paragraph, Spacer, Table

def _build_section_1(story, motor, config):
    """Generates Section 1: General Specifications & Materials."""
    story.append(Paragraph("1. General Specifications & Materials", config.h1_style))
    
    speed_val = f"{motor.mechanical_data.shaft_speed} RPM" if hasattr(motor, 'mechanical_data') else "N/A"
    i_rms_val = f"{motor.drive_data.i_rms} A" if hasattr(motor, 'drive_data') else "N/A"
    adv_ang = f"{motor.drive_data.phase_advanced}°" if hasattr(motor, 'drive_data') else "N/A"

    spec_data = [
        [Paragraph("<b>Parameter Description</b>", config.table_header), Paragraph("<b>Value / Assignment</b>", config.table_header)],
        [Paragraph("Machine Topology Classification", config.table_text), Paragraph(str(motor.motor_type), config.table_text)],
        [Paragraph("Operational Shaft Rotor Speed", config.table_text), Paragraph(str(speed_val), config.table_text)],
        [Paragraph("Stator Winding Excitation (I RMS)", config.table_text), Paragraph(str(i_rms_val), config.table_text)],
        [Paragraph("Current Advance Angle", config.table_text), Paragraph(str(adv_ang), config.table_text)],
        [Paragraph("Core Stator Iron Material", config.table_text), Paragraph(str(motor.material_data.iron_type), config.table_text)],
        [Paragraph("Rotor Permanent Magnet Grade", config.table_text), Paragraph(str(motor.material_data.magnet_type), config.table_text)]
    ]
    
    t_spec = Table(spec_data, colWidths=[250, 254])
    t_spec.setStyle(config.base_table_style)
    story.append(t_spec)
    story.append(Spacer(1, 12))