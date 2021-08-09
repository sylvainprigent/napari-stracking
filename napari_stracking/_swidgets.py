import numpy as np
from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel, QPushButton,
                            QLineEdit, QHBoxLayout, QVBoxLayout, QComboBox,
                            QTableWidget, QAbstractItemView, QTableWidgetItem,
                            QScrollArea)
import qtpy.QtCore as QtCore
from qtpy.QtCore import Signal


class SPropertiesViewer(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.layer_name = ''

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

    def reload(self):
        particles = self.viewer.layers[self.layer_name].data
        print(particles)
        properties = self.viewer.layers[self.layer_name].properties
        headers = []
        if particles.shape[1] == 3:
            headers = ['T', 'Y', 'X']
        elif particles.shape[1] == 4:
            headers = ['T', 'Z', 'Y', 'X']

        for key in properties:
            headers.append(key)
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(particles.shape[0])

        col = 0
        for line in range(particles.shape[0]):
            col = -1

            # T
            if particles.shape[1] == 4:
                col += 1
                self.tableWidget.setItem(line, col,
                                         QTableWidgetItem(
                                             str(particles[line, col])))
            # T or Z
            if particles.shape[1] >= 3:
                col += 1
                self.tableWidget.setItem(line, col,
                                         QTableWidgetItem(
                                             str(particles[line, col])))
            # Y
            col += 1
            self.tableWidget.setItem(line, col,
                                     QTableWidgetItem(
                                         str(particles[line, col])))
            # X
            col += 1
            self.tableWidget.setItem(line, col,
                                     QTableWidgetItem(
                                         str(particles[line, col])))
        # properties
        for key in properties:
            col += 1
            prop = properties[key]
            for line in range(len(prop)):
                self.tableWidget.setItem(line, col,
                                         QTableWidgetItem(str(prop[line])))


class SFeaturesViewer(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.layer_name = ''

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

    def reload(self):
        particles = self.viewer.layers[self.layer_name].data
        features = self.viewer.layers[self.layer_name].metadata
        headers = ['track_id']
        for key in features:
            if isinstance(features[key], dict):
                headers.append(key)
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(len(np.unique(particles[:, 0])))

        features_dict = dict()
        tracks_ids = np.unique(particles[:, 0])
        for id_ in tracks_ids:
            features_dict[id_] = list()

        for key in features:
            if isinstance(features[key], dict):
                feature_dict = features[key]
                for f_key in feature_dict:
                    if f_key in features_dict:
                        features_dict[f_key].append(str(feature_dict[f_key]))

        line = -1
        for key in features_dict:
            line += 1
            # track_id = key
            self.tableWidget.setItem(line, 0, QTableWidgetItem(str(key)))
            # add each feature per column
            col = 0
            for feature in features_dict[key]:
                col += 1
                self.tableWidget.setItem(line, col, QTableWidgetItem(feature))


class SProcessInListWidget(QWidget):
    remove = Signal(str)
    """Process widget that can be inserted and removed from SProcessListWidget

    Parameters
    ----------
    uuid: str
        Unique ID of the widget in the list
    process_widget: SProcessWidget
        Process widget to set in the list

    """
    def __init__(self, uuid, name, process_widget):
        super().__init__()

        self.name = name
        self.uuid = uuid
        self.process_widget = process_widget

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setContentsMargins(0, 0, 0, 0)
        self.title = QLabel(name)
        self.title.setStyleSheet("QWidget{background-color: #3d4851;}")
        close_btn = QPushButton('X')
        close_btn.setFixedWidth(45)
        close_btn.released.connect(self._on_remove)
        header_layout.addWidget(self.title, 1)
        header_layout.addWidget(close_btn, 0, QtCore.Qt.AlignRight)
        header_widget.setLayout(header_layout)

        layout.addWidget(header_widget)
        layout.addWidget(process_widget)

        self.setLayout(layout)

    def _on_remove(self):
        self.remove.emit(str(self.uuid))


class SPipelineListWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.input_layer_name = ''
        self._count = 0

        list_widget = QWidget()
        list_widget.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        scroll_widget = QScrollArea()
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setWidget(list_widget)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll_widget)
        self.setLayout(layout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(QWidget(), 1, QtCore.Qt.AlignTop)
        list_widget.setLayout(self.layout)

    def add_widget(self, name, widget):
        self._count += 1
        widget_ = SProcessInListWidget(str(self._count), name, widget)
        widget_.remove.connect(self._on_remove_widget)
        index = self.layout.count()-1
        self.layout.insertWidget(index, widget_, 0, QtCore.Qt.AlignTop)

    def _on_remove_widget(self, uuid):
        """Remove a filter

        Parameters
        ----------
        uuid: int
            Unique id of the filter to remove
        """
        # remove from widget list
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget:
                if hasattr(widget, 'uuid'):
                    if widget.uuid == uuid:
                        item_d = self.layout.takeAt(i)
                        item_d.widget().deleteLater()
                        break

    def widgets(self):
        widgets_ = list()
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            if widget:
                if hasattr(widget, 'uuid'):
                    widgets_.append(widget)
                    #widgets_.append(widget.process_widget)
        return widgets_


