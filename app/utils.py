import os
import requests
from flask import jsonify
from datetime import datetime
import pytz

class RouteOptimizer:
    def __init__(self, request_data):
        self.uuid = request_data.get('uuid')
        self.start_position = request_data.get('startPosition')
        self.parameters = request_data.get('parameters', {})
        self.points = request_data.get('points', [])
        self.here_api_key = os.getenv('HERE_API_KEY')
    
    def get_formatted_date(self):
        tz = pytz.timezone('Africa/Casablanca')
        date = datetime.now(tz)
        formatted_date = date.strftime('%Y-%m-%dT%H:%M:%S')
        offset = date.strftime('%z')
        encoded_offset = '%2B' + offset[1:] if offset.startswith('+') else offset
        return f"{formatted_date}{encoded_offset}"

    def optimize(self):
        try:
            improve_for = 'time'
            mode = 'fastest;car;traffic:enabled'
            clustering = ''

            if self.parameters.get('optimizeForFuel'):
                improve_for = 'distance'
            elif self.parameters.get('optimizeForTime'):
                improve_for = 'time'

            if self.parameters.get('minimizeStops'):
                clustering = 'clustering=drivingDistance:500'

            waypoints = '&'.join(
                f'destination{index + 1}={requests.utils.quote(f"{point['designation']};{point['latitude']},{point['longitude']}")}'
                for index, point in enumerate(self.points)
            )
            departure_time = self.get_formatted_date()
            api_url = (
                f"https://wps.hereapi.com/v8/findsequence2?start={self.start_position['latitude']},{self.start_position['longitude']}"
                f"&{waypoints}&improveFor={improve_for}&mode={mode}&departure={departure_time}"
                f"{'&' + clustering if clustering else ''}&apikey={self.here_api_key}"
            )

            response = requests.get(api_url)
            response.raise_for_status()  
            response_data = response.json()

            optimized_waypoints = response_data['results'][0]['waypoints']
            optimized_points = [
                {**point, 'order': index + 1}
                for index, wp in enumerate(optimized_waypoints[1:])
                for point in self.points if point['designation'] == wp['id']
            ]

            distance = int(response_data['results'][0]['distance'])
            duration = int(response_data['results'][0]['time'])

            result = {
                'uuid': self.uuid,
                'distance': distance / 1000,  
                'duration': duration / 60,   
                'startPosition': self.start_position,
                'parameters': self.parameters,
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


class MapURLGenerator:
    def __init__(self, request_data):
        self.uuid = request_data.get('uuid')
        self.start_position = request_data.get('startPosition')
        self.points = request_data.get('points', [])

    def generate(self):
        if not self.uuid or not self.start_position or not self.points or not isinstance(self.points, list) or len(self.points) == 0:
            return jsonify({'error': 'Invalid input format'}), 400

        ordered_points = sorted(self.points, key=lambda p: p.get('order', 0))

        origin = f"{self.start_position['latitude']}_{self.start_position['longitude']}"
        waypoints = ''.join([f"~pos.{p['latitude']}_{p['longitude']}" for p in ordered_points[:-1]])
        destination = f"~pos.{ordered_points[-1]['latitude']}_{ordered_points[-1]['longitude']}"

        map_url = f"https://www.bing.com/maps?rtp=pos.{origin}{waypoints}{destination}"

        return jsonify({'mapUrl': map_url})
