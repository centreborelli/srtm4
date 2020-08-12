#!/usr/bin/env python
# vim: set fileencoding=utf-8
# pylint: disable=C0103

"""
Module to download terrain digital elevation models from the SRTM 90m DEM.

Copyright (C) 2016, Carlo de Franchis <carlo.de-franchis@ens-cachan.fr>
"""

from __future__ import print_function
import subprocess
import zipfile
import sys
import os

import numpy as np
import requests
from requests.adapters import HTTPAdapter, Retry, RetryError
import filelock

BIN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
GEOID = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

SRTM_DIR = os.getenv('SRTM4_CACHE')
if not SRTM_DIR:
    SRTM_DIR = os.path.join(os.path.expanduser('~'), '.srtm')

SRTM_URL = 'http://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF'


def _requests_retry_session(
        retries=5,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504),
):
    """
    Makes a requests object with built-in retry handling with
    exponential back-off on 5xx error codes.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def download(to_file, from_url):
    """
    Download a file from the internet.

    Args:
        to_file: path where to store the downloaded file
        from_url: url of the file to download

    Raises:
        RetryError: if the `get` call exceeds the number of retries
            on 5xx codes
        ConnectionError: if the `get` call does not return a 200 code
    """
    # Use a requests session with retry logic because the server at
    # SRTM_URL sometimes returns 503 responses when overloaded
    session = _requests_retry_session()
    r = session.get(from_url, stream=True)
    if not r.ok:
        raise ConnectionError(
            "Response code {} received for url {}".format(r.status_code, from_url)
        )
    file_size = int(r.headers['content-length'])
    print("Downloading: {} Bytes: {}".format(to_file, file_size),
          file=sys.stderr)

    with open(to_file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def get_srtm_tile(srtm_tile, out_dir):
    """
    Download and unzip an srtm tile from the internet.

    Args:
        srtm_tile: string following the pattern 'srtm_%02d_%02d', identifying
            the desired strm tile
        out_dir: directory where to store and extract the srtm tiles
    """
    output_dir = os.path.abspath(os.path.expanduser(out_dir))
    try:
        os.makedirs(output_dir)
    except OSError:
        pass

    srtm_zip_download_lock = os.path.join(output_dir, 'srtm_zip.lock')
    srtm_tif_write_lock = os.path.join(output_dir, 'srtm_tif.lock')

    if os.path.exists(os.path.join(output_dir, '{}.tif'.format(srtm_tile))):
        # the tif file is either being written or finished writing
        # locking will ensure it is not being written.
        # Also by construction we won't write on something complete.
        lock_tif = filelock.FileLock(srtm_tif_write_lock)
        lock_tif.acquire()
        lock_tif.release()
        return

    # download the zip file
    srtm_tile_url = '{}/{}.zip'.format(SRTM_URL, srtm_tile)
    zip_path = os.path.join(output_dir, '{}.zip'.format(srtm_tile))

    lock_zip = filelock.FileLock(srtm_zip_download_lock)
    lock_zip.acquire()

    if os.path.exists(os.path.join(output_dir, '{}.tif'.format(srtm_tile))):
        # since the zip lock is returned after the tif lock
        # if we end up here, it means another process downloaded the zip
        # and extracted it.
        # No need to wait on lock_tif
        lock_zip.release()
        return

    if os.path.exists(zip_path):
        print('zip already exists')
        # Only possibility here is that the previous process was cut short

    try:
        download(zip_path, srtm_tile_url)
    except (ConnectionError, RetryError) as e:
        lock_zip.release()
        raise e

    lock_tif = filelock.FileLock(srtm_tif_write_lock)
    lock_tif.acquire()

    # extract the tif file
    if zipfile.is_zipfile(zip_path):
        z = zipfile.ZipFile(zip_path, 'r')
        z.extract('{}.tif'.format(srtm_tile), output_dir)
    else:
        print('{} not available'.format(srtm_tile))

    # remove the zip file
    os.remove(zip_path)

    # release locks
    lock_tif.release()
    lock_zip.release()


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
        get_srtm_tile(srtm_tile, SRTM_DIR)

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
