import pytest
import numpy as np
import srtm4

@pytest.mark.parametrize(
    "longitude, latitude, exp_altitude",
    [
        (2, 48, 174.613),
        ([2, 2], [48, 48], [174.613, 174.613]),
        (np.array([2, 2]), np.array([48, 48]), [174.613, 174.613]),
    ],
)
def test_srtm4(longitude, latitude, exp_altitude, tmp_path, monkeypatch):
    monkeypatch.setenv("SRTM4_CACHE", str(tmp_path))
    
    altitude = srtm4.srtm4(longitude, latitude)
    assert altitude == exp_altitude


@pytest.mark.parametrize(
    "bound, datum, expected_shape",
    [
     # bounds on a tile exactly
     ((20.0, 45.0 + 1.1 * srtm4.RES, 25.0 - 1.1*srtm4.RES, 50.0), "orthometric", (6000, 6000)),
     # in 2 tiles, one is all nan, does not exist
     ((-112, 16, -108, 18), "orthometric", (2401, 4802)),
     # bounds wrapping
     ((179, -20, 181, -19), "orthometric", (1201, 2401)),
     # bounds on normal region
     ((21.33, -3.78, 21.66, -2.97), "orthometric", (973, 398)),
     ]
    )
def test_crop(bound, datum, expected_shape, tmp_path, monkeypatch):
    monkeypatch.setenv("SRTM4_CACHE", str(tmp_path))
    raster, transform, crs = srtm4.crop(bound, datum=datum)
    assert raster.shape == expected_shape