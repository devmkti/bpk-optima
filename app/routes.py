from flask import Blueprint, render_template, request, jsonify
from controllers.proyek_controller import create_project

main_bp = Blueprint('main', __name__, template_folder='views/templates')

@main_bp.route("/")
def base():
  return render_template("base.html")

@main_bp.route("/home")
def home():
  return render_template("home.html")

@main_bp.route("/addNewProject")
def addNewProject():
  return render_template("add-new-project.html")

@main_bp.route("/listOfProject")
def listOfProject():
  return render_template("list-of-project.html")

@main_bp.route('/store_project', methods=['POST'])
def store_project():
    data = request.json
    result = create_project(data)
    return jsonify(result)
