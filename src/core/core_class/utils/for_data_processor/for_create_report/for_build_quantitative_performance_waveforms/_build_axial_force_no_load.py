from reportlab.platypus import Paragraph, Table, Spacer

def _create_metrics_table(metrics_data, unit, config):
    rows = [
        [Paragraph("<b>Waveform Property</b>", config.table_header),
         Paragraph("<b>MBGRN Solver</b>", config.table_header),
         Paragraph("<b>FEM Reference</b>", config.table_header),
         Paragraph("<b>Discrepancy Error</b>", config.table_header)],
        [Paragraph("Peak / Maximum Value", config.table_text), Paragraph(f"{metrics_data['mbgrn_max']} {unit}", config.table_text), Paragraph(f"{metrics_data['fem_max']} {unit}", config.table_text), Paragraph(metrics_data['error_max'], config.table_text)],
        [Paragraph("Root-Mean-Square (RMS)", config.table_text), Paragraph(f"{metrics_data['mbgrn_rms']} {unit}", config.table_text), Paragraph(f"{metrics_data['fem_rms']} {unit}", config.table_text), Paragraph(metrics_data['error_rms'], config.table_text)],
        [Paragraph("Integral Mean / DC Component", config.table_text), Paragraph(f"{metrics_data['mbgrn_mean']} {unit}", config.table_text), Paragraph(f"{metrics_data['fem_mean']} {unit}", config.table_text), Paragraph(metrics_data['error_mean'], config.table_text)],
        [Paragraph("Peak-to-Peak Amplitude", config.table_text), Paragraph(f"{metrics_data['mbgrn_amp']} {unit}", config.table_text), Paragraph(f"{metrics_data['fem_amp']} {unit}", config.table_text), Paragraph("Analytical Scale", config.table_text)]
    ]
    t = Table(rows, colWidths=[184, 110, 110, 100])
    t.setStyle(config.base_table_style)
    return t

def _create_harmonic_table(h_mrn, h_fem, config, target_orders=[1, 3, 5, 7]):
    rows = [
        [Paragraph("<b>Harmonic Order</b>", config.table_header),
         Paragraph("<b>MBGRN Amp (N)</b>", config.table_header),
         Paragraph("<b>FEM Amp (N)</b>", config.table_header),
         Paragraph("<b>Relative Error</b>", config.table_header)]
    ]
    
    for order in target_orders:
        amp_mrn = 0.0
        amp_fem = 0.0
        
        if h_mrn is not None and h_mrn.shape[1] > order:
            amp_mrn = h_mrn[0, order]
        if h_fem is not None and h_fem.shape[1] > order:
            amp_fem = h_fem[0, order]
            
        error_str = "0.00%"
        if amp_fem != 0:
            error_val = abs(amp_mrn - amp_fem) / amp_fem * 100
            error_str = f"{error_val:.2f}%"
        elif amp_mrn != 0:
            error_str = "100.00%"
            
        rows.append([
            Paragraph(f"Harmonic Order #{order}", config.table_text),
            Paragraph(f"{amp_mrn:.4f}", config.table_text),
            Paragraph(f"{amp_fem:.4f}", config.table_text),
            Paragraph(error_str, config.table_text)
        ])
        
    t = Table(rows, colWidths=[154, 120, 110, 120])
    t.setStyle(config.base_table_style)
    return t

def _build_axial_force_no_load(story, motor, config):
    story.append(Paragraph("5.7 Axial Force Transient Waveforms (Open-Circuit No-Load Component)", config.h2_style))
    
    from ...for_update_report.update_axial_force_no_load_data import update_axial_force_no_load_data
    from .._fig_to_image_flowable import _fig_to_image_flowable
    
    fig_wave = motor.data_processor.plot_axial_force_no_load(plot=False)
    update_axial_force_no_load_data(data_processor=motor.data_processor)
    
    metrics = motor.record.flux_linkage_no_load_metrics if hasattr(motor.record, "axial_force_no_load_metrics") else None
    metrics = motor.record.axial_force_no_load_metrics
    
    if metrics is not None:
        story.append(Paragraph("<b>Axial Force Quantitative Verification Metrics</b>", config.body_style))
        story.append(_create_metrics_table(metrics, "N", config))
        story.append(Spacer(1, 14))
    
    h_mrn = motor.record.axial_force_no_load_harmonic if hasattr(motor.record, "axial_force_no_load_harmonic") else None
    h_fem = motor.record.axial_force_no_load_harmonic_fem if hasattr(motor.record, "axial_force_no_load_harmonic_fem") else None
    
    story.append(Paragraph("<b>Axial Force Spectrum Harmonics Verification</b>", config.body_style))
    story.append(_create_harmonic_table(h_mrn, h_fem, config, target_orders=[1, 3, 5, 7]))
    story.append(Spacer(1, 12))
    
    img_wave = _fig_to_image_flowable(fig_wave, width=450)
    if img_wave:
        story.append(img_wave)