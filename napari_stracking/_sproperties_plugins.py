from ._splugin import SNapariPlugin
from ._sproperties_workers import (SSpotPropertiesWidget,
                                   SSpotPropertiesWorker)


class SParticlesProperties(SNapariPlugin):
    """Dock widget to calculate spot properties

    Parameters
    ----------
    napari_viewer: Viewer
        Napari viewer

    """
    def __init__(self, napari_viewer):
        super().__init__(napari_viewer)
        self.title = 'S Particles Properties'
        self.widget = SSpotPropertiesWidget(napari_viewer)
        self.worker = SSpotPropertiesWorker(napari_viewer, self.widget)
        self.widget.advanced.connect(self.set_advanced)
        self.fill_widget_resize = 0
        self.init_ui()
        self.set_advanced(False)

