import os
from qtpy import QtCore
from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel,
                            QPushButton, QLineEdit, QComboBox,
                            QFileDialog, QMessageBox)
from qtpy.QtCore import Signal, QThread, QObject
import napari
from stracking.pipelines import STrackingPipeline
from ._splugin import SProgressObserver, SLogWidget


class SPipelineWorker(QObject):
    finished = Signal()
    progress = Signal(int)
    log = Signal(str)

    def __init__(self):
        super().__init__()
        self.image = None
        self.pipeline_file = None
        self.tracks_ = None

        self.observer = SProgressObserver()
        self.observer.progress_signal.connect(self.progress)
        self.observer.notify_signal.connect(self.log)

    def set_inputs(self, image, pipeline_file):
        self.image = image
        self.pipeline_file = pipeline_file

    def run(self):
        self.progress.emit(0)
        pipeline = STrackingPipeline()
        pipeline.add_observer(self.observer)
        print('run pipeline with file:', self.pipeline_file)
        pipeline.load(self.pipeline_file)
        self.tracks_ = pipeline.run(self.image)
        self.progress.emit(100)
        self.finished.emit()


class SPipeline(QWidget):
    """Dock widget to run a STracking pipeline

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.viewer.events.layers_change.connect(self._on_layer_change)

        # thread
        self.thread = QThread()
        self.worker = SPipelineWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.set_outputs)

        layout = QGridLayout()
        # input image layer
        self._images_layers = QComboBox()

        # pipeline file
        self._pipeline_edit = QLineEdit()
        browse_button = QPushButton('...')
        browse_button.released.connect(self._browser_pipeline)

        # run
        self.run_btn = QPushButton('Run')
        self.run_btn.released.connect(self._run)

        # progress
        self.log_widget = SLogWidget()
        self.worker.progress.connect(self.log_widget.set_progress)
        self.worker.log.connect(self.log_widget.add_log)

        layout.addWidget(QLabel('Image:'), 0, 0)
        layout.addWidget(self._images_layers, 0, 1, 1, 2)
        layout.addWidget(QLabel('Pipeline:'), 1, 0)
        layout.addWidget(self._pipeline_edit, 1, 1)
        layout.addWidget(browse_button, 1, 2)
        layout.addWidget(self.run_btn, 2, 0, 1, 3)
        layout.addWidget(self.log_widget, 3, 0, 1, 3)
        layout.addWidget(QWidget(), 4, 0, 1, 3, QtCore.Qt.AlignTop)
        self.setLayout(layout)
        self._on_layer_change(None)

    def init_layers_list(self):
        self._on_layer_change(None)

    def _on_layer_change(self, e):
        # particles
        self._images_layers.clear()
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.image.image.Image):
                self._images_layers.addItem(layer.name)
        if self._images_layers.count() < 1:
            self.run_btn.setEnabled(False)
        else:
            self.run_btn.setEnabled(True)

    def _browser_pipeline(self):
        file = QFileDialog.getOpenFileName(self, 'Pipeline File')
        if len(file) > 0:
            self._pipeline_edit.setText(file[0])

    def _run(self):
        if self.check_inputs():
            self.worker.set_inputs(self.viewer.layers[self._images_layers.currentText()].data,
                                   self._pipeline_edit.text())
            self.thread.start()

    def check_inputs(self):
        pipeline_file = self._pipeline_edit.text()
        if not os.path.exists(pipeline_file):
            self._show_error("Cannot find the pipeline file")
            return False
        return True

    def _show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("STracking error")
        msg.exec_()

    def set_outputs(self):
        self.viewer.add_tracks(self.worker.tracks_.data,
                               name='S Pipeline',
                               scale=self.worker.tracks_.scale,
                               properties=self.worker.tracks_.properties,
                               metadata=self.worker.tracks_.features,
                               graph=self.worker.tracks_.graph)
