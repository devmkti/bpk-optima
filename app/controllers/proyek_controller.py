from flask import Blueprint, jsonify
# from app.models.model import Proyeks, Kriteria
from app.database import db
from datetime import datetime
# from app.models.model import Proyek
from app.models.proyek import Proyek
from app.models.kriteria import Kriteria
from sqlalchemy.dialects.postgresql import UUID
from app.global_functions import *


def get_proyek_kriteria():
    proyek_data = db.session.query(Proyek, Kriteria).join(Kriteria, Proyek.id == Kriteria.id_proyek).all()
    # Format hasil
    result = [
        {
            "proyek_id": Proyek.id,
            "nama_proyek": Proyek.nama_proyek,
            "deskripsi": Proyek.deskripsi,
            "kriteria_id": Kriteria.id,
            "nama_kriteria": Kriteria.nama_kriteria
        }
        for kriteria in proyek_data
    ]
    return result

def get_proyek():
    proyek_data = Proyek.query.all()
    result = [
        {
            'id': p.id,
            'nama_proyek': p.nama_proyek,
            'deskripsi': p.deskripsi,
            'jumlah_kriteria': p.jumlah_kriteria,
            'jumlah_responden': p.jumlah_responden,
            'periode_mulai': get_full_date(p.periode_mulai.strftime('%Y-%m-%d')) if p.periode_mulai else "-",
            'periode_selesai': get_full_date(p.periode_selesai.strftime('%Y-%m-%d')) if p.periode_selesai else "-"
        }
        for p in proyek_data
    ]
    # return jsonify(result)
    return result

def simpan_proyek(request):
    try:
        nama_proyek = request.form['nama_proyek']
        deskripsi = request.form['deskripsi']
        periode = request.form['periode_mulai']
        jumlah_responden = request.form['jumlah_responden']
        jumlah_kriteria = request.form['jumlah_kriteria']
        kriteria = request.form.getlist('kriteria[]')

        # Pisahkan tanggal awal dan tanggal akhir
        periode_awal, periode_akhir = periode.split(' to ')

        # Proses data yang dikirimkan
        proyek = Proyek(
            nama_proyek=nama_proyek,
            deskripsi=deskripsi,
            periode_mulai=periode_awal,
            periode_selesai=periode_akhir,
            jumlah_responden=jumlah_responden,
            jumlah_kriteria=jumlah_kriteria,
            created_at=datetime.now()
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
        return {"message": "Proyek berhasil ditambahkan", "id_proyek": proyek.id}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
    
def get_project_details(project_id):
    try:
        proyek = Proyek.query.get(project_id)
        if not proyek:
            return {"error": "Project not found"}, 404
        
        kriteria_list = Kriteria.query.filter_by(id_proyek=proyek.id).all()
        kriteria_data = [{"id": k.id, "nama_kriteria": k.nama_kriteria} for k in kriteria_list]
       
        return {
            "nama_proyek": proyek.nama_proyek,
            "deskripsi": proyek.deskripsi,
            "kriteria": kriteria_data
        }
    except Exception as e:
        return {"error": str(e)}, 500
    
def update_project(id, data):
    proyek = Proyek.query.get(id)
    if proyek:
        proyek.nama_proyek = data['nama_proyek']
        proyek.deskripsi = data['deskripsi']
        proyek.details.clear()  # Bersihkan kriteria yang ada sebelumnya

        for kriteria in data['kriteria']:
            if 'nama_kriteria' in kriteria:  # Validasi input kriteria
                new_kriteria = Kriteria(
                    nama_kriteria=kriteria['nama_kriteria'],
                    proyek=proyek
                )
                db.session.add(new_kriteria)
        db.session.commit()
        return True
    return False
    