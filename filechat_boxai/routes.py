from flask import Blueprint, render_template, request, jsonify
from app.controllers.proyek_controller import create_project
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

@main_bp.route('/store_project', methods=['POST'])
def store_project():
    data = request.json
    result = create_project(data)
    return jsonify(result)

@main_bp.route('/proyek', methods=['POST'])
def tambah_proyek():
    try:
        nama_proyek = request.form['nama_proyek']
        deskripsi_proyek = request.form['deskripsi_proyek']
        periode_mulai = request.form['periode_mulai']
        jumlah_responden = request.form['jumlah_responden']
        jumlah_kriteria = request.form['jumlah_kriteria']
        kriteria = request.form.getlist('kriteria[]')

        # Proses data yang dikirimkan
        proyek = Proyek(
            nama_proyek=nama_proyek,
            deskripsi_proyek=deskripsi_proyek,
            periode_mulai=periode_mulai,
            jumlah_responden=jumlah_responden,
            jumlah_kriteria=jumlah_kriteria
        )
        db.session.add(proyek)
        db.session.flush()

        # Tambahkan kriteria ke dalam database
        for kriteria_ in kriteria:
            kriteria_db = Kriteria(
                id_proyek=proyek.id,
                nama_kriteria=kriteria_
            )
            db.session.add(kriteria_db)

        db.session.commit()
        return jsonify({"message": "Proyek berhasil ditambahkan", "id_proyek": proyek.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)})
