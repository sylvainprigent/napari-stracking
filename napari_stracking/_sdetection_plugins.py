from ._splugin import SNapariPlugin
from ._sdetection_workers import (SDogWorker, SDogWidget,
                                  SDohWorker, SDohWidget,
                                  SLogWidget, SLogWorker,
                                  SSegWidget, SSegWorker)


class SDetectorDog(SNapariPlugin):
    """Dock widget for DoG detection

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S DoG Detector'
        self.widget = SDogWidget(napari_viewer)
        self.worker = SDogWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.widget.enable.connect(self.set_enable)
        self.init_ui()
        self.widget.init_layer_list()


class SDetectorDoh(SNapariPlugin):
    """Dock widget for DoH detection

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S DoH Detector'
        self.widget = SDohWidget(napari_viewer)
        self.worker = SDohWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.widget.enable.connect(self.set_enable)
        self.init_ui()
        self.widget.init_layer_list()


class SDetectorLog(SNapariPlugin):
    """Dock widget for LoG detection

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S LoG Detector'
        self.widget = SLogWidget(napari_viewer)
        self.worker = SLogWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.widget.enable.connect(self.set_enable)
        self.init_ui()
        self.widget.init_layer_list()


class SDetectorSeg(SNapariPlugin):
    """Dock widget for detection from segmentation map

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S Seg Detector'
        self.widget = SSegWidget(napari_viewer)
        self.worker = SSegWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.widget.enable.connect(self.set_enable)
        self.init_ui()
        self.widget.init_layer_list()