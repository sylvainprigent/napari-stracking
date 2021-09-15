Guide
=====

This page aims at guiding the `napari-stracking` user step by step to build a pipeline for particles tracking in 2D+t or
3D+t images. A classical particles tracking pipeline is made of 5 sequential steps:

1. Particles detection frame by frame

.. image:: images/sdogdetector_res.png
   :width: 600

2. Particles properties calculation (optional)

.. image:: images/sparticlesproperties_res.png
   :width: 600

3. Particles linking

.. image:: images/slinkershortestpath_res.png
   :width: 600

4. Tracks features extraction (optional)

.. image:: images/stracksfeatures_res.png
   :width: 600

5. Tracks filtering (optional)

.. image:: images/sfiltertracks_res.png
   :width: 600

Particles detection
-------------------

The particles detection step is performed frame by frame to independently detect the particles in each time frame. Many
particles (or spots) detection algorithms have been proposed in the scientific literature. The choice of the most appropriate particles detector should be data
driven. Furthermore, the performance of a particles detector is sensitive to the image quality. An image denoising
pre-processing step is sometime needed to improve the particles detection.

Particles detections plugins availeble in **napari-stracking** are:

.. raw:: html

   <details>
   <summary><a>S Detector DoG</a></summary>

The Difference of Gaussian (DoG) detector enhance spots in images by calculated a filtered image which is the difference
between two versions of the image filtered with a gaussian filter with different sigmas
[`wiki DoG <https://en.wikipedia.org/wiki/Difference_of_Gaussians>`_].
The *S Detector DoG* plugin uses the implementation from `skimage DoG <https://scikit-image.org/docs/dev/api/skimage.feature.html#skimage.feature.blob_dog>`_

We start the *S Detector DoG* by opening *Plugins>Add Dock Widget>napari-stracking>S Detector DoG*

.. image:: images/sdogdetector.png
   :width: 600

The input is an image layer. If only one image layer is opened in Napari, it is automatically selected. Otherwise,
we select the image layer we want to process.
The *S Detector DoG* plugin has 3 parameters:

1. *Min sigma*: is the full width at half max intensity of the smallest particles we want to detect. The unit is the one
   specified in the image layer scale. In our example we set *4* since the spots are about 4 or 5 pixels width.
2. *Max sigma*: is the maximum width of the spots we want to detect. It is set similarly to *Min sigma*. In our example
   we set *5* since the spots are about 4 or 5 pixels width.
3. *Threshold*: is the minimum intensity of the spots (in the DoG filtered image) that are considered as particles of
   interest. This parameter is image dependent and can be chosen by trial and error. In our example, a threshold of
   *0.2* allows to detect all the particles without false alarm.

.. image:: images/sdogdetector_res.png
   :width: 600

.. raw:: html

   </details>

.. raw:: html

   <details>
   <summary><a>S Detector DoH </a></summary>

The Determinant of Hessian (DoH) detector is a multiscale spot detector that uses the determinant of the hessian matrix
of the input image
[`wiki DoH <https://en.wikipedia.org/wiki/Blob_detection#The_determinant_of_the_Hessian>`_].
The *S Detector DoH* plugin uses the implementation from `skimage DoH <https://scikit-image.org/docs/dev/api/skimage.feature.html#skimage.feature.blob_doh>`_

We start the *S Detector DoH* by opening *Plugins>Add Dock Widget>napari-stracking>S Detector DoH*

.. image:: images/sdohdetector.png
   :width: 600

The input is an image layer. If only one image layer is opened in Napari, it is automatically selected. Otherwise,
we select the image layer we want to process.
The *S Detector DoH* plugin has 4 parameters:

1. *Min sigma*: is the full width at half max intensity of the smallest particles we want to detect. The unit is the one
   specified in the image layer scale. In our example we set *4* since the spots are about 4 or 5 pixels width.
2. *Max sigma*: is the maximum width of the spots we want to detect. It is set similarly to *Min sigma*. In our example
   we set *5* since the spots are about 4 or 5 pixels width.
3. *Num sigma*: is the number of sigmas used for the multi-scale analysis. In out example we set 2 since the spots are
   almost all the same size.
4. *Threshold*: is the minimum intensity of the spots (in the DoH filtered image) that are considered as particles of
   interest. This parameter is image dependent and can be chosen by trial and error. In our example, a threshold of
   *0.01* allows to detect all the particles without false alarm.

.. image:: images/sdohdetector_res.png
   :width: 600

.. raw:: html

   </details>


.. raw:: html

   <details>
   <summary><a>S Detector LoG </a></summary>

The Laplacian of Gaussian (LoG) detector is a multi-scale spot detector that uses the laplacian operator on the input
image filtered with a Gaussian filter to enhance spots. The scale is determined by the size of the Gaussian filter.
[`wiki LoG <https://en.wikipedia.org/wiki/Blob_detection#The_Laplacian_of_Gaussian>`_].
The *S Detector LoG* plugin uses the implementation for `skimage LoG <https://scikit-image.org/docs/dev/api/skimage.feature.html#skimage.feature.blob_log>`_

To start the *S Detector LoG* open *Plugins>Add Dock Widget>napari-stracking>S Detector LoG*

.. image:: images/slogdetector.png
   :width: 600

The input is an image layer. If only one image layer is opened in Napari, it is automatically selected. Otherwise,
we select the image layer we want to process.
The *S Detector LoG* plugin has 4 parameters:

