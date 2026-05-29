from reportlab.platypus import Paragraph, Spacer, Table

def _build_section_2(story, motor, config):
    """Generates Section 2: Machine Core Geometry Parameters."""
    story.append(Paragraph("2. Machine Core Geometry Parameters", config.h1_style))
    
    geo_stator = motor.geometry_data.stator
    geo_rotor = motor.geometry_data.rotor

    geometry_rows = [
        [Paragraph("<b>Geometric Attribute (Stator)</b>", config.table_header), Paragraph("<b>Value</b>", config.table_header),
         Paragraph("<b>Geometric Attribute (Rotor)</b>", config.table_header), Paragraph("<b>Value</b>", config.table_header)],
        
        [Paragraph("Stator Armature Outer Diameter", config.table_text), Paragraph(f"{geo_stator.stator_lam_dia * 1e3:.1f} mm", config.table_text),
         Paragraph("Rotor Outer Diameter", config.table_text), Paragraph(f"{geo_rotor.rotor_lam_dia * 1e3:.1f} mm", config.table_text)],
        
        [Paragraph("Stator Bore Internal Diameter", config.table_text), Paragraph(f"{geo_stator.stator_bore_dia * 1e3:.1f} mm", config.table_text),
         Paragraph("Main Operational Airgap Length", config.table_text), Paragraph(f"{geo_rotor.airgap * 1e3:.2f} mm", config.table_text)],
        
        [Paragraph("Total Slots Count", config.table_text), Paragraph(str(geo_stator.slot_number), config.table_text),
         Paragraph("Total Pole Count", config.table_text), Paragraph(str(geo_rotor.pole_number), config.table_text)],
        
        [Paragraph("Armature Slot Width / Depth", config.table_text), Paragraph(f"{geo_stator.slot_width*1e3:.1f} / {geo_stator.slot_depth*1e3:.1f} mm", config.table_text),
         Paragraph("Permanent Magnet Arc", config.table_text), Paragraph(f"{geo_rotor.magnet_arc}° mechanical", config.table_text)],
        
        [Paragraph("Slot Opening Width", config.table_text), Paragraph(f"{geo_stator.slot_opening * 1e3:.1f} mm", config.table_text),
         Paragraph("Permanent Magnet Axial Length", config.table_text), Paragraph(f"{geo_rotor.magnet_length * 1e3:.1f} mm", config.table_text)],
         
        [Paragraph("Active Axial Stator Core Length", config.table_text), Paragraph(f"{geo_stator.stator_length * 1e3:.1f} mm", config.table_text),
         Paragraph("Rotor Yoke Structural Backing Length", config.table_text), Paragraph(f"{geo_rotor.rotor_length * 1e3:.1f} mm", config.table_text)]
    ]

    t_geo = Table(geometry_rows, colWidths=[160, 92, 160, 92])
    t_geo.setStyle(config.base_table_style)
    story.append(t_geo)
    story.append(Spacer(1, 12))