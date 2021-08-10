"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from napari_plugin_engine import napari_hook_implementation
from ._sdetection_plugins import (SDetectorDog, SDetectorDoh,
                                  SDetectorLog)
from ._slinking_plugins import (SLinkerShortestPath)
from ._sproperties_plugins import SParticlesProperties
from ._sfeatures_plugins import STracksFeatures
from ._strackfilter_plugins import SFilterTrack

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return [SParticlesProperties,
            SDetectorDog,
            SDetectorDoh,
            SDetectorLog,
            STracksFeatures,
            SLinkerShortestPath,
            SFilterTrack
            ]
