from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QPushButton,
                            QHBoxLayout, QVBoxLayout, QProgressBar,
                            QTextEdit)
from qtpy import QtCore
from qtpy.QtCore import Signal, QThread, QObject


class SNapariWidget(QWidget):
    advanced = Signal(bool)

    def __init__(self):
        super().__init__()
        self.is_advanced = False

    def state(self):
        raise NotImplementedError()


class SNapariWorker(QObject):
    """Worker interface for plugin

    """
    finished = Signal()
    progress = Signal(int)
    log = Signal(str)

    def __init__(self, napari_viewer, widget):
        super().__init__()
        self.viewer = napari_viewer
        self.widget = widget

    def state(self):
        self.widget.state()

    def run(self):
        raise NotImplementedError()


class SNapariPlugin(QWidget):
    """Dock widget for SDetector

    To create a new plugin, simply create a new class that inherit from
    SNapariPlugin and instantiate self.worker and call self.initUI() in the
    constructor

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # thread
        self.title = 'Default plugin'
        self.worker = None
        self.widget = None
        self.fill_widget_resize = 1
        self.thread = QThread()

        # GUI
        self.log_widget = SLogWidget()

    def init_ui(self):
        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(self.title)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(self.widget)

        run_btn = QPushButton('Run')
        run_btn.released.connect(self.run)
        layout.addWidget(run_btn)

        layout.addWidget(self.log_widget)
        layout.addWidget(QWidget(), self.fill_widget_resize, QtCore.Qt.AlignTop)
        self.setLayout(layout)

        # connect
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.progress.connect(self.log_widget.set_progress)
        self.worker.log.connect(self.log_widget.add_log)
        self.worker.finished.connect(self.set_outputs)
        self.set_advanced(self.widget.is_advanced)

    def run(self):
        self.thread.start()

    def set_advanced(self, mode: bool):
        self.log_widget.set_advanced(mode)

    def set_outputs(self):
        self.worker.set_outputs()


class SLogWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar = QProgressBar()
        self.log_area = QTextEdit()
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_area)
        self.setLayout(layout)

    def set_advanced(self, mode: bool):
        if mode:
            self.log_area.setVisible(True)
        else:
            self.log_area.setVisible(False)

    def set_progress(self, value: int):
        self.progress_bar.setValue(value)

    def add_log(self, value: str):
        self.log_area.append(value)

    def clear_log(self):
        self.log_area.clear()


class SProgressObserver(QObject):
    progress_signal = Signal(int)
    notify_signal = Signal(str)

    def __init__(self):
        super().__init__()

    def progress(self, value):
        self.progress_signal.emit(value)

    def notify(self, message):
        self.notify_signal.emit(message)