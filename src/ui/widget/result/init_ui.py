import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from PyQt5.QtWidgets import (QHBoxLayout, QVBoxLayout, QWidget, QFrame, 
                             QLabel, QCheckBox, QComboBox, QScrollArea, 
                             QTabWidget, QGroupBox, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

def init_ui(result_tab):
    if result_tab is None:
        return None

    main_win = result_tab.main_window
    motor = main_win.motor if main_win else None

    result_tab.tab_controllers = {}

    main_layout = QVBoxLayout(result_tab)
    main_layout.setContentsMargins(5, 5, 5, 5)
    main_layout.setSpacing(5)

    result_tab.sub_tabs = QTabWidget()
    main_layout.addWidget(result_tab.sub_tabs, 1)

    quantities_config = [
        {"key": "torque", "title": "Torque (On Load)", "has_fem": True, "has_harm": False, "has_phase": False, "has_dq": False},
        {"key": "cogging_torque", "title": "Cogging Torque", "has_fem": True, "has_harm": False, "has_phase": False, "has_dq": False},
        {"key": "mechanical_power", "title": "Mechanical Power", "has_fem": True, "has_harm": False, "has_phase": False, "has_dq": False},
        {"key": "back_emf", "title": "Back EMF (On Load)", "has_fem": True, "has_harm": True, "has_phase": True, "has_dq": False},
        {"key": "back_emf_no_load", "title": "Back EMF (No Load)", "has_fem": True, "has_harm": True, "has_phase": True, "has_dq": False},
        {"key": "flux_linkage", "title": "Flux Linkage (On Load)", "has_fem": True, "has_harm": True, "has_phase": True, "has_dq": True},
        {"key": "flux_linkage_no_load", "title": "Flux Linkage (No Load)", "has_fem": True, "has_harm": True, "has_phase": True, "has_dq": True},
        {"key": "airgap_flux_density", "title": "Airgap Flux Density (On Load)", "has_fem": True, "has_harm": True, "has_phase": False, "has_dq": False},
        {"key": "airgap_flux_density_no_load", "title": "Airgap Flux Density (No Load)", "has_fem": True, "has_harm": True, "has_phase": False, "has_dq": False},
        {"key": "axial_force", "title": "Axial Force (On Load)", "has_fem": True, "has_harm": False, "has_phase": False, "has_dq": False},
        {"key": "axial_force_no_load", "title": "Axial Force (No Load)", "has_fem": True, "has_harm": False, "has_phase": False, "has_dq": False},
        {"key": "current", "title": "Stator Currents", "has_fem": True, "has_harm": False, "has_phase": False, "has_dq": False}
    ]

    for config in quantities_config:
        tab_page = QWidget()
        page_layout = QVBoxLayout(tab_page)
        page_layout.setContentsMargins(5, 5, 5, 5)
        page_layout.setSpacing(5)

        opt_box = QGroupBox("Display Options")
        opt_layout = QHBoxLayout(opt_box)
        opt_layout.setContentsMargins(10, 5, 10, 5)
        opt_layout.setSpacing(15)

        label_axis = QLabel("Horizontal Axis:")
        combo_axis = QComboBox()
        combo_axis.addItem("Mechanical Position", "mechanical_position")
        combo_axis.addItem("Time", "time")
        opt_layout.addWidget(label_axis)
        opt_layout.addWidget(combo_axis)

        chk_fem = None
        if config["has_fem"]:
            chk_fem = QCheckBox("Show FEM")
            chk_fem.setChecked(True)
            opt_layout.addWidget(chk_fem)

        chk_harmonic = None
        if config["has_harm"]:
            chk_harmonic = QCheckBox("Calculate Harmonics")
            chk_harmonic.setChecked(True)
            opt_layout.addWidget(chk_harmonic)

        chk_all_phases = None
        if config["has_phase"]:
            chk_all_phases = QCheckBox("Show All Phases")
            chk_all_phases.setChecked(False)
            opt_layout.addWidget(chk_all_phases)

        chk_dq = None
        if config["has_dq"]:
            chk_dq = QCheckBox("Show dq Components")
            chk_dq.setChecked(False)
            opt_layout.addWidget(chk_dq)

        opt_layout.addStretch()
        page_layout.addWidget(opt_box, 0)

        view_container = QWidget()
        view_layout = QVBoxLayout(view_container)
        view_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(view_container, 1)

        result_tab.tab_controllers[config["key"]] = {
            "key": config["key"],
            "title": config["title"],
            "has_harm": config["has_harm"],
            "combo_axis": combo_axis,
            "chk_fem": chk_fem,
            "chk_harmonic": chk_harmonic,
            "chk_all_phases": chk_all_phases,
            "chk_dq": chk_dq,
            "view_layout": view_layout,
            "view_container": view_container,
            "figures": [],
            "canvases": []
        }

        result_tab.sub_tabs.addTab(tab_page, config["title"])

    bottom_bar = QFrame()
    bottom_bar.setFixedHeight(40)
    bottom_layout = QHBoxLayout(bottom_bar)
    bottom_layout.setContentsMargins(10, 2, 10, 2)
    bottom_layout.setSpacing(10)

    result_tab.status_label = QLabel("Status: Ready")
    bottom_layout.addWidget(result_tab.status_label)
    bottom_layout.addStretch()

    result_tab.btn_export_report = QPushButton("Export PDF Report")
    result_tab.btn_export_report.setFixedWidth(160)
    bottom_layout.addWidget(result_tab.btn_export_report)

    main_layout.addWidget(bottom_bar, 0)

    def handle_export_report():
        if not hasattr(motor, "data_processor") or motor.data_processor is None:
            QMessageBox.warning(result_tab, "Warning", "DataProcessor is not initialized.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            result_tab,
            "Export Simulation Report",
            "Motor_Simulation_Report.pdf",
            "PDF Files (*.pdf);;All Files (*)"
        )

        if not file_path:
            return

        try:
            result_tab.status_label.setText("Status: Generating PDF report...")
            saved_file = motor.data_processor.create_report(path=file_path)
            result_tab.status_label.setText(f"Status: Report saved to {os.path.basename(saved_file)}")
            QMessageBox.information(result_tab, "Success", f"Report successfully generated:\n{saved_file}")
        except Exception as e:
            result_tab.status_label.setText("Status: Error generating report")
            QMessageBox.critical(result_tab, "Error", f"Failed to generate report:\n{str(e)}")

    result_tab.btn_export_report.clicked.connect(handle_export_report)

    def clear_tab_plots(controller):
        for fig in controller["figures"]:
            if fig is not None:
                plt.close(fig)
        controller["figures"].clear()
        controller["canvases"].clear()

        layout = controller["view_layout"]
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def build_figure_view(fig, parent_widget):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setSpacing(5)

        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas, parent_widget)

        fig_box = QFrame()
        fig_box.setFrameShape(QFrame.StyledPanel)
        fig_box_layout = QVBoxLayout(fig_box)
        fig_box_layout.setContentsMargins(5, 5, 5, 5)
        fig_box_layout.addWidget(toolbar)
        fig_box_layout.addWidget(canvas)

        container_layout.addWidget(fig_box)
        container_layout.addStretch()
        scroll_area.setWidget(container)

        return scroll_area, canvas

    def render_tab_figures(controller, figures_dict):
        clear_tab_plots(controller)
        layout = controller["view_layout"]
        parent = controller["view_container"]

        valid_items = {k: v for k, v in figures_dict.items() if v is not None}

        if not valid_items:
            no_data_label = QLabel("No simulation data available for this quantity.\nPlease run calculation first.")
            no_data_label.setAlignment(Qt.AlignCenter)
            no_data_label.setStyleSheet("font-size: 13px; color: #666666;")
            layout.addWidget(no_data_label)
            return

        if len(valid_items) == 1:
            name, fig = next(iter(valid_items.items()))
            controller["figures"].append(fig)
            view_widget, canvas = build_figure_view(fig, parent)
            controller["canvases"].append(canvas)
            layout.addWidget(view_widget)
            canvas.draw()
        else:
            nested_tabs = QTabWidget()
            for name, fig in valid_items.items():
                controller["figures"].append(fig)
                tab_widget, canvas = build_figure_view(fig, nested_tabs)
                controller["canvases"].append(canvas)
                nested_tabs.addTab(tab_widget, name)
                canvas.draw()
            layout.addWidget(nested_tabs)

    def update_single_tab(key):
        if key not in result_tab.tab_controllers:
            return
        if not hasattr(motor, "data_processor") or motor.data_processor is None:
            return

        ctrl = result_tab.tab_controllers[key]
        dp = motor.data_processor
        record = getattr(motor, "record", None)

        h_axis = ctrl["combo_axis"].currentData()
        show_fem = ctrl["chk_fem"].isChecked() if ctrl["chk_fem"] else True
        show_harm = ctrl["chk_harmonic"].isChecked() if ctrl["chk_harmonic"] else True
        show_all_p = ctrl["chk_all_phases"].isChecked() if ctrl["chk_all_phases"] else False
        show_dq = ctrl["chk_dq"].isChecked() if ctrl["chk_dq"] else False
        square_figsize = (8, 8)

        figures_dict = {}

        try:
            if key == "torque":
                if record is not None and (getattr(record, "torque", None) is not None or getattr(record, "torque_fem", None) is not None):
                    fig = dp.plot_torque(horizontal_axis=h_axis, show_fem=show_fem, plot=False, figsize=square_figsize)
                    figures_dict["Waveform"] = fig
            elif key == "cogging_torque":
                if record is not None and (getattr(record, "cogging", None) is not None or getattr(record, "cogging_fem", None) is not None):
                    fig = dp.plot_cogging_torque(horizontal_axis=h_axis, show_fem=show_fem, plot=False, figsize=square_figsize)
                    figures_dict["Waveform"] = fig
            elif key == "mechanical_power":
                if record is not None and (getattr(record, "mechanical_power", None) is not None or getattr(record, "mechanical_power_fem", None) is not None):
                    fig = dp.plot_mechanical_power(horizontal_axis=h_axis, show_fem=show_fem, plot=False, figsize=square_figsize)
                    figures_dict["Waveform"] = fig
            elif key == "back_emf":
                if record is not None and (getattr(record, "back_emf", None) is not None or getattr(record, "back_emf_fem", None) is not None):
                    f_wave, f_harm = dp.plot_back_emf(
                        horizontal_axis=h_axis, show_fem=show_fem, 
                        show_all_phases=show_all_p, show_harmonic=show_harm, plot=False,
                        figsize=square_figsize
                    )
                    figures_dict["Waveform"] = f_wave
                    if show_harm and f_harm:
                        figures_dict["Harmonics"] = f_harm
            elif key == "back_emf_no_load":
                if record is not None and (getattr(record, "back_emf_no_load", None) is not None or getattr(record, "back_emf_no_load_fem", None) is not None):
                    f_wave, f_harm = dp.plot_back_emf_no_load(
                        horizontal_axis=h_axis, show_fem=show_fem, 
                        show_all_phases=show_all_p, show_harmonic=show_harm, plot=False,
                        figsize=square_figsize
                    )
                    figures_dict["Waveform"] = f_wave
                    if show_harm and f_harm:
                        figures_dict["Harmonics"] = f_harm
            elif key == "flux_linkage":
                if record is not None and (getattr(record, "flux_linkage", None) is not None or getattr(record, "flux_linkage_fem", None) is not None):
                    f_wave, f_harm = dp.plot_flux_linkage(
                        horizontal_axis=h_axis, show_fem=show_fem, 
                        show_dq=show_dq, show_all_phase=show_all_p, 
                        show_harmonic=show_harm, plot=False,
                        figsize=square_figsize
                    )
                    figures_dict["Waveform"] = f_wave
                    if show_harm and f_harm:
                        figures_dict["Harmonics"] = f_harm
            elif key == "flux_linkage_no_load":
                if record is not None and (getattr(record, "flux_linkage_no_load", None) is not None or getattr(record, "flux_linkage_no_load_fem", None) is not None):
                    f_wave, f_harm = dp.plot_flux_linkage_no_load(
                        horizontal_axis=h_axis, show_fem=show_fem, 
                        show_dq=show_dq, show_all_phase=show_all_p, 
                        show_harmonic=show_harm, plot=False,
                        figsize=square_figsize
                    )
                    figures_dict["Waveform"] = f_wave
                    if show_harm and f_harm:
                        figures_dict["Harmonics"] = f_harm
            elif key == "airgap_flux_density":
                if record is not None and (getattr(record, "airgap_flux_density", None) is not None or getattr(record, "airgap_flux_density_fem", None) is not None):
                    f_wave, f_harm = dp.plot_airgap_flux_density(
                        horizontal_axis=h_axis, show_fem=show_fem, 
                        show_harmonic=show_harm, plot=False,
                        figsize=square_figsize
                    )
                    figures_dict["Waveform"] = f_wave
                    if show_harm and f_harm:
                        figures_dict["Harmonics"] = f_harm
            elif key == "airgap_flux_density_no_load":
                if record is not None and (getattr(record, "airgap_flux_density_no_load", None) is not None or getattr(record, "airgap_flux_density_no_load_fem", None) is not None):
                    f_wave, f_harm = dp.plot_airgap_flux_density_no_load(
                        horizontal_axis=h_axis, show_fem=show_fem, 
                        show_harmonic=show_harm, plot=False,
                        figsize=square_figsize
                    )
                    figures_dict["Waveform"] = f_wave
                    if show_harm and f_harm:
                        figures_dict["Harmonics"] = f_harm
            elif key == "axial_force":
                if record is not None and (getattr(record, "axial_force", None) is not None or getattr(record, "axial_force_fem", None) is not None):
                    fig = dp.plot_axial_force(horizontal_axis=h_axis, show_fem=show_fem, plot=False, figsize=square_figsize)
                    figures_dict["Waveform"] = fig
            elif key == "axial_force_no_load":
                if record is not None and (getattr(record, "axial_force_no_load", None) is not None or getattr(record, "axial_force_no_load_fem", None) is not None):
                    fig = dp.plot_axial_force_no_load(horizontal_axis=h_axis, show_fem=show_fem, plot=False, figsize=square_figsize)
                    figures_dict["Waveform"] = fig
            elif key == "current":
                if record is not None and getattr(record, "currents", None) is not None:
                    fig = dp.plot_current(horizontal_axis=h_axis, show_fem=show_fem, plot=False, figsize=square_figsize)
                    figures_dict["Waveform"] = fig

            render_tab_figures(ctrl, figures_dict)
            if result_tab.status_label:
                result_tab.status_label.setText(f"Status: Displaying {ctrl['title']}")
        except Exception as e:
            if result_tab.status_label:
                result_tab.status_label.setText(f"Error plotting {ctrl['title']}: {str(e)}")

    for config in quantities_config:
        k = config["key"]
        ctrl = result_tab.tab_controllers[k]
        ctrl["combo_axis"].currentIndexChanged.connect(lambda idx, key=k: update_single_tab(key))
        if ctrl["chk_fem"]:
            ctrl["chk_fem"].stateChanged.connect(lambda state, key=k: update_single_tab(key))
        if ctrl["chk_harmonic"]:
            ctrl["chk_harmonic"].stateChanged.connect(lambda state, key=k: update_single_tab(key))
        if ctrl["chk_all_phases"]:
            ctrl["chk_all_phases"].stateChanged.connect(lambda state, key=k: update_single_tab(key))
        if ctrl["chk_dq"]:
            ctrl["chk_dq"].stateChanged.connect(lambda state, key=k: update_single_tab(key))

    def on_sub_tab_changed(index):
        if 0 <= index < len(quantities_config):
            key = quantities_config[index]["key"]
            update_single_tab(key)

    result_tab.sub_tabs.currentChanged.connect(on_sub_tab_changed)

    def handle_refresh():
        current_idx = result_tab.sub_tabs.currentIndex()
        if 0 <= current_idx < len(quantities_config):
            key = quantities_config[current_idx]["key"]
            update_single_tab(key)

    result_tab.refresh = handle_refresh

    return None