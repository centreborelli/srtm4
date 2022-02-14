import pytest
import numpy as np


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
    import srtm4

    altitude = srtm4.srtm4(longitude, latitude)
    assert altitude == exp_altitude
