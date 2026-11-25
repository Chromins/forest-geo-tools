import ee
import pandas as pd
from points import load_points
from config import OUTPUT_DIR, EE_PROJECT_ID


def create_terrain():
    collection = ee.ImageCollection(
        "COPERNICUS/DEM/GLO30_2024_1"
    ).select("DEM")

    projection = collection.first().projection()
    dem = collection.mosaic().setDefaultProjection(projection)

    slope = ee.Terrain.slope(dem)

    terrain = dem.addBands(slope)
    terrain = terrain.rename(['elevation_m', 'slope_deg'])

    return terrain


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


def terrain_processing(points, terrain):

    data = fetch_terrain(points, terrain)

    df = pd.DataFrame(data)
    df['terrain_source'] = 'COPERNICUS/DEM/GLO30_2024_1'
    df['sampling_scale_m'] = 30

    return df

if __name__ == "__main__":

    ee.Initialize(project=EE_PROJECT_ID)

    points = load_points()

    terrain = create_terrain()

    df = terrain_processing(points, terrain)

    df.to_csv(
        OUTPUT_DIR / 'terrain_slope.csv',
        index=False,
        encoding='utf-8-sig'
    )

    print(df.to_string(index=False))