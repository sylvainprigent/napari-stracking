import sys
from qtpy.QtWidgets import QApplication
import napari
from skimage.io import imread
from napari_stracking._sdetection_plugins import (SDetectorDog,
                                                  SDetectorDoh,
                                                  SDetectorLog)
from napari_stracking._sproperties_plugins import SSpotProperties
from napari_stracking._slinking_plugins import (SLinkerNearestNeighbor,
                                                SLinkerShortestPath)
from napari_stracking._sfeatures_plugins import STracksFeatures

from napari_stracking._sproperties_workers import (SSpotPropertiesWidget)


if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    image = '/Users/sprigent/Documents/code/napari/stracking/stracking/data/fake_tracks1.tif'
    napari_viewer = napari.view_image(imread(image), name='toto')

    widget = SLinkerShortestPath(napari_viewer)
    widget.show()

    #widget = SSpotPropertiesWidget(napari_viewer)
    #widget.show()
    #widget.state()

    sys.exit(app.exec_())
