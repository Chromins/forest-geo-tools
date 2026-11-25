'''Работа с лесоустроительными данными и категориальными растрами'''
import geopandas as gpd
from config import FOREST_DIR
import rasterio
import numpy as np

points = [
        (1, 130.660446, 42.533511),
        (2, 131.524632, 43.097469),
        (3, 130.800000, 42.660000),
        (4, 130.865945, 42.614981),
    ]

def sample_raster(points, raster_path):
    ids = [point[0] for point in points]
    coordinates = [point[1:] for point in points]

values = []
df = gpd.read_file(FOREST_DIR / 'BEF_RUS' /'BCEF_RUS.tif.vat.dbf', ignore_geometry=True)

with rasterio.open(FOREST_DIR / 'BEF_RUS' / 'BCEF_RUS.tif') as src:
    for value in src.sample(coordinates, indexes=1, masked=True):
        if not np.ma.is_masked(value[0]):
            values.append(int(value[0]))
    mask = df['Value'].isin(values)
    result = df.loc[mask, ['Value', 'ID_FOR', 'SPEC_MOD', 'species', 'AGE']]



