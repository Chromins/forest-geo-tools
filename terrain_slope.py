from unittest import result
import ee
import requests
import numpy as np

ee.Authenticate()
ee.Initialize(project="omela-geo-tools")

# Цифровая модель поверхности с разрешением около 30 м
collection = ee.ImageCollection(
    "COPERNICUS/DEM/GLO30_2024_1"
).select("DEM")

# Объединяем географические фрагменты в единый слой
projection = collection.first().projection()
dem = collection.mosaic().setDefaultProjection(projection)

# Рассчитываем уклон поверхности в градусах
slope = ee.Terrain.slope(dem)

dem.reduceRegion()