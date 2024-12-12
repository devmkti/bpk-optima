from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from app.controllers.proyek_controller import *
from app.models.model import Proyek, Kriteria
from app.database import db

main_bp = Blueprint('main', __name__, template_folder='views/templates')

@main_bp.route("/")
def index():
  return render_template("home.html")

@main_bp.route("/home")
def home():
  return render_template("home.html")

@main_bp.route("/addNewProject")
def addNewProject():
  return render_template("add-new-project.html")

@main_bp.route("/listOfProject")
def listOfProject():
  return render_template("list-of-project.html")

@main_bp.route('/proyek', methods=['POST'])
def tambah_proyek():
    result = simpan_proyek(request)
    return jsonify(result)
