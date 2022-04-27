from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QLineEdit,
                            QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout,
                            QPushButton)
import numpy as np
import napari
from ._splugin import SNapariWorker, SNapariWidget, SProgressObserver
from ._swidgets import SPropertiesViewer, SPipelineListWidget

from stracking.detectors import (DoGDetector, DoHDetector, LoGDetector, SSegDetector)


# ---------------- DoG ----------------
class SDogWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        self._input_layer_box = QComboBox()
        self._advanced_check = QCheckBox('advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)

        self._current_frame_check = QCheckBox('Process only current frame')

        self._min_sigma_value = QLineEdit('1')
        self._min_sigma_label = QLabel('Min sigma')

        self._max_sigma_label = QLabel('Max sigma')
        self._max_sigma_value = QLineEdit('5')

        self._threshold_label = QLabel('Threshold')
        self._threshold_value = QLineEdit('2.0')

        self._sigma_ratio_label = QLabel('Sigma ratio')
        self._sigma_ratio_value = QLineEdit('1.6')

        self._overlap_label = QLabel('Overlap')
        self._overlap_value = QLineEdit('0.5')

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel('Image layer'), 0, 0)
        layout.addWidget(self._input_layer_box, 0, 1)
        layout.addWidget(self._advanced_check, 1, 0, 1, 2)

        layout.addWidget(self._current_frame_check, 2, 0, 1, 2)
        layout.addWidget(self._min_sigma_label, 3, 0)
        layout.addWidget(self._min_sigma_value, 3, 1)
        layout.addWidget(self._max_sigma_label, 4, 0)
        layout.addWidget(self._max_sigma_value, 4, 1)
        layout.addWidget(self._threshold_label, 5, 0)
        layout.addWidget(self._threshold_value, 5, 1)
        layout.addWidget(self._sigma_ratio_label, 6, 0)
        layout.addWidget(self._sigma_ratio_value, 6, 1)
        layout.addWidget(self._overlap_label, 7, 0)
        layout.addWidget(self._overlap_value, 7, 1)
        self.setLayout(layout)
        #self.init_layer_list()
        self.toggle_advanced(False)

    def init_layer_list(self):
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                self._input_layer_box.addItem(layer.name)
        if self._input_layer_box.count() < 1:
            # print('disable the run button')
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def _on_layer_change(self, e):
        current_text = self._input_layer_box.currentText()
        self._input_layer_box.clear()
        is_current_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                if layer.name == current_text:
                    is_current_item_still_here = True
                self._input_layer_box.addItem(layer.name)
        if is_current_item_still_here:
            self._input_layer_box.setCurrentText(current_text)
        if self._input_layer_box.count() < 1:
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def check_inputs(self):
        # Min sigma
        try:
            _ = float(self._min_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Min Sigma input must be a number")
            return False
        # Max sigma
        try:
            _ = float(self._max_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Max Sigma input must be a number")
            return False
        # Threshold value
        try:
            _ = float(self._threshold_value.text())
        except ValueError as err:
            self.show_error(f"Threshold input must be a number")
            return False
        # Sigma ratio
        try:
            _ = float(self._sigma_ratio_value.text())
        except ValueError as err:
            self.show_error(f"Sigma ratio input must be a number")
            return False
        # Overlap value
        try:
            _ = float(self._overlap_value.text())
        except ValueError as err:
            self.show_error(f"Overlap input must be a number")
            return False
        return True

    def state(self) -> dict:
        return {'name': 'SDoGDetector',
                'inputs': {'image': self._input_layer_box.currentText()},
                'parameters': {'min_sigma': float(self._min_sigma_value.text()),
                               'max_sigma': float(self._max_sigma_value.text()),
                               'threshold': float(self._threshold_value.text()),
                               'sigma_ratio': float(self._sigma_ratio_value.text()),
                               'overlap': float(self._overlap_value.text()),
                               'current_frame': self._current_frame_check.isChecked()
                               },
                'outputs': ['points', 'DoG detections']
                }

    def toggle_advanced(self, value):
        """Change the parameters widget to advanced mode"""
        if value:
            self._sigma_ratio_label.setVisible(True)
            self._sigma_ratio_value.setVisible(True)
            self._overlap_label.setVisible(True)
            self._overlap_value.setVisible(True)
        else:
            self._sigma_ratio_label.setVisible(False)
            self._sigma_ratio_value.setVisible(False)
            self._overlap_label.setVisible(False)
            self._overlap_value.setVisible(False)
        self.advanced.emit(value)
        self.is_advanced = value


class SDogWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        input_image_layer = state['inputs']['image']
        state_params = state['parameters']

        min_sigma = state_params['min_sigma']
        max_sigma = state_params['max_sigma']
        threshold = state_params['threshold']
        sigma_ratio = state_params['sigma_ratio']
        overlap = state_params['overlap']
        detector = DoGDetector(min_sigma=min_sigma, max_sigma=max_sigma,
                               threshold=threshold, sigma_ratio=sigma_ratio,
                               overlap=overlap)
        detector.add_observer(self.observer)

        image = self.viewer.layers[input_image_layer].data
        scale = self.viewer.layers[input_image_layer].scale

        if state_params['current_frame']:
            t = self.viewer.dims.current_step[0]
            particles = detector.run(np.expand_dims(image[t, ...], 0), scale)
            particles.data[:, 0] = t
        else:
            particles = detector.run(image, scale)

        self._out_data = {'data': particles.data, 'scale': scale,
                          'size': max_sigma,
                          'name': 'DoG detections'}

        self.finished.emit()

    def set_outputs(self):
        self.viewer.add_points(self._out_data['data'],
                               scale=self._out_data['scale'],
                               size=self._out_data['size'],
                               name='DoG detections')


# ----------------- LoG -------------------
class SLogWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        self._input_layer_box = QComboBox()
        self._advanced_check = QCheckBox('advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)

        self._current_frame_check = QCheckBox('Process only current frame')

        self._min_sigma_label = QLabel('Min sigma')
        self._min_sigma_value = QLineEdit('1')

        self._max_sigma_label = QLabel('Max sigma')
        self._max_sigma_value = QLineEdit('5')

        self._num_sigma_label = QLabel('Num sigma')
        self._num_sigma_value = QLineEdit('10')

        self._threshold_label = QLabel('Threshold')
        self._threshold_value = QLineEdit('0.2')

        self._overlap_label = QLabel('Overlap')
        self._overlap_value = QLineEdit('0.5')

        self._log_scale_label = QLabel('Log scale')
        self._log_scale_value = QComboBox()
        self._log_scale_value.addItems(['False', 'True'])

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel('Image layer'), 0, 0)
        layout.addWidget(self._input_layer_box, 0, 1)
        layout.addWidget(self._advanced_check, 1, 0, 1, 2)

        layout.addWidget(self._current_frame_check, 2, 0, 1, 2)
        layout.addWidget(self._min_sigma_label, 3, 0)
        layout.addWidget(self._min_sigma_value, 3, 1)
        layout.addWidget(self._max_sigma_label, 4, 0)
        layout.addWidget(self._max_sigma_value, 4, 1)
        layout.addWidget(self._num_sigma_label, 5, 0)
        layout.addWidget(self._num_sigma_value, 5, 1)
        layout.addWidget(self._threshold_label, 6, 0)
        layout.addWidget(self._threshold_value, 6, 1)
        layout.addWidget(self._overlap_label, 7, 0)
        layout.addWidget(self._overlap_value, 7, 1)
        layout.addWidget(self._log_scale_label, 8, 0)
        layout.addWidget(self._log_scale_value, 8, 1)
        self.setLayout(layout)
        # self._init_layer_list()
        self.toggle_advanced(False)

    def init_layer_list(self):
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                self._input_layer_box.addItem(layer.name)
        if self._input_layer_box.count() < 1:
            # print('disable the run button')
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def _on_layer_change(self, e):
        current_text = self._input_layer_box.currentText()
        self._input_layer_box.clear()
        is_current_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                if layer.name == current_text:
                    is_current_item_still_here = True
                self._input_layer_box.addItem(layer.name)
        if is_current_item_still_here:
            self._input_layer_box.setCurrentText(current_text)
        if self._input_layer_box.count() < 1:
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def check_inputs(self):
        # Min sigma
        try:
            _ = float(self._min_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Min Sigma input must be a number")
            return False
        # Max sigma
        try:
            _ = float(self._max_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Max Sigma input must be a number")
            return False
        # Num sigma
        try:
            _ = int(self._num_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Num Sigma input must be a number")
            return False
        # Threshold value
        try:
            _ = float(self._threshold_value.text())
        except ValueError as err:
            self.show_error(f"Threshold input must be a number")
            return False
        # Overlap value
        try:
            _ = float(self._overlap_value.text())
        except ValueError as err:
            self.show_error(f"Overlap input must be a number")
            return False
        return True

    def state(self) -> dict:
        return {'name': 'SDoGDetector',
                'inputs': {'image': self._input_layer_box.currentText()},
                'parameters': {'min_sigma': float(self._min_sigma_value.text()),
                               'max_sigma': float(self._max_sigma_value.text()),
                               'num_sigma': int(self._num_sigma_value.text()),
                               'threshold': float(self._threshold_value.text()),
                               'log_scale': self._log_scale_value.currentText(),
                               'overlap': float(self._overlap_value.text()),
                               'current_frame': self._current_frame_check.isChecked()
                               },
                'outputs': ['points', 'LoG detections']
                }

    def toggle_advanced(self, value):
        """Change the parameters widget to advanced mode"""
        if value:
            self._overlap_label.setVisible(True)
            self._overlap_value.setVisible(True)
            self._log_scale_label.setVisible(True)
            self._log_scale_value.setVisible(True)
        else:
            self._overlap_label.setVisible(False)
            self._overlap_value.setVisible(False)
            self._log_scale_label.setVisible(False)
            self._log_scale_value.setVisible(False)
        self.advanced.emit(value)
        self.is_advanced = value


class SLogWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        if state is None:
            return
        input_image_layer = state['inputs']['image']
        state_params = state['parameters']

        min_sigma = state_params['min_sigma']
        max_sigma = state_params['max_sigma']
        threshold = state_params['threshold']
        num_sigma = state_params['num_sigma']
        overlap = state_params['overlap']
        log_txt = state_params['log_scale']
        log_scale = False
        if log_txt == 'True':
            log_scale = True

        detector = LoGDetector(min_sigma=min_sigma, max_sigma=max_sigma,
                               num_sigma=num_sigma, threshold=threshold,
                               overlap=overlap, log_scale=log_scale)
        detector.add_observer(self.observer)

        image = self.viewer.layers[input_image_layer].data
        scale = self.viewer.layers[input_image_layer].scale
        if state_params['current_frame']:
            t = self.viewer.dims.current_step[0]
            particles = detector.run(np.expand_dims(image[t, ...], 0), scale)
            particles.data[:, 0] = t
        else:
            particles = detector.run(image, scale)

        self._out_data = {'data': particles.data, 'scale': scale,
                          'size': max_sigma,
                          'name': 'LoG detections'}

        self.finished.emit()

    def set_outputs(self):
        self.viewer.add_points(self._out_data['data'],
                               scale=self._out_data['scale'],
                               size=self._out_data['size'],
                               name='LoG detections')


# ------------------ DoH -------------------
class SDohWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        self._input_layer_box = QComboBox()
        self._advanced_check = QCheckBox('advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)

        self._current_frame_check = QCheckBox('Process only current frame')

        self._min_sigma_label = QLabel('Min sigma')
        self._min_sigma_value = QLineEdit('1')

        self._max_sigma_label = QLabel('Max sigma')
        self._max_sigma_value = QLineEdit('5')

        self._num_sigma_label = QLabel('Num sigma')
        self._num_sigma_value = QLineEdit('10')

        self._threshold_label = QLabel('Threshold')
        self._threshold_value = QLineEdit('0.01')

        self._overlap_label = QLabel('Overlap')
        self._overlap_value = QLineEdit('0.5')

        self._log_scale_label = QLabel('Log scale')
        self._log_scale_value = QComboBox()
        self._log_scale_value.addItems(['False', 'True'])

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel('Image layer'), 0, 0)
        layout.addWidget(self._input_layer_box, 0, 1)
        layout.addWidget(self._advanced_check, 1, 0, 1, 2)

        layout.addWidget(self._current_frame_check, 2, 0, 1, 2)
        layout.addWidget(self._min_sigma_label, 3, 0)
        layout.addWidget(self._min_sigma_value, 3, 1)
        layout.addWidget(self._max_sigma_label, 4, 0)
        layout.addWidget(self._max_sigma_value, 4, 1)
        layout.addWidget(self._num_sigma_label, 5, 0)
        layout.addWidget(self._num_sigma_value, 5, 1)
        layout.addWidget(self._threshold_label, 6, 0)
        layout.addWidget(self._threshold_value, 6, 1)
        layout.addWidget(self._overlap_label, 7, 0)
        layout.addWidget(self._overlap_value, 7, 1)
        layout.addWidget(self._log_scale_label, 8, 0)
        layout.addWidget(self._log_scale_value, 8, 1)
        self.setLayout(layout)
        # self._init_layer_list()
        self.toggle_advanced(False)

    def init_layer_list(self):
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                self._input_layer_box.addItem(layer.name)
        if self._input_layer_box.count() < 1:
            # print('disable the run button')
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def _on_layer_change(self, e):
        current_text = self._input_layer_box.currentText()
        self._input_layer_box.clear()
        is_current_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                if layer.name == current_text:
                    is_current_item_still_here = True
                self._input_layer_box.addItem(layer.name)
        if is_current_item_still_here:
            self._input_layer_box.setCurrentText(current_text)
        if self._input_layer_box.count() < 1:
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def check_inputs(self):
        # Min sigma
        try:
            _ = float(self._min_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Min Sigma input must be a number")
            return False
        # Max sigma
        try:
            _ = float(self._max_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Max Sigma input must be a number")
            return False
        # Num sigma
        try:
            _ = int(self._num_sigma_value.text())
        except ValueError as err:
            self.show_error(f"Num Sigma input must be an integer")
            return False
        # Threshold value
        try:
            _ = float(self._threshold_value.text())
        except ValueError as err:
            self.show_error(f"Threshold input must be a number")
            return False
        # Overlap value
        try:
            _ = float(self._overlap_value.text())
        except ValueError as err:
            self.show_error(f"Overlap input must be a number")
            return False
        return True

    def state(self) -> dict:
        return {'name': 'SDoGDetector',
                'inputs': {'image': self._input_layer_box.currentText()},
                'parameters': {'min_sigma': float(self._min_sigma_value.text()),
                               'max_sigma': float(self._max_sigma_value.text()),
                               'num_sigma': int(self._num_sigma_value.text()),
                               'threshold': float(self._threshold_value.text()),
                               'log_scale': self._log_scale_value.currentText(),
                               'overlap': float(self._overlap_value.text()),
                               'current_frame': self._current_frame_check.isChecked()
                               },
                'outputs': ['points', 'LoG detections']
                }

    def toggle_advanced(self, value):
        """Change the parameters widget to advanced mode"""
        if value:
            self._overlap_label.setVisible(True)
            self._overlap_value.setVisible(True)
            self._log_scale_label.setVisible(True)
            self._log_scale_value.setVisible(True)
        else:
            self._overlap_label.setVisible(False)
            self._overlap_value.setVisible(False)
            self._log_scale_label.setVisible(False)
            self._log_scale_value.setVisible(False)
        self.advanced.emit(value)
        self.is_advanced = value


class SDohWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        input_image_layer = state['inputs']['image']
        state_params = state['parameters']

        min_sigma = state_params['min_sigma']
        max_sigma = state_params['max_sigma']
        threshold = state_params['threshold']
        num_sigma = state_params['num_sigma']
        overlap = state_params['overlap']
        log_txt = state_params['log_scale']
        log_scale = False
        if log_txt == 'True':
            log_scale = True
        detector = DoHDetector(min_sigma=min_sigma, max_sigma=max_sigma,
                               num_sigma=num_sigma, threshold=threshold,
                               overlap=overlap, log_scale=log_scale)
        detector.add_observer(self.observer)

        image = self.viewer.layers[input_image_layer].data
        scale = self.viewer.layers[input_image_layer].scale

        if state_params['current_frame']:
            t = self.viewer.dims.current_step[0]
            particles = detector.run(np.expand_dims(image[t, ...], 0), scale)
            particles.data[:, 0] = t
        else:
            particles = detector.run(image, scale)

        self._out_data = {'data': particles.data, 'scale': scale,
                          'size': max_sigma,
                          'name': 'DoH detections'}

        self.finished.emit()

    def set_outputs(self):
        self.viewer.add_points(self._out_data['data'],
                               scale=self._out_data['scale'],
                               size=self._out_data['size'],
                               name='DoH detections')


# ------------------ Seg -------------------
class SSegWidget(SNapariWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        napari_viewer.events.layers_change.connect(self._on_layer_change)

        self._input_layer_box = QComboBox()
        self._advanced_check = QCheckBox('advanced')
        self._advanced_check.stateChanged.connect(self.toggle_advanced)

        self._current_frame_check = QCheckBox('Process only current frame')

        self._type_label = QLabel('Segmentation type')
        self._type_value = QComboBox()
        self._type_value.addItems(['Labels', 'Mask'])

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QLabel('Image layer'), 0, 0)
        layout.addWidget(self._input_layer_box, 0, 1)
        layout.addWidget(self._advanced_check, 1, 0, 1, 2)

        layout.addWidget(self._current_frame_check, 2, 0, 1, 2)
        layout.addWidget(self._type_label, 8, 0)
        layout.addWidget(self._type_value, 8, 1)
        self.setLayout(layout)
        self.toggle_advanced(False)

    def init_layer_list(self):
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                self._input_layer_box.addItem(layer.name)
        if self._input_layer_box.count() < 1:
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def _on_layer_change(self, e):
        current_text = self._input_layer_box.currentText()
        self._input_layer_box.clear()
        is_current_item_still_here = False
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                if layer.name == current_text:
                    is_current_item_still_here = True
                self._input_layer_box.addItem(layer.name)
        if is_current_item_still_here:
            self._input_layer_box.setCurrentText(current_text)
        if self._input_layer_box.count() < 1:
            self.enable.emit(False)
        else:
            self.enable.emit(True)

    def check_inputs(self):
        return True

    def state(self) -> dict:
        return {'name': 'SDoGDetector',
                'inputs': {'image': self._input_layer_box.currentText()},
                'parameters': {'type': self._type_value.currentText(),
                               'current_frame': self._current_frame_check.isChecked()
                               },
                'outputs': ['points', 'LoG detections']
                }

    def toggle_advanced(self, value):
        """Change the parameters widget to advanced mode"""
        self.advanced.emit(value)
        self.is_advanced = value


class SSegWorker(SNapariWorker):
    def __init__(self, napari_viewer, widget):
        super().__init__(napari_viewer, widget)

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

        self._out_data = None

    def run(self):
        """Execute the processing"""
        state = self.widget.state()
        input_image_layer = state['inputs']['image']
        state_params = state['parameters']

        is_mask = False
        if state_params['type'] == 'Mask':
            is_mask = True

        detector = SSegDetector(is_mask=is_mask)
        detector.add_observer(self.observer)

        image = self.viewer.layers[input_image_layer].data
        scale = self.viewer.layers[input_image_layer].scale

        if state_params['current_frame']:
            t = self.viewer.dims.current_step[0]
            particles = detector.run(np.expand_dims(image[t, ...], 0), scale)
            particles.data[:, 0] = t
        else:
            particles = detector.run(image, scale)

        self._out_data = {'data': particles.data, 'scale': scale,
                          'size': 2,
                          'name': 'Seg detections'}

        self.finished.emit()

    def set_outputs(self):
        self.viewer.add_points(self._out_data['data'],
                               scale=self._out_data['scale'],
                               size=self._out_data['size'],
                               name='Seg detections')
