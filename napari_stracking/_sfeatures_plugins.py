from ._splugin import SNapariPlugin
from ._sfeatures_workers import (STracksFeaturesWidget,
                                 STracksFeaturesWorker)


class STracksFeatures(SNapariPlugin):
    """ Calculate features of tracks

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S Tracks Features'
        self.widget = STracksFeaturesWidget(napari_viewer)
        self.worker = STracksFeaturesWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.fill_widget_resize = 0
        self.init_ui()
        self.set_advanced(False)
