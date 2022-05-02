Developers
==========

Plugin Interface
----------------

STracking napari plugins implements a dedicated plugin interface for a custom management of the
progress bar, progress log and advanced mode. To implement a new STracking plugin, developers needs
to implement a ``SNapariPlugin`` class with a dedicated ``SNapariWidget`` for the graphical
interface and a ``SNapariWorker`` that link the plugin widget to the STracking class.

.. automodule:: napari_stracking._splugin
   :members:

Plugin to change a layer scale
------------------------------

.. automodule:: napari_stracking._scale_plugin
   :members:

Plugins for import and export
-----------------------------

.. automodule:: napari_stracking._reader_plugin
   :members:

.. automodule:: napari_stracking._export_plugin
   :members:

Detection plugins
-----------------

.. automodule:: napari_stracking._sdetection_plugins
   :members:

.. automodule:: napari_stracking._sdetection_workers
   :members:

Properties plugins
------------------

.. automodule:: napari_stracking._sproperties_plugins
   :members:

.. automodule:: napari_stracking._sproperties_workers
   :members:

Linking plugins
---------------

.. automodule:: napari_stracking._slinking_plugins
   :members:

.. automodule:: napari_stracking._slinking_workers
   :members:

Features plugins
----------------

.. automodule:: napari_stracking._sfeatures_plugins
   :members:

.. automodule:: napari_stracking._sfeatures_workers
   :members:

Filters plugins
---------------

.. automodule:: napari_stracking._strackfilter_plugins
   :members:

.. automodule:: napari_stracking._strackfilter_workers
   :members:
