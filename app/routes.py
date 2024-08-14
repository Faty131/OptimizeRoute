from flask import Blueprint, request, jsonify
from .utils import generate_map_url, optimize_route

main = Blueprint('main', __name__)

@main.route('/generate-map-url', methods=['POST'])
def generate_map_url_route():
    return generate_map_url(request)

@main.route('/optimize-route', methods=['POST'])
def optimize_route_route():
    return optimize_route(request)
