import ee
import pandas as pd

ee.Initialize(project="omela-geo-tools")

points = [
    (1, 130.660446, 42.533511),
    (2, 131.524632, 43.097469),
    (3, 130.800000, 42.660000),
    (4, 130.865945, 42.614981),
]

def fetch_terrain(points, terrain):
    features = []

    for i, lon, lat in points:
        features.append(ee.Feature(
            ee.Geometry.Point([lon, lat]),
            {'id': i}
        ))
    features = ee.FeatureCollection(features)
    result = terrain.reduceRegions(
        collection=features,
        reducer=ee.Reducer.first(),
        scale=30
    )

    result = result.getInfo()
    data = []

    for point in result['features']:
        info = {}
        properties = point['properties']
        lon, lat = point['geometry']['coordinates']
        info['id'] = properties['id']
        info['lon'] = lon
        info['lat'] = lat
        info['elevation_m'] = properties.get('elevation_m')
        info['slope_deg'] = properties.get('slope_deg')
        data.append(info)

    return data

collection = ee.ImageCollection(
    "COPERNICUS/DEM/GLO30_2024_1"
).select("DEM")

# Объединяем географические фрагменты в единый слой
projection = collection.first().projection()
dem = collection.mosaic().setDefaultProjection(projection)

# Рассчитываем уклон поверхности в градусах
slope = ee.Terrain.slope(dem)

terrain = dem.addBands(slope)
terrain = terrain.rename(['elevation_m', 'slope_deg'])

data = fetch_terrain(points, terrain)

df = pd.DataFrame(data)
df['terrain_source'] = 'COPERNICUS/DEM/GLO30_2024_1'
df['sampling_scale_m'] = 30

df.to_csv('terrain_slope.csv', index=False)
