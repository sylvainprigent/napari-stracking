from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit,
                            QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout,
                            QPushButton)
import napari
from ._splugin import SNapariWorker, SNapariWidget, SProgressObserver
from ._swidgets import SPropertiesViewer, SPipelineListWidget

from stracking.containers import SParticles
from stracking.properties import IntensityProperty


# ------------- Spot properties -------------
class SSpotPropertiesWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        # viewers
        self.properties_viewer = SPropertiesViewer(napari_viewer)
        self.properties_viewer.setVisible(False)

        # create the dict of the filters
        global_layout = QVBoxLayout()
        global_layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(global_layout)
        filter_frame = QWidget()
        global_layout.addWidget(filter_frame)
        filter_frame.setStyleSheet(".QWidget{border: none;}")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # layer select
        tracks_selector = QWidget()
        tracks_selector.setStyleSheet(".QWidget{border: none;}")
        tracks_select_layout = QGridLayout()
        tracks_selector.setLayout(tracks_select_layout)
        self.points_layer_box = QComboBox()
        self.image_layer_box = QComboBox()
        self.points_layer_box.currentTextChanged.connect(
            self._on_point_layer_change)
        tracks_select_layout.addWidget(QLabel('Image layer'), 0, 0)
        tracks_select_layout.addWidget(self.image_layer_box, 0, 1)
        tracks_select_layout.addWidget(QLabel('Points layer'), 1, 0)
        tracks_select_layout.addWidget(self.points_layer_box, 1, 1)

        self._advanced_check = QCheckBox('Advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)
        tracks_select_layout.addWidget(self._advanced_check, 2, 0, 1, 2)
        tracks_select_layout.setContentsMargins(0, 0, 0, 0)

        # header widget (add filter from list)
        header_widget = QWidget()
        header_widget.setStyleSheet(".QWidget{border: 1px solid #3d4851;}")
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Add feature:"))
        self.filters_names = QComboBox()
        self.filters_names.addItems(['Intensity'])
        header_layout.addWidget(self.filters_names)
        add_filter_button = QPushButton("Add")
        add_filter_button.released.connect(self._on_add)
        header_layout.addWidget(add_filter_button)
        header_widget.setLayout(header_layout)

        # FilterListWidget
        list_widget = QWidget()
        list_layout = QVBoxLayout()
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_widget.setLayout(list_layout)
        list_widget.setStyleSheet(".QWidget{border: 1px solid #3d4851;}")
        self.pipeline_list_widget = SPipelineListWidget()
        list_layout.addWidget(self.pipeline_list_widget)

        # viewer buttons
        viewer_bar = QWidget()
        viewer_layout = QHBoxLayout()
        properties_btn = QPushButton('particles features')
        properties_btn.released.connect(self._on_show_properties)
        viewer_layout.addWidget(properties_btn)
        viewer_bar.setLayout(viewer_layout)
        viewer_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(tracks_selector, 0)
        layout.addWidget(header_widget, 0)
        layout.addWidget(list_widget, 1)
        layout.addWidget(viewer_bar, 0)
        layout.insertSpacing(2, -9)
        filter_frame.setLayout(layout)
        self._on_layer_change(None)
        self.toggle_advanced(False)

    def toggle_advanced(self, value):
        """Change the parameters widget to advanced mode"""
        self.advanced.emit(value)
        self.is_advanced = value

    def _on_show_properties(self):
        self.properties_viewer.reload()
        self.properties_viewer.show()

    def _on_layer_change(self, e):
        current_points_text = self.points_layer_box.currentText()
        current_image_text = self.image_layer_box.currentText()
        self.points_layer_box.clear()
        is_current_points_item_still_here = False
        is_current_image_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.points.points.Points):
                if layer.name == current_points_text:
                    is_current_points_item_still_here = True
                self.points_layer_box.addItem(layer.name)
            if isinstance(layer, napari.layers.image.image.Image):
                if layer.name == current_image_text:
                    is_current_image_item_still_here = True
                self.image_layer_box.addItem(layer.name)
        if is_current_points_item_still_here:
            self.points_layer_box.setCurrentText(current_points_text)
        if is_current_image_item_still_here:
            self.image_layer_box.setCurrentText(current_image_text)

    def _on_add(self):
        filter_ = self.filters_names.currentText()
        if filter_ == 'Intensity':
            self.pipeline_list_widget.add_widget('Intensity',
                                                 SIntensityPropertyWidget())

    def _on_point_layer_change(self, text):
        self.properties_viewer.layer_name = text

    def state(self) -> dict:
        filters_names = []
        filters_params = []
        filters_widgets = self.pipeline_list_widget.widgets()
        for wid in filters_widgets:
            filters_names.append(wid.name)
            filters_params.append(wid.process_widget.parameters())

        return {'name': 'SSpotProperties',
                'inputs': {'points': self.points_layer_box.currentText(),
                           'image': self.image_layer_box.currentText()},
                'parameters': {'filters': filters_names,
                               'filters_params': filters_params
                               },
                'outputs': ['points', self.points_layer_box.currentText()]
                }


class SIntensityPropertyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layer_name = ''
        self.image_layer_name = ''

        layout = QGridLayout()
        self.setLayout(layout)

        radius_label = QLabel("Radius")
        self.radius_val = QLineEdit()
        layout.addWidget(radius_label, 1, 0)
        layout.addWidget(self.radius_val, 1, 1)

    def parameters(self):
        return {'radius': float(self.radius_val.text())}


class SSpotPropertiesWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        input_points_layer_name = state['inputs']['points']
        input_image_layer_name = state['inputs']['image']

        # get the particles
        spots = self.viewer.layers[input_points_layer_name].data
        particles = SParticles(data=spots)

        # get the image
        image = self.viewer.layers[input_image_layer_name].data

        # run the filters
        state_params = state['parameters']

        filters_names = state_params['filters']
        filters_params = state_params['filters_params']
        for i in range(len(filters_names)):
            n_filter = filters_names[i]
            if n_filter == 'Intensity':
                radius = filters_params[i]['radius']
                property_calc = IntensityProperty(radius)
                property_calc.add_observer(self.observer)
                property_calc.run(particles, image)

        self._out_data = particles
        self.progress.emit(100)
        self.finished.emit()

    def set_outputs(self):
        # set the properties to the layer
        state = self.widget.state()
        input_points_layer_name = state['inputs']['points']
        self.viewer.layers[input_points_layer_name].properties.update(
            self._out_data.properties)

        # print(self.viewer.layers[input_points_layer_name].properties)

