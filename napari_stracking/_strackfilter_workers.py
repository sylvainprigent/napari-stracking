from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit,
                            QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout,
                            QPushButton, QMessageBox)
import napari
from ._splugin import SNapariWorker, SNapariWidget, SProgressObserver
from ._swidgets import SPropertiesViewer, SPipelineListWidget

from stracking.containers import STracks
from stracking.filters import FeatureFilter


# ------------- Spot properties -------------
class STrackFilterWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        # tracks layer select
        tracks_selector = QWidget()
        tracks_selector.setStyleSheet(".QWidget{border: none;}")
        tracks_select_layout = QHBoxLayout()
        tracks_selector.setLayout(tracks_select_layout)
        self._tracks_layer_box = QComboBox()
        tracks_select_layout.addWidget(QLabel('Tracks layer'))
        tracks_select_layout.addWidget(self._tracks_layer_box)

        tracks_select_layout.setContentsMargins(0, 0, 0, 0)

        # header widget (add filter from list)
        header_widget = QWidget()
        header_widget.setStyleSheet(".QWidget{border: 1px solid #3d4851;}")
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Add filter:"))
        self.filters_names = QComboBox()
        self.filters_names.addItems(['Features'])
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

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tracks_selector)
        self._advanced_check = QCheckBox('Advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)
        layout.addWidget(self._advanced_check)
        layout.addWidget(header_widget)
        layout.addWidget(list_widget)
        layout.insertSpacing(2, -9)
        self.setLayout(layout)
        self._on_layer_change(None)
        self.toggle_advanced(False)

    def toggle_advanced(self, value):
        """Change the parameters widget to advanced mode"""
        self.advanced.emit(value)
        self.is_advanced = value

    def _on_layer_change(self, e):
        current_tracks_text = self._tracks_layer_box.currentText()
        self._tracks_layer_box.clear()
        is_current_tracks_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.tracks.tracks.Tracks):
                if layer.name == current_tracks_text:
                    is_current_tracks_item_still_here = True
                self._tracks_layer_box.addItem(layer.name)
        if is_current_tracks_item_still_here:
            self._tracks_layer_box.setCurrentText(current_tracks_text)

    def _on_add(self):
        filter_ = self.filters_names.currentText()
        current_layer = self._tracks_layer_box.currentText()
        if filter_ == 'Features':
            self.pipeline_list_widget.add_widget('Features',
                                                 SFeatureFilterWidget(
                                                     self.viewer,
                                                     current_layer))

    def state(self) -> dict:
        filters_names = []
        filters_params = []
        filters_widgets = self.pipeline_list_widget.widgets()
        for wid in filters_widgets:
            filters_names.append(wid.name)
            filters_params.append(wid.process_widget.parameters())

        return {'name': 'STracksFilter',
                'inputs': {'tracks': self._tracks_layer_box.currentText()},
                'parameters': {'filters': filters_names,
                               'filters_params': filters_params
                               },
                'outputs': ['tracks', 'S Tracks Filter']
                }


class SFeatureFilterWidget(QWidget):
    def __init__(self, napari_viewer, layer_name):
        super().__init__()
        self.viewer = napari_viewer
        self.layer_name = layer_name

        self.features_box = QComboBox()
        if len(napari_viewer.layers) > 0:
            for key in napari_viewer.layers[layer_name].metadata.keys():
                self.features_box.addItem(key)

        layout = QGridLayout()
        layout.addWidget(QLabel('Feature:'), 0, 0)
        layout.addWidget(self.features_box, 0, 1)

        min_label = QLabel("Min:")
        self.min_val = QLineEdit()
        layout.addWidget(min_label, 1, 0)
        layout.addWidget(self.min_val, 1, 1)

        max_label = QLabel("Max:")
        self.max_val = QLineEdit()
        layout.addWidget(max_label, 2, 0)
        layout.addWidget(self.max_val, 2, 1)
        self.setLayout(layout)

    def parameters(self):
        return {'feature': self.features_box.currentText(),
                'min': float(self.min_val.text()),
                'max': float(self.max_val.text())
                }


class STrackFilterWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        current_layer = state['inputs']['tracks']

        # get the particles
        data = self.viewer.layers[current_layer].data.copy()
        properties = self.viewer.layers[current_layer].properties.copy()
        features = self.viewer.layers[current_layer].metadata.copy()
        scale = self.viewer.layers[current_layer].scale.copy()
        tracks = STracks(data=data, properties=properties, features=features,
                         scale=scale)

        # run the filters
        state_params = state['parameters']

        filters_names = state_params['filters']
        filters_params = state_params['filters_params']
        tracks_o = tracks
        for i in range(len(filters_names)):
            n_filter = filters_names[i]
            if n_filter == 'Features':
                feature_name = filters_params[i]['feature']
                min_val = filters_params[i]['min']
                max_val = filters_params[i]['max']
                f_filter = FeatureFilter(feature_name=feature_name,
                                         min_val=min_val,
                                         max_val=max_val)
                f_filter.add_observer(self.observer)
                tracks_o = f_filter.run(tracks_o)

        self._out_data = tracks_o
        self.progress.emit(100)
        self.finished.emit()

    def set_outputs(self):
        if len(self._out_data.data) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("No track found")
            msg.exec_()
        else:
            self.viewer.add_tracks(self._out_data.data,
                                   name='S Tracks Filter')

