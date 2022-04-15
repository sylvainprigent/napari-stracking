import qtpy.QtCore 
from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, 
                            QPushButton, QLineEdit, QComboBox)
import napari


class SScale(QWidget):
    """Dock widget for DoG detection

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.viewer.events.layers_change.connect(self._on_layer_change)
        
        # create the scale widget
        layout = QGridLayout()
        self.setLayout(layout)

        self.layers_box = QComboBox()
        self.layers_box.currentTextChanged.connect(self.changed_layer)

        self.x_res_box = QLineEdit('1')
        self.y_res_box = QLineEdit('1')
        self.z_res_box = QLineEdit('1')
        self.t_res_box = QLineEdit('1')

        self.x_label = QLabel('X scale')
        self.y_label = QLabel('Y scale')
        self.z_label = QLabel('Z scale')
        self.t_label = QLabel('t scale')

        btn = QPushButton('Update')
        btn.released.connect(self.update_scale)

        title_label = QLabel("S Scale")
        title_label.setMaximumHeight(50)
        layout.addWidget(title_label, 0, 0, 1, 2)
        layout.addWidget(QLabel('Layer'), 1, 0)
        layout.addWidget(self.layers_box, 1, 1)
        layout.addWidget(self.x_label, 2, 0)
        layout.addWidget(self.x_res_box, 2, 1)
        layout.addWidget(self.y_label, 3, 0)
        layout.addWidget(self.y_res_box, 3, 1)
        layout.addWidget(self.z_label, 4, 0)
        layout.addWidget(self.z_res_box, 4, 1)
        layout.addWidget(self.t_label, 5, 0)
        layout.addWidget(self.t_res_box, 5, 1)
        layout.addWidget(btn, 6, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        title_label.setAlignment(qtpy.QtCore.Qt.AlignHCenter)

        self._init_layer_list()

    def _init_layer_list(self):
        for layer in self.viewer.layers:
            self.layers_box.addItem(layer.name)

        self._show_hide_boxes(self.layers_box.currentText())  
        self._read_scale(self.layers_box.currentText())         

    def _on_layer_change(self, e):
        current_text = self.layers_box.currentText()
        self.layers_box.clear()
        is_current_item_still_here = False
        for layer in self.viewer.layers:
            if layer.name == current_text:
                is_current_item_still_here = True   
            self.layers_box.addItem(layer.name)
        if is_current_item_still_here: 
            self.layers_box.setCurrentText(current_text)
        self._show_hide_boxes(self.layers_box.currentText()) 
        self._read_scale(self.layers_box.currentText())  

    def changed_layer(self, layer_name):
        self._show_hide_boxes(layer_name) 
        self._read_scale(layer_name)  

    def _read_scale(self, layer_name):
        if layer_name in self.viewer.layers:
            current_layer = self.viewer.layers[layer_name]
            if len(current_layer.scale) == 2:
                self.y_res_box.setText(str(current_layer.scale[0]))
                self.x_res_box.setText(str(current_layer.scale[1]))
            elif len(current_layer.scale) == 3:
                self.z_res_box.setText(str(current_layer.scale[0]))
                self.y_res_box.setText(str(current_layer.scale[1]))
                self.x_res_box.setText(str(current_layer.scale[2]))  
            elif len(current_layer.scale) == 4:
                self.t_res_box.setText(str(current_layer.scale[0]))
                self.z_res_box.setText(str(current_layer.scale[1]))
                self.y_res_box.setText(str(current_layer.scale[2]))
                self.x_res_box.setText(str(current_layer.scale[3])) 

    def _show_hide_boxes(self, layer_name):
        if layer_name in self.viewer.layers:
            current_layer = self.viewer.layers[layer_name]
            if len(current_layer.scale) == 2:
                self.z_label.setVisible(False)
                self.t_label.setVisible(False)
                self.z_res_box.setVisible(False)
                self.t_res_box.setVisible(False)
            elif len(current_layer.scale) == 3:
                self.z_label.setVisible(True)
                self.t_label.setVisible(False)
                self.z_res_box.setVisible(True)
                self.t_res_box.setVisible(False)
            elif len(current_layer.scale) == 4:
                self.z_label.setVisible(True)
                self.t_label.setVisible(True)
                self.z_res_box.setVisible(True)
                self.t_res_box.setVisible(True)         

    def update_scale(self):
        current_layer = self.viewer.layers[self.layers_box.currentText()]
        if len(current_layer.scale) == 2:
            current_layer.scale = [float(self.y_res_box.text()), float(self.x_res_box.text())]
        elif len(current_layer.scale) == 3:
            current_layer.scale = [float(self.z_res_box.text()), float(self.y_res_box.text()), float(self.x_res_box.text())]
        elif len(current_layer.scale) == 4:
            current_layer.scale = [float(self.t_res_box.text()), float(self.z_res_box.text()), float(self.y_res_box.text()), float(self.x_res_box.text())]
