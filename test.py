import requests

def test_optimize_route():
    url = 'http://localhost:5000/optimize_route'
    payload = {
        "uuid": "12345",
        "startPosition": {"latitude": 34.052235, "longitude": -118.243683},
        "parameters": {"optimizeForFuel": False, "optimizeForTime": True, "minimizeStops": False},
        "points": [
            {"designation": "Point A", "latitude": 34.052235, "longitude": -118.243683},
            {"designation": "Point B", "latitude": 34.052235, "longitude": -118.243684}
        ]
    }
    response = requests.post(url, json=payload)
    print(response.json())

if __name__ == "__main__":
    test_optimize_route()



def test_generate_map_url():
    url = 'http://localhost:5000/generate_map_url'
    payload = {
        "uuid": "12345",
        "startPosition": {"latitude": 34.052235, "longitude": -118.243683},
        "points": [
            {"latitude": 34.052235, "longitude": -118.243683, "order": 1},
            {"latitude": 34.052236, "longitude": -118.243684, "order": 2}
        ]
    }
    response = requests.post(url, json=payload)
    print(response.json())

if __name__ == "__main__":
    test_generate_map_url()