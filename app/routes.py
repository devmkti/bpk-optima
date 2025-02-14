from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session
from app.controllers.proyek_controller import *
from app.models.proyek import Proyek
from app.models.kriteria import Kriteria
from app.models.partisipate import DetailPartisipasi1, DetailPartisipasi2, Pegawai
from app.database import db
from app.models.kriteria_skor import KriteriaSkor
# from app.global_functions import *

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
# from src.helpers.utils import generate_random_string
from pulp import LpProblem, LpVariable, LpMinimize, LpMaximize, lpSum, PULP_CBC_CMD, LpStatus
from urllib.parse import urlencode

import uuid
import pandas as pd
import numpy as np
import logging
import os
import urllib.parse
import urllib.request
from functools import wraps
from flask import session, redirect, url_for
main_bp = Blueprint('main', __name__, template_folder='views/templates')

# Konfigurasi
client_id = os.environ.get('IDPRO_CLIENT_ID')
client_secret = os.environ.get('IDPRO_CLIENT_SECRET')
base_url = os.environ.get('IDPRO_BASE_URL')
redirect_uri = os.environ.get('IDPRO_REDIRECT_URL')
scope = os.environ.get('IDPRO_SCOPE')
# state = generate_random_string(length=10, use_digits=True, use_uppercase=True, use_lowercase=True, use_special=False)
state = 'string_generate_random_string'
base_url_login = os.environ.get('BASE_URL')

@main_bp.before_request
def login_required():
    allowed_routes = ['main.login', 'main.callback'] 
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('main.login')) 


# URL untuk authorization
@main_bp.route('/login')
def login():
    # return 'tes'
    auth_url = f"{base_url}/authorize"
    query_params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state,
        'response_type': 'code',
    }
    auth_url_with_params = f"{auth_url}?{urllib.parse.urlencode(query_params)}"
    return redirect(auth_url_with_params)

