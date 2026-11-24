'''GeoPandas, векторные геоданные, пространственное объединение, справочники.'''

import geopandas as gpd
import pandas as pd
from config import SOIL_DIR, OUTPUT_DIR


def load_soil_data():

    soil_legend = pd.read_excel(
        SOIL_DIR / "soil_map_M2_5_legend-1.0.xls",
        engine="calamine"
    )

    soil_polygons = gpd.read_file(SOIL_DIR / "soil_map_M2_5-1.0" / 'soil_map_M2_5-1.0.shp')

    return soil_polygons, soil_legend


def create_geo_points(points):

    df = pd.DataFrame(
        points,
        columns=['id', 'lon', 'lat']
    )

    return gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['lon'], df['lat']),
        crs="EPSG:4326"
    )


def decode_soil_types(joined, soil_legend):

    df = pd.merge(joined,
                  soil_legend,
                  left_on='SOIL0',
                  right_on='SOIL_ID',
                  how='left',
                  validate='many_to_one'
                  )

    return df


def prepare_soil_output(df):

    df = df.rename(columns={
        'SOIL0': 'soil_code',
        'Descript': 'soil_name'
    })

    df['soil_code'] = df['soil_code'].replace(-9999, pd.NA)
    df['soil_code'] = df['soil_code'].astype('Int64')
    df['soil_source'] = 'https://egrpr.esoil.ru/content/1DB.html'
    df['soil_scale'] = 2500000
    df['soil_status'] = 'ok'

    na = df['soil_name'].isna()
    duplicates = df['id'].duplicated(keep=False)

    df.loc[na, 'soil_status'] = 'no_data'
    df.loc[duplicates, 'soil_status'] = 'ambiguous'

    columns = [
        'id',
        'lon',
        'lat',
        'soil_code',
        'soil_name',
        'soil_source',
        'soil_scale',
        'soil_status'
    ]

    return df[columns]


def soil_processing(points, soil_polygons, soil_legend):
    geo_points = create_geo_points(points)

    joined = gpd.sjoin(geo_points,
                       soil_polygons,
                       how='left',
                       predicate='intersects'
                       )

    df = decode_soil_types(joined, soil_legend)

    prepared_df = prepare_soil_output(df)

    return prepared_df

if __name__ == '__main__':

    points = [
        (1, 130.660446, 42.533511),
        (2, 131.524632, 43.097469),
        (3, 130.800000, 42.660000),
        (4, 130.865945, 42.614981),
    ]

    soil_polygons, soil_legend = load_soil_data()

    df = soil_processing(points, soil_polygons, soil_legend)

    df.to_csv(
        OUTPUT_DIR / 'soils.csv',
        index=False,
        encoding='utf-8-sig'
    )



