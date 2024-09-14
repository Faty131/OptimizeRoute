# routes.py
from flask import Blueprint, request, jsonify
from .utils import RouteOptimizer, MapURLGenerator

main = Blueprint('main', __name__)

@main.route('/generate-map-url', methods=['POST'])
def generate_map_url_route():
    generator = MapURLGenerator(request.json)
    return generator.generate()

@main.route('/optimize-route', methods=['POST'])
def optimize_route_route():
    optimizer = RouteOptimizer(request.json)
    return optimizer.optimize()
