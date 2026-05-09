import requests

def test_radius(radius):
    r = requests.post(
        'http://localhost:8000/api/recommend-hospitals',
        json={
            'latitude': 18.5204,
            'longitude': 73.8567,
            'disease_category': 'heart_disease',
            'radius_km': radius
        }
    )
    if r.status_code == 200:
        data = r.json()
        print(f"Radius {radius}km: Found {data.get('total_found')} hospitals using {data.get('source')} in {data.get('calls_made')} calls.")
    else:
        print(f"Error for {radius}km: {r.text}")

test_radius(10)
test_radius(30)
test_radius(60)
test_radius(100)
