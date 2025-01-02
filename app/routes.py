from datetime import datetime
import uuid
from flask import Blueprint, render_template, request, jsonify
from app.controllers.proyek_controller import *
from app.models.proyek import Proyek
from app.models.kriteria import Kriteria
from app.models.partisipate import DetailPartisipasi1, DetailPartisipasi2, Pegawai
from app.database import db

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased

import pandas as pd
import numpy as np
from pulp import LpProblem, LpVariable, LpMinimize, LpMaximize, lpSum, PULP_CBC_CMD, LpStatus
import logging

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

# Route untuk melihat view proyek
@main_bp.route('/proyek/<uuid:id>/view', methods=['GET'])
def view_proyek(id):
    proyek = Proyek.query.get_or_404(id)
    kriterias = db.session.query(Proyek.id, Kriteria.nama_kriteria).join(Kriteria, Proyek.id == Kriteria.id_proyek, isouter=True).where(Proyek.id == id).all()
    temp = []
    for k in kriterias:
      temp.append(k[1])

    return render_template('view_proyek.html', proyek=proyek, kriterias=temp)


# Route untuk melihat view proyek OWNER
@main_bp.route('/proyek/<uuid:id>/view_po', methods=['GET'])
def view_po(id):
    proyek = Proyek.query.get_or_404(id)
      
    # Subquery AA
    subquery_aa = db.session.query(
        Proyek.nama_proyek.label('nama_proyek'),
        Kriteria.nama_kriteria.label('nama_kriteria'),
        Proyek.id.label('proyek_id'),
        Kriteria.id.label('kriteria_id')
    ).join(Kriteria, Proyek.id == Kriteria.id_proyek).filter(Proyek.id == id).subquery()

    # Subquery BB
    subquery_bb = db.session.query(
    #results = db.session.query(
        DetailPartisipasi1.nip.label('nip'),
        subquery_aa.c.nama_kriteria.label('nama_kriteria'),
        #DetailPartisipasi1.best_to_others.label('bo'),
        #DetailPartisipasi1.others_to_worst.label('ow'),
        subquery_aa.c.proyek_id.label('proyek_id'),
        subquery_aa.c.kriteria_id.label('kriteria_id')
    ).join(subquery_aa, subquery_aa.c.proyek_id == DetailPartisipasi1.id_proyek
    #).filter(
    #    DetailPartisipasi1.nip == nip_filter
    ).subquery()

    # # Final Query
    results = db.session.query(
        subquery_bb.c.nip.label('nip'),
        subquery_bb.c.proyek_id,
        Pegawai.nama.label('nama_pegawai')  # Menampilkan nama pegawai
        #subquery_bb.c.nama_kriteria,
        # subquery_bb.c.best_to_others,
        # subquery_bb.c.others_to_worst,
        # DetailPartisipasi2.opsi,
        # DetailPartisipasi2.skor,
        #DetailPartisipasi2.id_proyek
        # DetailPartisipasi2.id_kriteria
    ).join(
        DetailPartisipasi2,
        (subquery_bb.c.nip == DetailPartisipasi2.nip) &
        # (subquery_bb.c.proyek_id == DetailPartisipasi2.id_proyek) &
        (subquery_bb.c.kriteria_id == DetailPartisipasi2.id_kriteria)
    ).join(
        Pegawai, subquery_bb.c.nip == Pegawai.nip  # Join tabel Pegawai
    ).distinct().all()
    
    return render_template('view_proyek-owner.html', proyek=proyek, view_po=results)

@main_bp.route('/api/proyek/<uuid:project_id>', methods=['GET'])
def api_get_project_details(project_id):
    transaksi_terkait = DetailPartisipasi1.query.filter_by(id_proyek=project_id).first()
    if transaksi_terkait:
        return {"fail": "Proyek tidak dapat diedit karena sudah ada transaksi terkait"}, 400
    return jsonify(get_project_details(project_id))

# Route untuk melihat detail proyek
@main_bp.route('/proyek/<uuid:id>/participate', methods=['GET'])
def participate_proyek(id):
    proyek = Proyek.query.get_or_404(id)
    kriterias = db.session.query(Proyek.id, Kriteria.nama_kriteria, Kriteria.id).join(Kriteria, Proyek.id == Kriteria.id_proyek, isouter=True).where(Proyek.id == id).all()
   
    temp = []
    for k in kriterias:
       temp.append({"nama_kriteria": k[1], "id_kriteria": k[2]})
    # return temp
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
    
