from flask import Blueprint

bp = Blueprint("SenderCenter", __name__, url_prefix="/master")

from . import view
