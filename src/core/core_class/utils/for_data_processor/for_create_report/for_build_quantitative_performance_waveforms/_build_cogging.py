from reportlab.platypus import Paragraph, Table, Spacer
from .._fig_to_image_flowable import _fig_to_image_flowable

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

def _build_cogging(story, motor, config):
    story.append(Paragraph("5.4 Standalone Open-Circuit Cogging Torque Profile", config.h2_style))
    fig_cogging = motor.data_processor.plot_cogging_torque(plot=False)
    img_cogging = _fig_to_image_flowable(fig_cogging, width=450)
    if img_cogging:
        story.append(img_cogging)
        story.append(Spacer(1, 6))
        
    cogging_metrics = motor.record.cogging_metrics
    story.append(_create_metrics_table(cogging_metrics, "Nm", config))