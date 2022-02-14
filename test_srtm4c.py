import pytest
import numpy as np
import os
import rasterio
import srtm4c
import srtm4

@pytest.mark.parametrize(
    "bound, datum, expected_shape",
    [
     # bounds on a tile exactly
     ((20.0, 45.0 + 1.1 * srtm4c.RES, 25.0 - 1.1*srtm4c.RES, 50.0), "orthometric", (6000, 6000)),
     # in 2 tiles, one is all nan, does not exist
     ((-112, 16, -108, 18), "orthometric", (2401, 4802)),
     # bounds wrapping
     ((179, -20, 181, -19), "orthometric", (1201, 2401)),
     # bounds on normal region
     ((21.33, -3.78, 21.66, -2.97), "ellipsoidal", (973, 398)),
     ]
    )
def test_crop(bound, datum, expected_shape, tmp_path, monkeypatch):
    monkeypatch.setenv("SRTM4_CACHE", str(tmp_path))

    raster, transform, crs = srtm4c.crop(bound, datum=datum)
    assert raster.shape == expected_shape
    assert raster.dtype == np.float32

    # write to file
    dem_path = os.path.join(str(tmp_path), "dem.tif")
    srtm4c.write_crop_to_file(raster, transform, crs, dem_path)

    # re-read
    with rasterio.open(dem_path, 'r') as db:
        read_raster = db.read(1)

    mask = ~np.isnan(raster)
    assert np.all(read_raster[mask] == raster[mask]), "read raster different from written one"

    # test w.r.t query
    if datum == "ellipsoidal":
        raster_shape = raster.shape
        # get dem points in crs
        col, row = np.meshgrid(
            np.arange(raster_shape[1]), np.arange(raster_shape[0]))
        col = col.ravel()
        row = row.ravel()

        # Add 0.5 for pixel is area
        col = col + 0.5
        row = row + 0.5

        # to earth coordinates
        x, y = transform * (col, row)

        # query srtm4
        alts = np.reshape(srtm4.srtm4(x, y), raster_shape)

        np.testing.assert_allclose(raster[mask], alts[mask], atol=0, rtol=1e-2)