@main_bp.route('/api/proyek_delete/<uuid:id>', methods=['DELETE'])
def delete_proyek(id):
    try:
        # logging.info(f"UUID diterima: {id}")
        proyek = Proyek.query.get(id)
       
        if not proyek:
            return {"error": "Proyek not found"}, 404
        
        transaksi_terkait = DetailPartisipasi1.query.filter_by(id_proyek=id).first()
        if transaksi_terkait:
            return {"error": "Proyek tidak dapat dihapus karena sudah ada transaksi terkait"}, 400

        Kriteria.query.filter_by(id_proyek=id).delete()
        # Hapus data dari database
        db.session.delete(proyek)
        db.session.commit()
        
        return {"message": "Kriteria berhasil dihapus"}, 200
    except Exception as e:
        db.session.rollback()  # Rollback jika terjadi error
        return {"error": f"Terjadi kesalahan: {str(e)}"}, 500

@main_bp.route('/api/proyek_partisipasi', methods=['POST'])
def add_partisipasi():
    try:
        data = request.get_json()
        nip = data.get('nip')
        id_proyek = data.get('idProyek')
        best_to_others = data.get('best_to_others')
        others_to_worst = data.get('others_to_worst')
        
        if not data:
            return jsonify({"message": "Tidak ada data yang dikirim."}), 400

        # print("Data diterima:", data)  # Debugging log

        if not data.get('nip'):
            return jsonify({"message": "NIP tidak ditemukan!"}), 400

        bo_data = data.get('bo', [])
        wo_data = data.get('wo', [])

        if not bo_data or not wo_data:
            return jsonify({"message": "Data BO atau WO tidak lengkap!"}), 400

        nip = data['nip']
        # print("NIP:", nip)  # Debugging log

        # Insert data untuk BO
        for bo in bo_data:
            # print("Proses BO:", bo)  # Debugging log
            id_kriteria = uuid.UUID(bo['id_kriteria'])
            skor = bo['skor']
            new_partisipasi = DetailPartisipasi2(nip=nip, id_kriteria=id_kriteria, opsi='bo', skor=skor)
            db.session.add(new_partisipasi)

        # Insert data untuk WO
        for wo in wo_data:
            # print("Proses WO:", wo)  # Debugging log
            id_kriteria = uuid.UUID(wo['id_kriteria'])
            skor = wo['skor']
            new_partisipasi = DetailPartisipasi2(nip=nip, id_kriteria=id_kriteria, opsi='ow', skor=skor)
            db.session.add(new_partisipasi)

        # Commit perubahan ke database
        new_proyek_dropdown = DetailPartisipasi1(
            nip=nip,
            id_proyek=id_proyek,
            best_to_others=best_to_others,
            others_to_worst=others_to_worst,
        )
        db.session.add(new_proyek_dropdown)
        db.session.commit()
        print("Data berhasil disimpan!")  # Debugging log
        return jsonify({"message": "Data berhasil disimpan!"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")  # Debugging log
        return jsonify({"message": f"Error: {str(e)}"}), 500

@main_bp.route('/proyek/<uuid:id>/view_pod/<nip>', methods=['GET'])
def calculate(id,nip):
    #data = request.json

    proyek = Proyek.query.get_or_404(id)
    nama_pegawai=get_namapegawai(nip)
    # Alias tabel untuk subquery
    proyek_alias = aliased(Proyek)
    kriteria_alias = aliased(Kriteria)

    # Subquery: bagian "AA" dalam SQL
    subquery = (
        db.session.query(
            proyek_alias.nama_proyek.label("nama_proyek"),
            kriteria_alias.nama_kriteria.label("nama_kriteria"),
            proyek_alias.id.label("proyek_id"),
            kriteria_alias.id.label("kriteria_id")
        )
        .join(kriteria_alias, proyek_alias.id == kriteria_alias.id_proyek)
        .filter(proyek_alias.id == id )
        .subquery()  # Membuat subquery
    )

    # Query utama
    kriterias = (
        db.session.query(
            DetailPartisipasi2.nip,
            subquery.c.nama_kriteria,
            DetailPartisipasi2.opsi,
            DetailPartisipasi2.skor,
            subquery.c.kriteria_id,
            DetailPartisipasi1.best_to_others,
            DetailPartisipasi1.others_to_worst,
            DetailPartisipasi2.opsi
                
        )
        .join(subquery, subquery.c.kriteria_id == DetailPartisipasi2.id_kriteria)
        .join(DetailPartisipasi1, DetailPartisipasi2.nip == DetailPartisipasi1.nip)
        .filter(DetailPartisipasi2.nip == nip)
        .all()
    )

    # Array untuk data kriteria
    kriter = []
    nm_kriter = []
    n_BO = []
    n_OW = []
    for field in kriterias:
        if field[7] == 'bo':
            kriter.append(str(field[4]))
            nm_kriter.append(str(field[1]))
            best_criterion = str(field[5])
            worst_criterion = str(field[6])
            n_BO.append(str(field[3]))
        if field[7] == 'ow':
            n_OW.append(str(field[3]))

    #return worst_criterion
    criteria = kriter
    lcriteria = nm_kriter
    goal = 'minimize'  # Default to 'minimize'
    best_to_others = np.array(n_BO, dtype=float)
    others_to_worst = np.array(n_OW, dtype=float)
    
    n = len(criteria)
    best_index = criteria.index(best_criterion)
    worst_index = criteria.index(worst_criterion)
    
    # Solve using descriptive statistics (direct BO/OW)
    weights_descriptive, consistency_descriptive = solve_bwm(best_to_others, others_to_worst, criteria, best_index, worst_index, goal)

    # Solve using Bayesian approach (adjust prior BO/OW with weights)
    priors = [1 / n] * n
    bayesian_bo = [bo * prior for bo, prior in zip(best_to_others, priors)]
    bayesian_ow = [ow * prior for ow, prior in zip(others_to_worst, priors)]
    weights_bayesian, consistency_bayesian = solve_bwm(bayesian_bo, bayesian_ow, criteria, best_index, worst_index, goal)

    # Create DataFrame for visualization
    df_results = pd.DataFrame({
        "Criteria": lcriteria,
        "Weights_Descriptive": weights_descriptive,
        "Weights_Bayesian": weights_bayesian
    }).set_index("Criteria")

    # Gabungkan kedua list menjadi pasangan
    paired_data = list(zip(lcriteria, weights_descriptive))
    paired_databayes = list(zip(lcriteria, weights_bayesian))
    #print(paired_data)

    # Add consistency columns to the DataFrame
    df_results["Consistency_Descriptive"] = consistency_descriptive
    df_results["Consistency_Bayesian"] = consistency_bayesian

    # Convert data to JSON for Chart.js
    weights_descriptive_json = json.dumps(weights_descriptive)
    weights_bayesian_json = json.dumps(weights_bayesian)
    criteria_json = json.dumps(lcriteria)

    #print ("Weights Descriptive:", weights_descriptive)
    #return weights_descriptive_json
    # weights_descriptive_json = weights_descriptive
    # weights_bayesian_json = weights_bayesian
    # criteria_json = criteria

    # Pass data to the template
    return render_template('view_proyek-owner-detil2.html',
                           proyek=proyek, kriterias=kriterias, nip=nip, nama=nama_pegawai,paired_data=paired_data,paired_databayes=paired_databayes,
                           df_results=df_results.to_html(classes="table table-striped", index=True),
                           weights_descriptive_json=weights_descriptive_json,
                           weights_bayesian_json=weights_bayesian_json,
                           criteria_json=criteria_json)
#     return render_template('view_proyek-owner-detil2.html', proyek=proyek, kriterias=kriterias, nip=nip, nama=nama_pegawai,paired_data=paired_data)

# Function to solve Best Worst Method
def solve_bwm(best_to_others, others_to_worst, criteria, best_index, worst_index, goal):
    # Define the problem
    # Define problem
    if goal == 'minimize':
        prob = LpProblem("Best_Worst_Method", LpMinimize)
    elif goal == 'maximize':
        prob = LpProblem("Best_Worst_Method", LpMaximize)
    else:
        return jsonify({'error': 'Invalid goal. Use "minimize" or "maximize".'}), 400
    

    n = len(criteria)
    # prob = LpProblem("Best_Worst_Method", LpMinimize)
    weights = [LpVariable(f'w{i}', lowBound=0) for i in range(n)]
    xi = LpVariable('xi', lowBound=0)
    prob += xi, "Objective_Xi"
    
    # Constraints for Best-to-Others
    for i in range(n):
        if i != best_index:
            prob += weights[best_index] - best_to_others[i] * weights[i] <= xi
            prob += weights[best_index] - best_to_others[i] * weights[i] >= -xi

    # Constraints for Others-to-Worst
    for i in range(n):
        if i != worst_index:
            prob += weights[i] - others_to_worst[i] * weights[worst_index] <= xi
            prob += weights[i] - others_to_worst[i] * weights[worst_index] >= -xi

    # Sum of weights = 1
    prob += lpSum(weights) == 1
    
    # Solve
    solver = PULP_CBC_CMD(msg=False)
    prob.solve(solver)
    
    # Results
    if prob.status == 1:
        weights_values = [w.varValue for w in weights]
        consistency_ratio = xi.varValue
        return weights_values, consistency_ratio
    else:
        return None, None
