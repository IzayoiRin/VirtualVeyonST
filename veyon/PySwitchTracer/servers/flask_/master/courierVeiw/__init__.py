from flask import Blueprint

bp = Blueprint("StCourierServer", __name__, url_prefix="/master")

from . import view
