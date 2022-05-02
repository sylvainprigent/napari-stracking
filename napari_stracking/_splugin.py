from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QPushButton,
                            QHBoxLayout, QVBoxLayout, QProgressBar,
                            QTextEdit, QMessageBox)
from qtpy import QtCore
from qtpy.QtCore import Signal, QThread, QObject


class SNapariWidget(QWidget):
    """Interface for a STracking napari widget

    This interface implements three methods
    - show_error: to display a user input error
    - check_inputs (abstract): to check all the user input from the plugin widget
    - state (abstract): to get the plugin widget state, ie the user inputs values set in the widget

    """
    advanced = Signal(bool)
    enable = Signal(bool)

    def __init__(self):
        super().__init__()
        self.is_advanced = False

    @staticmethod
    def show_error(message):
        """Display an error message in a QMessage box

        Parameters
        ----------
        message: str
            Error message

        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setText(message)
        msg.setWindowTitle("STracking error")
        msg.exec_()

    def check_inputs(self):
        """Check the user input in this widget

        Returns:
            True if no error, False if at least one input contains an error.
            (ex not well writen number)

        """
        raise NotImplementedError()

    def state(self):
        """Return the current state of the widget

        The state in inputs values displayed in the the widget. Example

        .. highlight:: python
        .. code-block:: python

            {'name': 'SDoGDetector',
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

        Returns:
            dict: a dictionary containing the widget inputs

        """
        raise NotImplementedError()


class SNapariWorker(QObject):
    """Interface for a STracking napari plugin

    The worker is an object that run the calculation (using the run method) using the user inputs
    from the plugin widget interface (SNapariWidget)

    """
    finished = Signal()
    progress = Signal(int)
    log = Signal(str)

    def __init__(self, napari_viewer, widget):
        super().__init__()
        self.viewer = napari_viewer
        self.widget = widget

    def state(self):
        """Get the states from the SNapariWidget"""
        self.widget.state()

    def run(self):
        """Exec the data processing"""
        raise NotImplementedError()


class SNapariPlugin(QWidget):
    """Definition of a STracking napari widget

    To create a new plugin, simply create a new class that inherit from
    SNapariPlugin and instantiate self.worker, self.widget and call init_ui in the
    constructor.

    The SNapariPlugin purpose is to implement a default run button and log widget for all STracking
    plugins and provide a run method that start the worker in a separate thread

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    Attributes
    ----------
    worker: SNapariWorker
        Instance of the plugin worker
    widget: SNapariWidget
        Instance of the plugin widget

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
        self.run_btn = None
        self.log_widget = SLogWidget()

    def init_ui(self):
        """Initialize the plugin graphical interface

        The plugin interface add a run button and a log widget to the plugin (SNapariWidget) widget

        """
        layout = QVBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(self.title)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(self.widget)

        self.run_btn = QPushButton('Run')
        self.run_btn.released.connect(self.run)
        layout.addWidget(self.run_btn)

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
        """Start the worker in a new thread"""
        if self.widget.check_inputs():
            self.thread.start()

    def set_advanced(self, mode: bool):
        """Toggle the graphical interface to advanced mode

        Parameters
        ----------
        mode: bool
            True to set mode to advanced, False to set mode to default

        """
        self.log_widget.set_advanced(mode)

    def set_enable(self, mode: bool):
        """Callback called to disable the run button when the inputs layers are not available"""
        self.run_btn.setEnabled(mode)

    def set_outputs(self):
        """Call the worker set_outputs method to set the plugin outputs to napari layers"""
        self.worker.set_outputs()


class SLogWidget(QWidget):
    """Widget to log the STracking plugins messages in the graphical interface"""
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
        """Show hide the log area depending on the plugin mode"""
        if mode:
            self.log_area.setVisible(True)
        else:
            self.log_area.setVisible(False)

    def set_progress(self, value: int):
        """Callback to update the progress bar"""
        self.progress_bar.setValue(value)

    def add_log(self, value: str):
        """Callback to add a new message in the log area"""
        self.log_area.append(value)

    def clear_log(self):
        """Callback to clear all the log area"""
        self.log_area.clear()


class SProgressObserver(QObject):
    """Implement the STRacking observer design pattern to display STracking tools progress"""
    progress_signal = Signal(int)
    notify_signal = Signal(str)

    def __init__(self):
        super().__init__()

    def progress(self, value):
        """Callback to refresh the computation progress"""
        self.progress_signal.emit(value)

    def notify(self, message):
        """Callback to notify a new log message"""
        self.notify_signal.emit(message)
