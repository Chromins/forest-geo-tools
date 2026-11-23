import requests
import numpy as np

url = "https://api.opentopodata.org/v1/srtm30m"
lat = 42.9901
lon = 131.2438

dlat = 0.00027
dlon = 0.00037

geo_map = []

for dy in (-1, 0, 1):
    new_lat = lat + dy * dlat

    for dx in (-1, 0, 1):
        new_lon = lon + dx * dlon
        geo_map.append((new_lat, new_lon))

result = []

for point in geo_map:
    result.append(','.join(map(str, point)))

locations = '|'.join(result)

response = requests.get(url,params={'locations': locations}, timeout=15)
response.raise_for_status()
data = response.json()
heights = []
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

print(heights)