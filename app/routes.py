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
@main_bp.route('/proyek/<uuid:id>/view', methods=['GET'])
# @main_bp.route('/proyek/view', methods=['GET'])
def view_proyek(id):
    proyek = Proyek.query.get_or_404(id)
    return render_template('view_proyek.html', proyek=proyek)

@main_bp.route('/api/proyek/<uuid:project_id>', methods=['GET'])
def api_get_project_details(project_id):
    return jsonify(get_project_details(project_id))

# Route untuk melihat detail proyek
@main_bp.route('/proyek/<uuid:id>/participate', methods=['GET'])
def participate_proyek(id):
    proyek = Proyek.query.get_or_404(id)
    kriterias = db.session.query(Proyek.id, Kriteria.nama_kriteria).join(Kriteria, Proyek.id == Kriteria.id_proyek, isouter=True).where(Proyek.id == id).all()
    temp = []
    for k in kriterias:
      temp.append(k[1])

    return render_template('participate_proyek.html', proyek=proyek, kriterias=temp)


@main_bp.route('/api/edit_proyek/<uuid:id>', methods=['PUT'])
def edit_proyek(id):
    data = request.json  # Ambil data JSON dari request body

    # Validasi data input
    if not data or not data.get('nama_proyek') or not data.get('details'):
        return jsonify({"message": "Data tidak valid!"}), 400

    proyek = Proyek.query.get(id)  # Ambil proyek berdasarkan ID
    if proyek:
        proyek.nama_proyek = data['nama_proyek']
        proyek.deskripsi = data['deskripsi']
        proyek.jumlah_responden = data['jumlah_responden']
        proyek.periode_mulai = data['periode_mulai']
        proyek.periode_selesai = data['periode_selesai']
        
        # Buat set untuk menyimpan ID kriteria yang ada
        existing_kriteria_ids = {kriteria.id for kriteria in proyek.details}

        # Update atau tambahkan kriteria baru
        for detail in data['details']:
            # Cek apakah kriteria sudah ada
            existing_kriteria = next(
                (k for k in proyek.details if k.nama_kriteria == detail['nama_kriteria']), None)
            print("Kriteria yang ada:", existing_kriteria_ids)
            if existing_kriteria:
                # Jika ada, perbarui kriteria tanpa mengubah ID
                existing_kriteria.nama_kriteria = detail['nama_kriteria']
                existing_kriteria_ids.discard(existing_kriteria.id)  # Hapus dari set
                
            else:
                # Jika tidak ada, tambahkan kriteria baru
                new_kriteria = Kriteria(
                    nama_kriteria=detail['nama_kriteria'],
                    proyek=proyek
                )
                db.session.add(new_kriteria)

        # Hapus kriteria yang tidak ada dalam data baru
        for kriteria_id in existing_kriteria_ids:
            kriteria_to_delete = Kriteria.query.get(kriteria_id)
            if kriteria_to_delete:
                db.session.delete(kriteria_to_delete)

        db.session.commit()
        return jsonify({"message": "Proyek berhasil diperbarui."}), 200

    return jsonify({"message": "Proyek tidak ditemukan."}), 404

@main_bp.route('/api/kriteria_edit/<uuid:kriteria_id>', methods=['PUT'])
def update_kriteria(kriteria_id):
    try:
        # Ambil data dari request body
        data = request.get_json()
        nama_kriteria_baru = data.get('nama_kriteria')

        # Validasi data input
        if not nama_kriteria_baru:
            return jsonify({"message": "Nama kriteria tidak boleh kosong"}), 400

        # Cari kriteria berdasarkan ID
        kriteria = Kriteria.query.get(kriteria_id)
        if not kriteria:
            return jsonify({"message": "Kriteria tidak ditemukan"}), 404

        # Update kriteria
        kriteria.nama_kriteria = nama_kriteria_baru
        db.session.commit()

        return jsonify({"message": "Data kriteria berhasil diubah"}), 200
    except Exception as e:
        return jsonify({"message": f"Terjadi kesalahan: {str(e)}"}), 500

@main_bp.route('/api/kriteria_delete/<uuid:kriteria_id>', methods=['DELETE'])
def delete_kriteria(kriteria_id):
    try:
        kriteria = Kriteria.query.get(kriteria_id)
        if not kriteria:
            return {"error": "Kriteria not found"}, 404
        
        # Hapus data dari database
        db.session.delete(kriteria)
        db.session.commit()
        
        return {"message": "Kriteria berhasil dihapus"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
