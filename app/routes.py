from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from app.controllers.proyek_controller import *
from app.models.proyek import Proyek
from app.models.kriteria import Kriteria
from app.database import db

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

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

@main_bp.route("/listProjectOwner")
def listProjectOwner():
  return render_template("list-project-owner.html")

@main_bp.route('/proyek', methods=['POST'])
def tambah_proyek():
    result = simpan_proyek(request)
    return jsonify(result)

@main_bp.route('/api/proyek', methods=['GET'])
def get_project():
    # data = request.json
    # result = get_proyek(data)
    result = get_proyek()
    return jsonify(result)

# Route untuk melihat detail proyek
@main_bp.route('/proyek/<int:id>/view', methods=['POST'])
def view_proyek(id):
    proyek = Proyek.query.get_or_404(id)
    return render_template('view_proyek.html', proyek=proyek)

@main_bp.route('/api/proyek/<uuid:project_id>', methods=['GET'])
def api_get_project_details(project_id):
    return jsonify(get_project_details(project_id))