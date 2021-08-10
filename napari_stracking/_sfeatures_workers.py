from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit,
                            QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout,
                            QPushButton)
import napari
from ._splugin import SNapariWorker, SNapariWidget, SProgressObserver
from ._swidgets import SFeaturesViewer, SPipelineListWidget

from stracking.containers import SParticles, STracks
from stracking.features import (LengthFeature, DistanceFeature,
                                DisplacementFeature)


# ------------------ STracksFeaturesWidget --------
class STracksFeaturesWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        # viewers
        self.features_viewer = SFeaturesViewer(napari_viewer)
        self.features_viewer.setVisible(False)

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
        self._tracks_layer_box = QComboBox()
        self._tracks_layer_box.currentTextChanged.connect(
            self._on_tracks_layer_change)
        tracks_select_layout.addWidget(QLabel('Tracks layer'), 0, 0)
        tracks_select_layout.addWidget(self._tracks_layer_box, 0, 1)
        tracks_select_layout.setContentsMargins(0, 0, 0, 0)

        # header widget (add filter from list)
        header_widget = QWidget()
        header_widget.setStyleSheet(".QWidget{border: 1px solid #3d4851;}")
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Add feature:"))
        self.filters_names = QComboBox()
        self.filters_names.addItems(['Length', 'Distance', 'Displacement'])
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
        properties_btn = QPushButton('tracks features')
        properties_btn.released.connect(self._on_show_features)
        viewer_layout.addWidget(properties_btn)
        viewer_bar.setLayout(viewer_layout)
        viewer_layout.setContentsMargins(0, 0, 0, 0)

        self._advanced_check = QCheckBox('Advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)

        layout.addWidget(tracks_selector, 0)
        layout.addWidget(self._advanced_check, 0)
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

    def _on_layer_change(self, e):
        current_points_text = self._tracks_layer_box.currentText()
        self._tracks_layer_box.clear()
        is_current_points_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.tracks.tracks.Tracks):
                if layer.name == current_points_text:
                    is_current_points_item_still_here = True
                self._tracks_layer_box.addItem(layer.name)
        if is_current_points_item_still_here:
            self._tracks_layer_box.setCurrentText(current_points_text)

    def _on_tracks_layer_change(self, text):
        self.features_viewer.layer_name = text

    def _on_show_features(self):
        self.features_viewer.reload()
        self.features_viewer.show()

    def _on_add(self):
        filter_ = self.filters_names.currentText()
        if filter_ == 'Length':
            self.pipeline_list_widget.add_widget('Length',
                                                 SLengthFeatureWidget())
        elif filter_ == 'Distance':
            self.pipeline_list_widget.add_widget('Distance',
                                                 SDistanceFeatureWidget())

        elif filter_ == 'Displacement':
            self.pipeline_list_widget.add_widget('Displacement',
                                                 SDisplacementFeatureWidget())

    def state(self) -> dict:
        filters_names = []
        filters_params = []
        filters_widgets = self.pipeline_list_widget.widgets()
        for wid in filters_widgets:
            filters_names.append(wid.name)
            filters_params.append(wid.process_widget.parameters())

        return {'name': 'SSpotProperties',
                'inputs': {'tracks': self._tracks_layer_box.currentText()},
                'parameters': {'filters': filters_names,
                               'filters_params': filters_params
                               },
                'outputs': ['points', self._tracks_layer_box.currentText()]
                }


class SLengthFeatureWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

    def parameters(self):
        return {}


class SDistanceFeatureWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

    def parameters(self):
        return {}


class SDisplacementFeatureWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        self.setLayout(layout)

    def parameters(self):
        return {}


class STracksFeaturesWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        print(state)
        input_tracks_layer_name = state['inputs']['tracks']

        # get the particles
        data = self.viewer.layers[input_tracks_layer_name].data
        tracks = STracks(data=data, features=dict())

        # run the filters
        state_params = state['parameters']

        filters_names = state_params['filters']
        filters_params = state_params['filters_params']
        for i in range(len(filters_names)):
            n_filter = filters_names[i]
            if n_filter == 'Length':
                feature_calc = LengthFeature()
                feature_calc.add_observer(self.observer)
                tracks = feature_calc.run(tracks)
            elif n_filter == 'Distance':
                feature_calc = DistanceFeature()
                feature_calc.add_observer(self.observer)
                tracks = feature_calc.run(tracks)
            elif n_filter == 'Displacement':
                feature_calc = DisplacementFeature()
                feature_calc.add_observer(self.observer)
                tracks = feature_calc.run(tracks)

        self._out_data = tracks
        self.progress.emit(100)
        self.finished.emit()

    def set_outputs(self):
        # set the properties to the layer
        state = self.widget.state()
        input_tracks_layer_name = state['inputs']['tracks']
        self.viewer.layers[input_tracks_layer_name].metadata.update(
            self._out_data.features)