# SRTM4 (Shuttle Radar Topography Mission)

Download and parsing of SRTM4 elevation data.

[![PyPI version](https://img.shields.io/pypi/v/srtm4)](https://pypi.org/project/srtm4)

[Carlo de Franchis](mailto:carlo.de-franchis@cmla.ens-cachan.fr), Enric
Meinhardt, Gabriele Facciolo, CMLA 2018

# Installation and dependencies

The main source code repository for this project is https://github.com/centreborelli/srtm4.
It is written in Python. It is tested with Python 3.10, 3.11, 3.12 and 3.13.

`srtm4` requires `libtiff` development files. They can be installed with
`apt-get install libtiff-dev` (Ubuntu, Debian) or `brew install libtiff`
(macOS).

Once `libtiff` is installed, `srtm4` can be installed with `pip`:

    pip install srtm4

# Usage

In a Python interpreter:

    >>> import srtm4
    >>> longitude, latitude = 2, 48
    >>> altitude = srtm4.srtm4(longitude, latitude)
    >>> print(altitude)  # should be 174.613 (altitude in meters above the WGS84 ellipsoid)

In a shell:

    GEOID_PATH=data ./bin/srtm4 2 48

For the `crop` function, if pyproj complains about the download of file, you can fix it manually with the command:

    pyproj sync -v --file us_nga_egm96_15
