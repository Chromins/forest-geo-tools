

import requests
import numpy as np


url = "https://api.opentopodata.org/v1/srtm30m"

geo_map = []

def fetch_elevation(points):
    locations = "|".join(f"{lat},{lon}" for _, lon, lat in points)
    response = requests.get(url, params={'locations': locations}, timeout=15)
    response.raise_for_status()
    data = response.json()
    heights = []

    for point, result in zip(points, data['results']):
        heights.append((point[0], result['elevation']))

    return np.array(heights)

points = [
    (1, 130.660446, 42.533511),
    (2, 131.524632, 43.097469),
    (3, 130.800000, 42.660000),
    (4, 130.865945, 42.614981),
]

elevations = fetch_elevation(points)
for dy in (-1, 0, 1):
    new_lat = lat + dy * dlat

    for dx in (-1, 0, 1):
        new_lon = lon + dx * dlon
        geo_map.append((new_lat, new_lon))

for point in geo_map:
    result.append(','.join(map(str, point)))


for result, point in zip(data['results'], geo_map):
    heights.append(result['elevation'])

if len(heights) != 9 and None in heights:
    raise ValueError('Height is out of range')

heights = np.array(heights)
heights = np.reshape(heights, (3,3))
hy = 30
dx = (heights[1][2] - heights[1][0]) / (2 * hy)
dy = (heights[2][1] - heights[0][1]) / (2 * hy)
dz = np.degrees(np.arctan(np.sqrt((dy ** 2 + dx ** 2))))