@main_bp.route('/callback')
def callback():
    # return 'callback'
    code = request.args.get('code')
    # return code
    print('code: ', code)
    
    if not code:
        return "Authorization code not found", 400
        
    token_url = f"{base_url}/token"
    try:
        data = urllib.parse.urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'code': code,
            'grant_type': 'authorization_code'
        }).encode()

        req = urllib.request.Request(token_url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        req.add_header('Accept-Language', 'en-US,en;q=0.5')

        with urllib.request.urlopen(req) as response:
            token_json = json.loads(response.read())
        
        access_token_sso = token_json.get('access_token')
       # print('access_token: ', access_token_sso)
        if not access_token_sso:
            return "Access token not found in the response", 500
        
        userinfo_url = f"{base_url}/userinfo"
        userinfo_req = urllib.request.Request(userinfo_url)
        userinfo_req.add_header('Authorization', f'Bearer {access_token_sso}')
        userinfo_req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        userinfo_req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        userinfo_req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8')
        userinfo_req.add_header('Accept-Language', 'en-US,en;q=0.5')
        
        with urllib.request.urlopen(userinfo_req) as response:
            user_info = json.loads(response.read())

        session['user_id'] = user_info.get("employee_id")
        session['nama_pegawai']=user_info.get("display_name")
        session['logged_in'] = True
        
        # print('session user id: ', session.get('user_id'))
        # print('session logged id: ', session.get('logged_in'))

        return redirect(url_for('main.home'))  # Gunakan nama blueprint di endpoint
    #     return jsonify({
    #     "message": "Login successful",
    #     "id_token": user_info,
    # })

    except urllib.error.HTTPError as e:
        # return f"Error during token request: {str(e)}", 500
        print("yyyyy")
    except ValueError:
        print("=============================")
        # return "Failed to parse token response", 500

@main_bp.route('/logout')
def logout():    
    session.clear()
    #return login()

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

@main_bp.route("/role")
def role():
  return render_template("role.html")

@main_bp.route("/listProjectOwner")
def listProjectOwner():
  return render_template("list-project-owner.html")

@main_bp.route('/proyek', methods=['POST'])
def tambah_proyek():
    result = simpan_proyek(request)
    return jsonify(result)

@main_bp.route('/api/proyek', methods=['GET'])
def get_project():
    result = get_proyek()
    return jsonify(result)

@main_bp.route('/api/role', methods=['GET'])
def get_role():
    result = get_role_user()
    #print(result)
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

@main_bp.route("/api/role/<string:nip>", methods=["PUT"])
def update_role(nip):
    data = request.get_json()
    
    # Cari pegawai berdasarkan NIP
    pegawai = Pegawai.query.filter_by(nip=nip).first()
    if not pegawai:
        return jsonify({"message": "Data tidak ditemukan"}), 404
    
    # Perbarui data pegawai
    
    pegawai.administrator = data.get("administrator", pegawai.administrator)
    
    # Simpan perubahan
    try:
        db.session.commit()  # Menyimpan perubahan ke database
        return jsonify({"message": "Data berhasil diperbarui!"})
    except Exception as e:
        db.session.rollback()  # Jika ada kesalahan, rollback transaksi
        return jsonify({"message": "Terjadi kesalahan", "error": str(e)}), 500
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
    try:
        # Cek apakah ada transaksi terkait
        transaksi_terkait = DetailPartisipasi1.query.filter_by(id_proyek=project_id).first()
        if transaksi_terkait:
            return {"fail": "maaf tidak dapat dilihat/diedit karena sudah ada transaksi terkait!"}, 400

        # Jika tidak ada transaksi terkait, kembalikan detail proyek
        return jsonify(get_project_details(project_id))
    except Exception as e:
        return {"fail": f"Terjadi kesalahan: {str(e)}"}, 500

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

@main_bp.route('/api/kriteria_delete/<uuid:id>', methods=['DELETE'])
def delete_kriteria(id):
    try:
        kriteria = Kriteria.query.filter_by(id=id).first()
        if kriteria:
            # Hapus data dari database
            Kriteria.query.filter_by(id=id).delete()
            db.session.commit()
            return {"message": "Kriteria berhasil dihapus"}, 200
        else:
            db.session.rollback()
            return {"error": "Kriteria tidak ditemukan"}, 404
    except Exception as e:
        db.session.rollback()
        db.session.remove()
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
        db.session.remove()
        return {"error": f"Terjadi kesalahan: {str(e)}"}, 500
    
@main_bp.route('/api/validasi_partisipate/<uuid:id>',)
def validasiPartisipate(id):
    try:
        # logging.info(f"UUID diterima: {id}")
        proyek = Proyek.query.get(id)
       
        if not proyek:
            return {"error": "Proyek not found"}, 404
        
        validasi = DetailPartisipasi1.query.filter_by(id_proyek=id,nip=session['user_id']).first()
        if validasi:
            return {"error": "Proyek ini sudah pernah anda melakukan partisipate sebelum nya"}, 400
        return {"message": "Proyek dapat diikuti."}, 200
    except Exception as e:
        db.session.rollback()  # Rollback jika terjadi error
        db.session.remove()
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
        return jsonify({"message": "Data berhasil disimpan!","success":True}), 200
    except Exception as e:
        db.session.rollback()
        db.session.remove()
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
            DetailPartisipasi2.opsi,
            subquery.c.proyek_id,   
                
        )
        .join(subquery, subquery.c.kriteria_id == DetailPartisipasi2.id_kriteria)
        .join(DetailPartisipasi1, DetailPartisipasi2.nip == DetailPartisipasi1.nip)
        #.filter(DetailPartisipasi2.nip == nip )
        .filter(DetailPartisipasi2.nip == nip, subquery.c.proyek_id==DetailPartisipasi1.id_proyek)
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
                           id=id, proyek=proyek, kriterias=kriterias, nip=nip, nama=nama_pegawai,paired_data=paired_data,paired_databayes=paired_databayes,
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

