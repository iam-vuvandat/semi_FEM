from reportlab.platypus import Paragraph, PageBreak
from .for_build_quantitative_performance_waveforms._build_airgap_flux_no_load import _build_airgap_flux_no_load
from .for_build_quantitative_performance_waveforms._build_airgap_flux import _build_airgap_flux
from .for_build_quantitative_performance_waveforms._build_back_emf_no_load import _build_back_emf_no_load
from .for_build_quantitative_performance_waveforms._build_back_emf import _build_back_emf
from .for_build_quantitative_performance_waveforms._build_flux_linkage_no_load import _build_flux_linkage_no_load
from .for_build_quantitative_performance_waveforms._build_flux_linkage import _build_flux_linkage
from .for_build_quantitative_performance_waveforms._build_torque import _build_torque
from .for_build_quantitative_performance_waveforms._build_cogging_torque import _build_cogging_torque
from .for_build_quantitative_performance_waveforms._build_axial_force_no_load import _build_axial_force_no_load
from .for_build_quantitative_performance_waveforms._build_axial_force import _build_axial_force

def _build_section_5(story, motor, config):
    story.append(Paragraph("5. Quantitative Performance Waveforms", config.h1_style))
    
    _build_airgap_flux_no_load(story, motor, config)
    story.append(PageBreak())
    
    _build_airgap_flux(story, motor, config)
    story.append(PageBreak())
    
    _build_back_emf_no_load(story, motor, config)
    story.append(PageBreak())
    
    _build_back_emf(story, motor, config)
    story.append(PageBreak())
    
    _build_flux_linkage_no_load(story, motor, config)
    story.append(PageBreak())
    
    _build_flux_linkage(story, motor, config)
    story.append(PageBreak())
    
    _build_torque(story, motor, config)
    story.append(PageBreak())
    
    _build_cogging_torque(story, motor, config)
    story.append(PageBreak())
    
    _build_axial_force_no_load(story, motor, config)
    story.append(PageBreak())
    
    _build_axial_force(story, motor, config)