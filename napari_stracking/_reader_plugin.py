import os
import qtpy.QtCore
from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel,
                            QPushButton, QLineEdit, QComboBox,
                            QFileDialog)
from stracking.io import read_tracks


class STracksReader(QWidget):
    """Dock widget to read tracks

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        layout = QGridLayout()

        self.file_edit = QLineEdit()
        browse_btn = QPushButton('...')
        browse_btn.released.connect(self.browse)

        import_btn = QPushButton('Open')
        import_btn.released.connect(self.open)

        layout.addWidget(self.file_edit, 0, 0)
        layout.addWidget(browse_btn, 0, 1)
        layout.addWidget(import_btn, 1, 0, 1, 2)
        layout.addWidget(QWidget(), 2, 0, 1, 2, qtpy.QtCore.Qt.AlignTop)
        self.setLayout(layout)

    def browse(self):
        file = QFileDialog.getOpenFileName(self, "open file", "", "")
        self.file_edit.setText(file[0])

    def open(self):
        tracks = read_tracks(self.file_edit.text())
        #self.viewer.add_tracks(tracks.data,
        #                       features=tracks.features,
        #                       properties=tracks.properties,
        #                       graph=tracks.graph,
        #                       scale=tracks.scale,
        #                       name=os.path.basename(self.file_edit.text()))
        print('features=', tracks.features)
        print('properties=', tracks.properties)
        print('scale=', tracks.scale)
        self.viewer.add_tracks(tracks.data, metadata=tracks.features,
                               properties=tracks.properties,
                               graph=tracks.graph,
                               scale=tracks.scale,
                               name=os.path.basename(self.file_edit.text()))
