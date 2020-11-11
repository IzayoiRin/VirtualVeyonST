from flask import Blueprint

bp = Blueprint("Receptor", __name__, url_prefix="/slaver")

from . import view
