import requests
import json

query = """
[out:json][timeout:25];
(
  node["amenity"="hospital"](around:100000,18.5204,73.8567);
  way["amenity"="hospital"](around:100000,18.5204,73.8567);
  relation["amenity"="hospital"](around:100000,18.5204,73.8567);
);
out center;
"""

r = requests.get('https://overpass-api.de/api/interpreter', params={'data': query}, headers={'User-Agent': 'HealthIntel/1.0'})
if r.status_code == 200:
    data = r.json()
    print(len(data.get('elements', [])))
else:
    print(r.status_code, r.text)
