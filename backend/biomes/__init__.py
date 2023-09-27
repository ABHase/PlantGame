from flask import Blueprint

biomes = Blueprint('biomes', __name__)

from . import routes
