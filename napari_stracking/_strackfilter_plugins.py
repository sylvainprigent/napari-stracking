from ._splugin import SNapariPlugin
from ._strackfilter_workers import (STrackFilterWidget,
                                    STrackFilterWorker
                                    )


class SFilterTrack(SNapariPlugin):
    """Dock widget to link detections using the nearest neighbor algorithm

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S Filter Tracks'
        self.widget = STrackFilterWidget(napari_viewer)
        self.worker = STrackFilterWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.fill_widget_resize = 0
        self.init_ui()
        self.set_advanced(False)

