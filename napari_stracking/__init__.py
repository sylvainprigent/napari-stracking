
try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


from ._dock_widget import napari_experimental_provide_dock_widget

#from ._sdetection_plugins import (SDetectorDog, SDetectorDoh,
#                                  SDetectorLog)
#from ._slinking_plugins import (SLinkerShortestPath)
#from ._sproperties_plugins import SParticlesProperties
#from ._sfeatures_plugins import STracksFeatures
#from ._strackfilter_plugins import SFilterTrack
#
#__all__ = ['SDetectorDog',
#           'SDetectorDoh',
#           'SDetectorLog',
#           'SLinkerShortestPath',
#           'SParticlesProperties',
#           'STracksFeatures',
#           'SFilterTrack']
