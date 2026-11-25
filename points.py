'''Убираем дублирование координат в модулях'''

import pandas as pd
from config import POINTS_FILE

def load_points():
    df = pd.read_excel(POINTS_FILE, engine='calamine')

    df = df.rename(columns={
        '№': 'id',
        'Долгота (EPSG:4326)': 'lon',
        'Широта (EPSG:4326)': 'lat'
    })

    df = df[['id', 'lon', 'lat']]

    df = df.dropna(subset=['lon', 'lat'])

    points = list(df.itertuples(index=False, name=None))

    return points

if __name__ == '__main__':
    points = load_points()
    print(points)
    print(len(points))