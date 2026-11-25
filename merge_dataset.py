'''Итоговый CSV и Excel, контроль качества и воспроизводимости'''

import pandas as pd
import numpy as np

from config import OUTPUT_DIR
from points import load_points


terrain = pd.read_csv(OUTPUT_DIR / 'terrain_slope.csv')
forest = pd.read_csv(OUTPUT_DIR / 'forest_typology.csv')
soil = pd.read_csv(OUTPUT_DIR / 'soils.csv')
species = pd.read_csv(OUTPUT_DIR / 'tree_species.csv')

datasets = {
    'terrain': terrain,
    'forest': forest,
    'soil': soil,
    'species': species
}

df = pd.DataFrame(
    load_points(),
    columns=['id', 'lon', 'lat']
)

def merge_datasets(df, datasets):

    for name, dataset in datasets.items():
        if not df['id'].is_unique or df['id'].isna().any():
            raise ValueError('Некорректные ID в исходных точках')
        if not dataset['id'].is_unique:
            raise ValueError(f'{name}: обнаружены повторяющиеся ID')
        if set(df['id']) != set(dataset['id']):
            raise ValueError(f'{name}: наборы ID не совпадают')

        check = df[['id', 'lon', 'lat']].merge(
            dataset[['id', 'lon', 'lat']],
            on='id',
            validate='one_to_one'
        )

        lon_ok = np.allclose(
            check['lon_x'],
            check['lon_y'],
            rtol=0,
            atol=1e-8
        )

        lat_ok = np.allclose(
            check['lat_x'],
            check['lat_y'],
            rtol=0,
            atol=1e-8
        )

        if not lon_ok or not lat_ok:
            raise ValueError(f'{name}: обнаружены несовпадающие координаты!')
        df = df.merge(
            dataset.drop(columns=['lon', 'lat']),
            on='id',
            how='left',
            validate='one_to_one'
        )

    return df

result = merge_datasets(df, datasets)

result.to_csv(
    OUTPUT_DIR / 'forest_dataset.csv',
    index=False,
    encoding='utf-8-sig'
)
