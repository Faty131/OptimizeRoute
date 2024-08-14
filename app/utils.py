import os
import requests
from flask import jsonify
from datetime import datetime
import pytz

def get_formatted_date():
    tz = pytz.timezone('Africa/Casablanca')
    date = datetime.now(tz)
    formatted_date = date.strftime('%Y-%m-%dT%H:%M:%S')
    offset = date.strftime('%z')
    encoded_offset = '%2B' + offset[1:] if offset.startswith('+') else offset
    return f"{formatted_date}{encoded_offset}"

def optimize_route(request):
    try:
        # Récupérer les données de la requête
        data = request.json
        here_api_key = os.getenv('HERE_API_KEY')
        uuid = data.get('uuid')
        start_position = data.get('startPosition')
        parameters = data.get('parameters', {})
        points = data.get('points', [])

        # Déterminer les paramètres d'optimisation
        improve_for = 'time'
        mode = 'fastest;car;traffic:enabled'
        clustering = ''

        if parameters.get('optimizeForFuel'):
            improve_for = 'distance'
        elif parameters.get('optimizeForTime'):
            improve_for = 'time'

        if parameters.get('minimizeStops'):
            clustering = 'clustering=drivingDistance:500'

        # Construire l'URL de l'API
        waypoints = '&'.join(
            f'destination{index + 1}={requests.utils.quote(f"{point['designation']};{point['latitude']},{point['longitude']}")}'
            for index, point in enumerate(points)
        )
        departure_time = get_formatted_date()
        api_url = (
            f"https://wps.hereapi.com/v8/findsequence2?start={start_position['latitude']},{start_position['longitude']}"
            f"&{waypoints}&improveFor={improve_for}&mode={mode}&departure={departure_time}"
            f"{'&' + clustering if clustering else ''}&apikey={here_api_key}"
        )

        # Appeler l'API HERE
        response = requests.get(api_url)
        response.raise_for_status()  # Lancer une exception pour les erreurs HTTP
        response_data = response.json()

        # Journaliser la réponse de l'API
        print(f"API Response: {response_data}")

        # Traiter les points optimisés
        optimized_waypoints = response_data['results'][0]['waypoints']
        optimized_points = [
            {**point, 'order': index + 1}
            for index, wp in enumerate(optimized_waypoints[1:])
            for point in points if point['designation'] == wp['id']
        ]

        # Convertir les valeurs de distance et durée
        distance = int(response_data['results'][0]['distance'])
        duration = int(response_data['results'][0]['time'])

        result = {
            'uuid': uuid,
            'distance': distance / 1000,  # Convertir mètres en kilomètres
            'duration': duration / 60,    # Convertir secondes en minutes
            'startPosition': start_position,
            'parameters': parameters,
            'points': optimized_points,
        }

        return jsonify(result)
    except requests.exceptions.RequestException as req_err:
        print(f'HTTP Request Error: {req_err}')
        return jsonify({'error': 'HTTP Request Error'}), 500
    except ValueError as val_err:
        print(f'Value Error: {val_err}')
        return jsonify({'error': str(val_err)}), 400
    except Exception as e:
        print(f'Unexpected Error: {e}')
        return jsonify({'error': 'Error optimizing route'}), 500


def generate_map_url(request):
    try:
        data = request.json
        uuid = data.get('uuid')
        start_position = data.get('startPosition')
        points = data.get('points', [])

        if not uuid or not start_position or not points or not isinstance(points, list) or len(points) == 0:
            return jsonify({'error': 'Invalid input format'}), 400

        ordered_points = sorted(points, key=lambda p: p.get('order', 0))
        origin = f"{start_position['latitude']},{start_position['longitude']}"
        destination = f"{ordered_points[-1]['latitude']},{ordered_points[-1]['longitude']}"
        waypoints = '|'.join(f"{p['latitude']},{p['longitude']}" for p in ordered_points[:-1])

        map_url = (
            f"https://www.google.com/maps/dir/?api=1&origin={origin}"
            f"&destination={destination}&waypoints={waypoints}"
        )

        return jsonify({'map_url': map_url})
    except Exception as e:
        print(f'Error generating map URL: {e}')
        return jsonify({'error': 'Error generating map URL'}), 500
