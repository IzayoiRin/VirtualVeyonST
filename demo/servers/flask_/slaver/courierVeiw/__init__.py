from flask import Blueprint

bp = Blueprint("StCourierServer", __name__, url_prefix="/slaver")

from . import view
