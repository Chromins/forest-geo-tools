'''Работа с лесоустроительными данными и категориальными растрами'''
import geopandas as gpd
from config import FOREST_DIR, OUTPUT_DIR
import rasterio
import numpy as np
import pandas as pd
from points import load_points


def sample_raster(points, raster_path):
    values = []
    coordinates = [point[1:] for point in points]
    with rasterio.open(raster_path) as src:
        for value in src.sample(coordinates, indexes=1, masked=True):
            if not np.ma.is_masked(value[0]):
                values.append(int(value[0]))
            else:
                values.append(pd.NA)
    df = pd.DataFrame(points, columns=['id', 'lon', 'lat'])
    df['raster_value'] = pd.array(values, dtype='Int64')
    return df


def decode_species(sampled_df, species_legend):

    df = pd.merge(sampled_df,
                  species_legend[['Value', 'species', 'AGE']],
                  left_on='raster_value',
                  right_on='Value',
                  how='left',
                  validate='many_to_one'
                  )

    return df

def prepare_species_output(df):

    df['species_source'] = 'https://zenodo.org/records/6056054'
    df['species_year'] = 2009
    df['species_resolution_arcsec'] = 5
    df['species_status'] = 'ok'
    no_data = df['raster_value'].isna()
    unknown = df['species'].isna() & df['raster_value'].notna()
    df.loc[no_data, 'species_status'] = 'no_data'
    df.loc[unknown, 'species_status'] = 'unknown_value'

    columns = [
        'id',
        'lon',
        'lat',
        'species',
        'species_source',
        'species_year',
        'species_resolution_arcsec',
        'species_status',
    ]

    return df[columns]


def species_processing(points, raster_path, species_legend):

    sampled_df = sample_raster(points, raster_path)

    df = decode_species(sampled_df, species_legend)
    df = prepare_species_output(df)

    return df


if __name__ == '__main__':

    points = load_points()

    raster_path = FOREST_DIR / 'BEF_RUS' / 'BCEF_RUS.tif'

    species_legend = gpd.read_file(
        FOREST_DIR / 'BEF_RUS' / 'BCEF_RUS.tif.vat.dbf',
        ignore_geometry=True
    )

    df = species_processing(points, raster_path, species_legend)

    df.to_csv(
        OUTPUT_DIR / 'tree_species.csv',
        index=False,
        encoding='utf-8-sig',
    )



