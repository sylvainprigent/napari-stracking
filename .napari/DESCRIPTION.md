# Description

The STracking suite provides a set of plugins for particles tracking in 2D+t and 3D+t images. 
A classical particles tracking pipeline is made of 5 sequential steps:

* Particles detection frame by frame

![img](https://raw.githubusercontent.com/sylvainprigent/napari-stracking/main/docs/images/sdogdetector_res.png)


* Particles properties calculation (optional)

![img](https://raw.githubusercontent.com/sylvainprigent/napari-stracking/main/docs/images/sparticlesproperties_res.png?raw=true)


* Particles linking

![img](https://raw.githubusercontent.com/sylvainprigent/napari-stracking/main/docs/images/slinkershortestpath_res.png?raw=true)


* Tracks features extraction (optional)

![img](https://raw.githubusercontent.com/sylvainprigent/napari-stracking/main/docs/images/stracksfeatures_res.png?raw=true)


* Tracks filtering (optional)

![img](https://raw.githubusercontent.com/sylvainprigent/napari-stracking/main/docs/images/sfiltertracks_res.png?raw=true)


## Installation

You can install `napari-stracking` via [pip]:

    pip install napari-stracking

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [GNU GPL v3.0] license,
"napari-tracks-reader" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin
[file an issue]: https://github.com/sylvainprigent/napari-strcking/issues
[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/