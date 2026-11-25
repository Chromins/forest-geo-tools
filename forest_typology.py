import ee
import pandas as pd
import numpy as np
from points import load_points
from config import OUTPUT_DIR, EE_PROJECT_ID


def create_forest():

    collection = ee.ImageCollection(
        "projects/nature-trace/assets/forest_typology/"
        "forest_typology_2020_v1_0_collection")

    return collection.mosaic()

def fetch_forest(points, forest):
    forest_types = []

    for i, lon, lat in points:
        forest_types.append(ee.Feature(
            ee.Geometry.Point([lon, lat]),
            {'id': i}
        ))
    forest_types = ee.FeatureCollection(forest_types)
    result = forest.reduceRegions(
        collection=forest_types,
        reducer=ee.Reducer.first(),
        scale=10
    )

    result = result.getInfo()

    return result


def classify_forest(properties):
    scores = []

    classes = [
        'PrimaryForest',
        'NaturallyRegeneratingForest',
        'PlantedForest',
        'PlantationForest',
        'TreeCropsAndAgroforestry'
    ]

    for forest_type in classes:
        scores.append(properties.get(forest_type))

    if None in scores:
        return None, None

    scores = np.array(scores)

    OtherLand = 250 - np.sum(scores)
    classes.append('OtherLand')
    scores = np.append(scores, OtherLand)
    scores = scores / 250

    forest_type = classes[np.argmax(scores)]

    return forest_type, float(np.max(scores))


def process_forest(data):

    result = []

    for point in data['features']:
        point_data = {}
        properties = point['properties']
        lon, lat = point['geometry']['coordinates']
        forest_type, forest_score = classify_forest(properties)
        point_data['id'] = properties['id']
        point_data['lon'], point_data['lat'] = lon, lat
        point_data['forest_type'], point_data['forest_score'] = forest_type, forest_score
        result.append(point_data)

    return result


def forest_processing(points, forest):

    data = fetch_forest(points, forest)
    result = process_forest(data)

    df = pd.DataFrame(result)

    df['forest_source'] = 'Nature Trace ForTy v1.0'
    df['forest_year'] = 2020
    df['forest_scale_m'] = 10

    return df


if __name__ == '__main__':

    ee.Initialize(project=EE_PROJECT_ID)

    points = load_points()
    forest = create_forest()

    df = forest_processing(points, forest)


    df.to_csv(OUTPUT_DIR/ 'forest_typology.csv',
              index=False,
              encoding='utf-8-sig',)