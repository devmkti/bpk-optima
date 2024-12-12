from app.models.model import Proyek, Kriteria
from app.database import db
from datetime import datetime

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