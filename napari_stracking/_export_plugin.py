import os
from qtpy import QtCore
from qtpy.QtWidgets import (QWidget, QGridLayout, QLabel,
                            QPushButton, QLineEdit, QComboBox,
                            QFileDialog)
import napari
from stracking.containers import STracks, SParticles
from stracking.io import write_tracks, write_particles


class SExport(QWidget):
    """Dock widget to read tracks

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer
        self.viewer.events.layers_change.connect(self._on_layer_change)
        layout = QGridLayout()

        # export particles
        particles_title = QLabel('Particles')
        particles_title.setMaximumHeight(50)
        self._particles_layers = QComboBox()
        particles_export_btn = QPushButton('Export')
        particles_export_btn.released.connect(self._save_particles)
        # export tracks
        tracks_title = QLabel('Tracks')
        tracks_title.setMaximumHeight(50)
        self._tracks_layers = QComboBox()
        tracks_export_btn = QPushButton('Export')
        tracks_export_btn.released.connect(self._save_tracks)

        layout.addWidget(particles_title, 0, 0, 1, 2)
        layout.addWidget(self._particles_layers, 1, 0, 1, 2)
        layout.addWidget(particles_export_btn, 2, 1)
        layout.addWidget(tracks_title, 3, 0, 1, 2)
        layout.addWidget(self._tracks_layers, 4, 0, 1, 2)
        layout.addWidget(tracks_export_btn, 5, 1)
        layout.addWidget(QWidget(), 6, 0, 1, 2, QtCore.Qt.AlignTop)
        self.setLayout(layout)
        self._on_layer_change(None)

    def _on_layer_change(self, e):
        # particles
        self._particles_layers.clear()
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.points.points.Points):
                self._particles_layers.addItem(layer.name)
        # tracks
        self._tracks_layers.clear()
        for layer in self.viewer.layers:
            if isinstance(layer, napari.layers.tracks.tracks.Tracks):
                self._tracks_layers.addItem(layer.name)

    def _save_particles(self):
        file = QFileDialog.getSaveFileName(self, 'Save File')
        if len(file) > 0:
            layer = self.viewer.layers[self._particles_layers.currentText()]
            particles = SParticles(data=layer.data, properties=layer.properties, scale=layer.scale)
            write_particles(file[0], particles)

    def _save_tracks(self):
        file = QFileDialog.getSaveFileName(self, 'Save File')
        if len(file) > 0:
            layer = self.viewer.layers[self._tracks_layers.currentText()]
            tracks = STracks(data=layer.data, properties=layer.properties,
                             graph=layer.graph, features=layer.metadata,
                             scale=layer.scale)
            format_ = 'st.json'
            if file[0].endswith('csv'):
                format_ = 'csv'
            write_tracks(file[0], tracks, format_)
