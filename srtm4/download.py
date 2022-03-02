#!/usr/bin/env python
# vim: set fileencoding=utf-8
# pylint: disable=C0103

"""
Module to download terrain digital elevation models from the SRTM 90m DEM.

Copyright (C) 2016, Carlo de Franchis <carlo.de-franchis@ens-cachan.fr>
"""

from __future__ import print_function
import zipfile
import sys
import os

import requests
from requests.adapters import HTTPAdapter, Retry, RetryError
import filelock

SRTM_URL = 'https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF'


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
