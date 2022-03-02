import os
import subprocess

import numpy as np

from srtm4 import download

SRTM_DIR = os.getenv('SRTM4_CACHE')

if not SRTM_DIR:
    SRTM_DIR = os.path.join(os.path.expanduser('~'), '.srtm')

BIN = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bin')
GEOID = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')


def lon_lats_str(lon, lat):
    """
    Make a lon_lats string that can be passed to the
    srtm4 binaries

    Args:
        lon, lat: lists of longitudes and latitudes (same length), or single
            longitude and latitude

    Returns:
        str: lon_lats string
    """
    try:
        lon_lats = '\n'.join('{} {}'.format(a, b) for a, b in zip(lon, lat))
    except TypeError:
        lon_lats = '{} {}'.format(lon, lat)
    return lon_lats


def srtm4_which_tile(lon, lat):
    """
    Determine the srtm tiles needed to cover the (list of) point(s)
    by running the srtm4_which_tile binary

    Args:
        lon, lat: lists of longitudes and latitudes (same length), or single
            longitude and latitude

    Returns:
        list of str: list of srtm tile names
    """
    # run the srtm4_which_tile binary and feed it from stdin
    lon_lats = lon_lats_str(lon, lat)
    p = subprocess.Popen(['srtm4_which_tile'], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         env={'PATH': BIN, 'SRTM4_CACHE': SRTM_DIR})
    outs, errs = p.communicate(input=lon_lats.encode())

    # read the list of needed tiles
    srtm_tiles = outs.decode().split()
    return srtm_tiles


def srtm4(lon, lat):
    """
    Gives the SRTM height of a (list of) point(s).

    Args:
        lon, lat: lists of longitudes and latitudes (same length), or single
            longitude and latitude

    Returns:
        height(s) in meters above the WGS84 ellipsoid (not the EGM96 geoid)
    """
    # get the names of srtm_tiles needed
    srtm_tiles = srtm4_which_tile(lon, lat)

    # download the tiles if not already there
    for srtm_tile in set(srtm_tiles):
        download.get_srtm_tile(srtm_tile, SRTM_DIR)

    # run the srtm4 binary and feed it from stdin
    lon_lats = lon_lats_str(lon, lat)
    p = subprocess.Popen(['srtm4'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         env={'PATH': BIN,
                              'SRTM4_CACHE': SRTM_DIR,
                              'GEOID_PATH': GEOID})
    outs, errs = p.communicate(input=lon_lats.encode())

    # return the altitudes
    alts = list(map(float, outs.decode().split()))
    return alts if isinstance(lon, (list, np.ndarray)) else alts[0]
