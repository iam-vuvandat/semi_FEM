import os
import paths
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate

from .for_create_report._report_config import ReportConfig
from .for_create_report._create_header_section import _create_header_section
from .for_create_report._build_section_1 import _build_section_1
from .for_create_report._build_section_2 import _build_section_2
from .for_create_report._build_section_3 import _build_section_3
from .for_create_report._build_section_4 import _build_section_4
from .for_create_report._build_section_5 import _build_section_5
from .for_create_report._build_computational_performance import _build_computational_performance

def create_report(data_processor):
    """
    Generates a comprehensive electrical machine simulation report containing
    motor specifications, geometric data, winding layouts, and analysis graphs.
    """

    # update_record
    data_processor.update_record()
    root_dir = paths.configure_path()
    report_dir = os.path.join(root_dir, "data", "repo", "report")
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
        
    filename = os.path.join(report_dir, "Motor_Simulation_Report.pdf")

    motor = data_processor.motor
    record = motor.record

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    config = ReportConfig()
    story = []

    _create_header_section(story, config)
    _build_section_1(story, motor, config)
    _build_section_2(story, motor, config)
    _build_section_3(story, motor, config)
    _build_section_4(story, record, config)
    _build_section_5(story, data_processor, config)
    _build_computational_performance(story, data_processor, config)

    doc.build(story)
    return filename