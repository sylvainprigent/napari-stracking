from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit,
                            QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout,
                            QPushButton, QMessageBox)
import napari
from ._splugin import SNapariWorker, SNapariWidget, SProgressObserver

from stracking.linkers import SNNLinker, SPLinker, EuclideanCost
from stracking.containers import SParticles, STracks


# ------------------- SLinkerNearestNeighbor -------
class SLinkerNearestNeighborWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        self._points_layer_box = QComboBox()

        self._max_distance_label = QLabel('Max distance')
        self._max_distance_value = QLineEdit('5')

        self._gap_label = QLabel('Gap')
        self._gap_value = QLineEdit('2')

        layout = QGridLayout()
        layout.addWidget(QLabel('Detections layer'), 0, 0)
        layout.addWidget(self._points_layer_box, 0, 1)
        layout.addWidget(self._max_distance_label, 1, 0)
        layout.addWidget(self._max_distance_value, 1, 1)
        layout.addWidget(self._gap_label, 2, 0)
        layout.addWidget(self._gap_value, 2, 1)
        self.setLayout(layout)
        self._init_layer_list()

    def _init_layer_list(self):
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.points.points.Points):
                self._points_layer_box.addItem(layer.name)

    def _on_layer_change(self, e):
        current_points_text = self.points_layer_box.currentText()
        self.points_layer_box.clear()
        is_current_points_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.points.points.Points):
                if layer.name == current_points_text:
                    is_current_points_item_still_here = True
                self.points_layer_box.addItem(layer.name)
        if is_current_points_item_still_here:
            self.points_layer_box.setCurrentText(current_points_text)

    def state(self) -> dict:
        return {'name': 'SNearestNeighborLinker',
                'inputs': {'points': self._points_layer_box.currentText()},
                'parameters': {'max_distance':
                               float(self._max_distance_value.text()),
                               'gap': int(self._gap_value.text())
                               },
                'outputs': ['tracks', 'S Nearest Neighbor Tracks']
                }


class SLinkerNearestNeighborWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        points_layer = state['inputs']['points']
        state_params = state['parameters']

        max_distance = state_params['max_distance']
        gap = state_params['gap']

        euclidean_cost = EuclideanCost(max_cost=max_distance * max_distance)
        linker = SNNLinker(cost=euclidean_cost, gap=gap)
        linker.add_observer(self.observer)
        particles = SParticles(data=self.viewer.layers[points_layer].data,
                               properties=dict(),
                               scale=self.viewer.layers[points_layer].scale)
        self._out_data = linker.run(particles)

        self.finished.emit()

    def set_outputs(self):
        if len(self._out_data.data) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("No track found")
            msg.exec_()
        else:
            self.viewer.add_tracks(self._out_data.data,
                                   name='S Nearest Neighbor Tracks')


# ------------------- SLinkerShortestPath ------------
class SLinkerShortestPathWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        self._points_layer_box = QComboBox()

        self._max_distance_label = QLabel('Max distance')
        self._max_distance_value = QLineEdit('15')

        self._gap_label = QLabel('Gap')
        self._gap_value = QLineEdit('2')

        layout = QGridLayout()
        layout.addWidget(QLabel('Detections layer'), 0, 0)
        layout.addWidget(self._points_layer_box, 0, 1)
        layout.addWidget(self._max_distance_label, 1, 0)
        layout.addWidget(self._max_distance_value, 1, 1)
        layout.addWidget(self._gap_label, 2, 0)
        layout.addWidget(self._gap_value, 2, 1)
        self.setLayout(layout)
        self._init_layer_list()

    def _init_layer_list(self):
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.points.points.Points):
                self._points_layer_box.addItem(layer.name)

    def _on_layer_change(self, e):
        current_points_text = self._points_layer_box.currentText()
        self._points_layer_box.clear()
        is_current_points_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.points.points.Points):
                if layer.name == current_points_text:
                    is_current_points_item_still_here = True
                self._points_layer_box.addItem(layer.name)
        if is_current_points_item_still_here:
            self._points_layer_box.setCurrentText(current_points_text)

    def state(self) -> dict:
        return {'name': 'SShortestPathLinker',
                'inputs': {'points': self._points_layer_box.currentText()},
                'parameters': {'max_distance':
                               float(self._max_distance_value.text()),
                               'gap': int(self._gap_value.text())
                               },
                'outputs': ['tracks', 'S Shortest Path Tracks']
                }


class SLinkerShortestPathWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        points_layer = state['inputs']['points']
        state_params = state['parameters']

        max_distance = state_params['max_distance']
        gap = state_params['gap']

        euclidean_cost = EuclideanCost(max_cost=max_distance * max_distance)
        linker = SPLinker(cost=euclidean_cost, gap=gap)
        linker.add_observer(self.observer)
        particles = SParticles(data=self.viewer.layers[points_layer].data,
                               properties=dict(),
                               scale=self.viewer.layers[points_layer].scale)
        self._out_data = linker.run(particles)

        self.finished.emit()

    def set_outputs(self):
        if len(self._out_data.data) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("No track found")
            msg.exec_()
        else:
            self.viewer.add_tracks(self._out_data.data,
                                   name='S Shortest Path Tracks')
