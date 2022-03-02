from srtm4.download import get_srtm_tile
from srtm4.point import SRTM_DIR
from srtm4.point import srtm4_which_tile
from srtm4.point import srtm4

try:
    from srtm4.raster import crop
except ImportError:  # optional requirements were not installed
    pass
