from ._splugin import SNapariPlugin
from ._slinking_workers import (SLinkerNearestNeighborWidget,
                                SLinkerNearestNeighborWorker,
                                SLinkerShortestPathWidget,
                                SLinkerShortestPathWorker,
                                )


class SLinkerNearestNeighbor(SNapariPlugin):
    """Dock widget to link detections using the nearest neighbor algorithm

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S Linker Nearest Neighbor'
        self.widget = SLinkerNearestNeighborWidget(napari_viewer)
        self.worker = SLinkerNearestNeighborWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.fill_widget_resize = 0
        self.init_ui()
        self.set_advanced(True)


class SLinkerShortestPath(SNapariPlugin):
    """Dock widget to calculate spot properties

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S Linker Shortest Path'
        self.widget = SLinkerShortestPathWidget(napari_viewer)
        self.worker = SLinkerShortestPathWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.fill_widget_resize = 0
        self.init_ui()
        self.set_advanced(True)
