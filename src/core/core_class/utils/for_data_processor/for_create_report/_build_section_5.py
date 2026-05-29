from reportlab.platypus import Paragraph, Spacer, PageBreak
from ._fig_to_image_flowable import _fig_to_image_flowable

def _build_section_5(story, data_processor, config):
    """Generates Section 5: Quantitative Performance Waveforms (Plots)."""
    story.append(Paragraph("5. Quantitative Performance Waveforms", config.h1_style))
    
    # 5.1 Output Torque
    story.append(Paragraph("5.1 Output Electromagnetic Torque Ripple", config.h2_style))
    fig_torque = data_processor.plot_torque(plot=False)
    img_torque = _fig_to_image_flowable(fig_torque, width=450)
    if img_torque:
        story.append(img_torque)
        story.append(Spacer(1, 10))

    # 5.2 Cogging Torque
    story.append(Paragraph("5.2 Standalone Open-Circuit Cogging Torque Profile", config.h2_style))
    fig_cogging = data_processor.plot_cogging_torque(plot=False)
    img_cogging = _fig_to_image_flowable(fig_cogging, width=450)
    if img_cogging:
        story.append(img_cogging)

    story.append(PageBreak())

    # 5.3 Flux Linkage
    story.append(Paragraph("5.3 Core Winding Flux Linkage Transient Waveforms", config.h2_style))
    fig_flux_wave, fig_flux_harm = data_processor.plot_flux_linkage(plot=False)
    img_flux_wave = _fig_to_image_flowable(fig_flux_wave, width=450)
    if img_flux_wave:
        story.append(img_flux_wave)
        story.append(Spacer(1, 8))
        
    img_flux_harm = _fig_to_image_flowable(fig_flux_harm, width=450)
    if img_flux_harm:
        story.append(img_flux_harm)

    story.append(PageBreak())

    # 5.4 Back EMF
    story.append(Paragraph("5.4 Phase Inductive Back Electromotive Force (EMF)", config.h2_style))
    fig_emf_wave, fig_emf_harm = data_processor.plot_back_emf(plot=False)
    img_emf_wave = _fig_to_image_flowable(fig_emf_wave, width=450)
    if img_emf_wave:
        story.append(img_emf_wave)
        story.append(Spacer(1, 8))
        
    img_emf_harm = _fig_to_image_flowable(fig_emf_harm, width=450)
    if img_emf_harm:
        story.append(img_emf_harm)

    story.append(PageBreak())

    # 5.5 Loaded Airgap Flux Density
    story.append(Paragraph("5.5 Airgap Flux Density Spatial Distribution (On-Load Component)", config.h2_style))
    fig_bg_wave, fig_bg_harm = data_processor.plot_airgap_flux_density(plot=False)
    img_bg_wave = _fig_to_image_flowable(fig_bg_wave, width=450)
    if img_bg_wave:
        story.append(img_bg_wave)
        story.append(Spacer(1, 10))
        
    img_bg_harm = _fig_to_image_flowable(fig_bg_harm, width=450)
    if img_bg_harm:
        story.append(img_bg_harm)