1. *Min sigma*: is the full width at half max intensity of the smallest particles we want to detect. The unit is the one
   specified in the image layer scale. In our example we set *4* since the spots are about 4 or 5 pixels width.
2. *Max sigma*: is the maximum width of the spots we want to detect. It is set similarly to *Min sigma*. In our example
   we set *5* since the spots are about 4 or 5 pixels width.
3. *Num sigma*: is the number of sigmas used for the multi-scale analysis. In out example we set 2 since the spots are
   almost all the same size.
4. *Threshold*: is the minimum intensity of the spots (in the LoG filtered image) that are considered as particles of
   interest. This parameter is image dependent and can be chosen by trial and error. In our example, a threshold of
   *0.2* allows to detect all the particles without false alarm.

.. image:: images/slogdetector_res.png
   :width: 600

.. raw:: html

   </details>


Particles properties
--------------------

The particles properties plugin allows to calculate properties of each particles (mean intensity for example). This
step is not mandatory, but can be very useful for the tracks analysis depending on the scientific application. To ease
the properties calculation, all the properties are grouped in a single plugin called *S Particles Properties*.

To open the particles properties plugin, open the plugin: *Plugins>Add Dock Widget>napari-stracking>S Detector DoG*

.. image:: images/sparticlesproperties.png
   :width: 600

This plugin needs two inputs:

1. *Image layer*: is the layer containing the raw image
2. *Points layer*: is the layer containing the detections (ie. the localisation of particles)

The plugin contains a list of possible features (or properties). To add a feature, we can select it in the list, and
then click on the *Add* button. The feature appears in the panel. In this example, we selected the *Intensity* feature
that needs one parameter: *Radius*. It is the radius used to calculate the particles intensity features. In this example
we then set radius to 2.5 since it is the average radius of our particles. We can then click on *Run*.

When the run is finished, there is no new layer in Napari since it is the input points layer that is updated. To
visualize the particles properties, we click on the *particles features* button:

.. image:: images/sparticlesproperties_res.png
   :width: 600

Particles linking
-----------------

Particles linking is the second main step of a particles tracking pipeline. It goal is to link close particles in
neighboring time frame to create the tracks. Several strategies have been proposed in the scientific literature to
perform this task. Available linkers in the stracking plugin suite are:

.. raw:: html

   <details>
   <summary><a>S Linker Shortest Path </a></summary>

The *S Linker Shortest Path* algorithm links the detected particles along the time frame using the following strategy.
First, a connection graph is created to connect all the neighboring particles of neighboring frames. Then, it
iteratively estimates the optimal trajectories by applying a shortest path algorithms with a graph pruning strategy. The
result is a set of trajectories. This tracker cannot handle split/merge events.

To open the *S Linker Shortest Path* plugin, open the plugin: *Plugins>Add Dock Widget>napari-stracking>S Linker Shortest Path*

.. image:: images/slinkershortestpath_res.png
   :width: 600

This plugin has one input which is the layer containing the particles detection. The two parameters are:

1. *max distance*: is the maximum distance that a particle can move between two consecutive frames. In our example we set
   100 since we are sure that our particles moves less that 100 pixels between two consecutive frames.
2. *gap*: is the number of neighboring frames used to search for a particle connection. In our example we set 1 since
   we do not have missing detection and then want to connect only with the next frame. If we expect having missing
   detections we can set a gap of 2 to enable connecting a particle from frame *n* to frame *n+2*

We then click, *Run* and when the processing is finished, we have a new layer with the tracks.

.. raw:: html

   </details>


Tracks features
---------------

The tracks features extraction plugin allows to measure feature of trajectories like length, distance... This
step is not mandatory, but very useful for the tracks analysis depending on the scientific application. To ease the
tracks features calculation, all the features are grouped in a single plugin called *S Tracks Feature*.

.. image:: images/stracksfeatures.png
   :width: 600

The input is a Tracks layer that contains the tracking result. Then, the *Add feature* menu allows to select the
features we want to extract. In our example we selected the following features:

1. *Length* is the number of time points in the track.
2. *Distance* is the full distance that the particles moved (frame by frame).
3. *Displacement* is the distance between the starting point and the ending point of the track.

Clicking *Run* starts the computation of the features. When the calculation is finished, clicking on the button
*tracks feature* allows to visualize the feature:

.. image:: images/stracksfeatures_res.png
   :width: 600

We can see that our 3 trajectories moves horizontally the same displacement, and almost the same distance during 5
frames.

Tracks filtering
----------------

Particles tracking pipelines are never perfect, and most of the time tracks with no interest are detected by the
tracking pipeline. For example they can be tracks of not moving object which are not interesting for some scientific
applications. the *S Filter Tracks* plugins is a post processing plugin that aims at removing tracks with
*unrealistic* properties (false positive).

To open the *S Filter Tracks* plugin, open the plugin: *Plugins>Add Dock Widget>napari-stracking>S Filter Tracks*

.. image:: images/sfiltertracks.png
   :width: 600

The input, is the layer containing the tracks. We can then select the features we want to filter with. In our fake
example we want here to remove the track with a *Distance* above to 60 pixels. To do so, we select the distance feature
and set a minimum value of 0, and a maximum value of 60. We then click *Run*. When it finished we have a new layer with
only 2 tracks since the tracks with a *Distance* above to 60 pixels has been removed:

.. image:: images/sfiltertracks_res.png
   :width: 600