from PyQt5.QtWidgets import QAction, QStyle, QWidget
import numpy as np

def _setup_viewer_ui(pl, state, sym_factor, has_results):
    menubar = pl.app_window.menuBar()
    view_menu = None
    for action in menubar.actions():
        if "View" in action.text():
            view_menu = action.menu()
            break
    
    if view_menu:
        view_menu.clear() 
        
        act_geo = QAction("Show Geometry", pl.app_window); act_geo.setCheckable(True); act_geo.setChecked(state.show_geometry)
        act_geo.triggered.connect(state.toggle_geometry_btn); view_menu.addAction(act_geo)
        state.ref_act_geo = act_geo
        
        act_mesh = QAction("Show Mesh Wireframe", pl.app_window); act_mesh.setCheckable(True)
        act_mesh.triggered.connect(state.toggle_mesh_btn); view_menu.addAction(act_mesh)
        
        act_axes = QAction("Show Custom Axes", pl.app_window); act_axes.setCheckable(True); act_axes.setChecked(True)
        act_axes.triggered.connect(state.toggle_axes_btn); view_menu.addAction(act_axes)
        
        if sym_factor > 1:
            act_sym = QAction("Enable Symmetry", pl.app_window); act_sym.setCheckable(True); act_sym.setChecked(False)
            act_sym.triggered.connect(state.toggle_symmetry_btn); view_menu.addAction(act_sym)
            
        act_bmap = QAction("Show B-Map (Flux)", pl.app_window); act_bmap.setCheckable(True); act_bmap.setChecked(state.bmap_mode)
        act_bmap.setEnabled(has_results)
        act_bmap.triggered.connect(state.toggle_bmap_btn); view_menu.addAction(act_bmap)
        state.ref_act_bmap = act_bmap

        view_menu.addSeparator()
        scale_menu = view_menu.addMenu("Scale Axes")
        act_inc = QAction("Increase Size (+)", pl.app_window); act_inc.triggered.connect(lambda: state.resize_axes(1)); scale_menu.addAction(act_inc)
        act_dec = QAction("Decrease Size (-)", pl.app_window); act_dec.triggered.connect(lambda: state.resize_axes(-1)); scale_menu.addAction(act_dec)
        view_menu.addSeparator()
        act_hd = QAction("Screenshot HD", pl.app_window); act_hd.triggered.connect(state.save_screenshot_hd); view_menu.addAction(act_hd)

    tb = pl.app_window.addToolBar("Playback & Slicing")
    def add_slice(label, attr_show, attr_pos, check=False):
        a = QAction(label, pl.app_window); a.setCheckable(True); a.setChecked(check)
        a.triggered.connect(lambda s: (setattr(state, attr_show, s), state.render()))
        tb.addAction(a)
        l_attr = f"max_{attr_pos.split('_')[1]}"
        dec = QAction("-", pl.app_window); dec.triggered.connect(lambda: (setattr(state, attr_pos, np.clip(getattr(state, attr_pos)-1, 0, getattr(state, l_attr)-1)), state.render())); tb.addAction(dec)
        inc = QAction("+", pl.app_window); inc.triggered.connect(lambda: (setattr(state, attr_pos, np.clip(getattr(state, attr_pos)+1, 0, getattr(state, l_attr)-1)), state.render())); tb.addAction(inc)
        tb.addWidget(QWidget())

    add_slice("R", 'show_i', 'pos_i', False)
    add_slice("Th", 'show_j', 'pos_j', False)
    add_slice("Z", 'show_k', 'pos_k', False)
    
    tb.addSeparator()
    act_play = QAction(pl.app.style().standardIcon(QStyle.SP_MediaPlay), "", pl.app_window)
    act_play.setEnabled(has_results)
    act_play.triggered.connect(state.toggle_play); tb.addAction(act_play)
    
    act_gif = QAction("GIF", pl.app_window)
    act_gif.setEnabled(has_results)
    act_gif.triggered.connect(state.save_gif); tb.addAction(act_gif)