@main_bp.route('/api/proyek_partisipasi_bobot', methods=['POST'])
def store_weight_participate():
    try:
        data = request.get_json()
        id = data.get('id_proyek')
        
        if not data:
            return jsonify({"message": "Tidak ada data yang dikirim."}), 400

        # Pengecekan data bobot setiap partisipan apakah sudah ada di tabel kriteria_skor atau belum
        kriteria_skor = KriteriaSkor.query.filter_by(id_proyek=id).first()
        if not kriteria_skor:
            participates = DetailPartisipasi1.query.filter_by(id_proyek=id).all()
            proyek = Proyek.query.get_or_404(id)

            # Lakukan perulangan dan simpan bobot setiap partisipan
            for p in participates:
                nip = p.nip
                print("participates nip: ", nip)

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
                        DetailPartisipasi2.opsi,
                        subquery.c.proyek_id,   
                            
                    )
                    .join(subquery, subquery.c.kriteria_id == DetailPartisipasi2.id_kriteria)
                    .join(DetailPartisipasi1, DetailPartisipasi2.nip == DetailPartisipasi1.nip)
                    #.filter(DetailPartisipasi2.nip == nip )
                    .filter(DetailPartisipasi2.nip == nip, subquery.c.proyek_id==DetailPartisipasi1.id_proyek)
                    # .filter(subquery.c.proyek_id==DetailPartisipasi1.id_proyek)
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

                # Gabungkan kedua list menjadi pasangan
                paired_data = list(zip(criteria, weights_descriptive))
                # print('Paired data nip ' , nip , ': ', paired_data)

                for pr in paired_data:
                    print('Sub paired data nip ' , nip , ': ', pr[0])
                    # Proses data yang dikirimkan
                    ks = KriteriaSkor(
                        id_proyek=id,
                        nip=nip,
                        id_kriteria=pr[0],
                        bobot=pr[1]
                    )
                    db.session.add(ks)
                db.session.flush()
            db.session.commit()

        return jsonify({"message": "Data berhasil disimpan!","success":True}), 200
    except Exception as e:
        db.session.rollback()
        db.session.remove()
        print(f"Error: {str(e)}")  # Debugging log
        return jsonify({"message": f"Error: {str(e)}"}), 500

@main_bp.route('/api/final_simulate', methods=['POST'])
def final_simulate():
    try:
        data = request.get_json()
        id = data.get('idProyek')
        kriteria_skor = KriteriaSkor.query.filter_by(id_proyek=id).all()

        # Query data nama kriteria
        kriteria = Kriteria.query.all()  # Mengambil semua kriteria
        kriteria_dict = {k.id: k.nama_kriteria for k in kriteria}  # Mapping id ke nama_kriteria

        # Grouping data by 'nip'
        from collections import defaultdict
        grouped_data = defaultdict(lambda: {})

        for skor in kriteria_skor:
            grouped_data[skor.nip][skor.id_kriteria] = skor.bobot

        # Convert grouped data into individual_weights array
        unique_kriteria = sorted({skor.id_kriteria for skor in kriteria_skor})
        individual_weights = []

        for nip, kriteria_bobot in grouped_data.items():
            row = [kriteria_bobot.get(kriteria_id, 0) for kriteria_id in unique_kriteria]
            individual_weights.append(row)

        # Convert to NumPy array
        individual_weights = np.array(individual_weights, dtype=float)
        print("Individual weights:\n", individual_weights)
        
        # Calculate group weights using geometric mean
        group_weights = np.prod(individual_weights, axis=0) ** (1 / len(individual_weights))
        group_weights = group_weights / np.sum(group_weights)  # Normalize
        print("Group weights:\n", group_weights)

        # Zip nama_kriteria dengan group_weights
        kriteria_names = [kriteria_dict[k_id] for k_id in unique_kriteria]  # Ambil nama kriteria sesuai urutan id_kriteria
        zipped_results = list(zip(kriteria_names, group_weights))

        # Prepare group_weights and kriteria_names as JSON
        group_weights_json = [float(weight) for weight in group_weights]
        kriteria_names_json = kriteria_names

        print("Zipped results (nama_kriteria dan group_weights):\n", zipped_results)

        return jsonify({
            "message": "Data simulasi berhasil disimpan!",
            "success":True,
            "data": [{"nama_kriteria": name, "bobot": weight} for name, weight in zipped_results],
            "group_weights_json": group_weights_json,
            "kriteria_names_json": kriteria_names_json
        }), 200
        # store the final results
    except Exception as e:
        db.session.rollback()
        db.session.remove()
        print(f"Error: {str(e)}") #Debugging log
        return jsonify({"message": f"Error: {str(e)}"}), 500
    # end try