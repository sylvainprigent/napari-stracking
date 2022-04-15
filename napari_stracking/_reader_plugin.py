import os
from qtpy import QtCore
from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel,
                            QPushButton, QLineEdit, QComboBox,
                            QFileDialog)
from stracking.io import read_tracks, read_particles


class SLoad(QWidget):
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

        # particles
        self.particles_file_edit = QLineEdit()
        browse_btn_p = QPushButton('...')
        browse_btn_p.released.connect(self.browse_particles)

        title_label = QLabel('Load particles')
        title_label.setMaximumHeight(50)
        layout.addWidget(title_label, 0, 0, 1, 2)
        layout.addWidget(self.particles_file_edit, 1, 0, 1, 1)
        layout.addWidget(browse_btn_p, 1, 1, 1, 1)
        import_btn_p = QPushButton('Open')
        import_btn_p.released.connect(self.load_particles)
        layout.addWidget(import_btn_p, 2, 0, 1, 2)

        # tracks
        self.tracks_file_edit = QLineEdit()
        browse_btn = QPushButton('...')
        browse_btn.released.connect(self.browse_tracks)

        title_label = QLabel('Load tracks')
        title_label.setMaximumHeight(50)
        layout.addWidget(title_label, 3, 0, 1, 2)
        layout.addWidget(self.tracks_file_edit, 4, 0)
        layout.addWidget(browse_btn, 4, 1)
        import_btn = QPushButton('Open')
        import_btn.released.connect(self.load_tracks)
        layout.addWidget(import_btn, 5, 0, 1, 2)
        layout.addWidget(QWidget(), 6, 0, 1, 2)
        self.setLayout(layout)

    def browse_particles(self):
        file = QFileDialog.getOpenFileName(self, "open file", "", "")
        self.particles_file_edit.setText(file[0])

    def browse_tracks(self):
        file = QFileDialog.getOpenFileName(self, "open file", "", "")
        self.tracks_file_edit.setText(file[0])

    def load_tracks(self):
        tracks = read_tracks(self.tracks_file_edit.text())
        self.viewer.add_tracks(tracks.data,
                               metadata=tracks.features,
                               properties=tracks.properties,
                               graph=tracks.graph,
                               scale=tracks.scale,
                               name=os.path.basename(self.tracks_file_edit.text())
                               )

    def load_particles(self):
        particles = read_particles(self.particles_file_edit.text())
        self.viewer.add_points(data=particles.data,
                               properties=particles.properties,
                               scale=particles.scale,
                               name=os.path.basename(self.particles_file_edit.text())
                               )
