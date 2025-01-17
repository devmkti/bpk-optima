import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.database import db
import uuid
from sqlalchemy import PrimaryKeyConstraint


class DetailPartisipasi1(db.Model):
    __tablename__ = 'detail_partisipasi1'
   # id = db.Column(db.Integer, primary_key=True)

    nip = db.Column(db.String(50), nullable=False)
    id_proyek = db.Column(db.String(50), nullable=False)
    best_to_others = db.Column(db.String(50), nullable=False)  # ID kriteria dari dropdown Best to Others
    others_to_worst = db.Column(db.String(50), nullable=False)  # ID kriteria dari dropdown Others to Worst
    
    # Menentukan gabungan primary key
    __table_args__ = (
        PrimaryKeyConstraint('nip', 'id_proyek'),
    )

class DetailPartisipasi2(db.Model):
    __tablename__ = 'detail_partisipasi2'
    id = db.Column(db.String, primary_key=True)
    # id_proyek = db.Column(UUID(as_uuid=True), db.ForeignKey('proyek.id'), nullable=False)
    
    nip = db.Column(db.String(50), primary_key=True, nullable=False)
    id_kriteria = db.Column(UUID(as_uuid=True), db.ForeignKey('kriteria.id'), primary_key=True, nullable=False)
    opsi = db.Column(db.String(10), nullable=False)  # BO atau WO
    skor = db.Column(db.Integer, nullable=False)     # Nilai dari input kriteria

    kriteria = db.relationship('Kriteria', backref=db.backref('partisipasi', lazy=True))

    def __init__(self, nip, id_kriteria, opsi, skor):
        self.nip = nip
        self.id_kriteria = id_kriteria
        self.opsi = opsi
        self.skor = skor


class Pegawai(db.Model):
    __tablename__ = 'pegawai'
    #id = db.Column(db.String, primary_key=True)
    nip = db.Column(db.String, primary_key=True)
    nama = db.Column(db.String)
    email = db.Column(db.String)
    administrator = db.Column(db.String)



# #-------------------------------------------------------------------------------------------------------------------
# class Partisipasi1(db.Model):
#     __tablename__ = 'detail_partisipasi1'
    
#     nip = db.Column(db.String(50), nullable=False)
#     id_proyek = db.Column(db.String(50), nullable=False)
#     best_to_others = db.Column(db.String(50), nullable=False)  # ID kriteria dari dropdown Best to Others
#     others_to_worst = db.Column(db.String(50), nullable=False)  # ID kriteria dari dropdown Others to Worst
    
#     # Menentukan gabungan primary key
#     __table_args__ = (
#         PrimaryKeyConstraint('nip', 'id_proyek'),
#     )

# class Partisipasi(db.Model):
#     __tablename__ = 'detail_partisipasi2'
    
#     nip = db.Column(db.String(50), primary_key=True, nullable=False)
#     id_kriteria = db.Column(UUID(as_uuid=True), db.ForeignKey('kriteria.id'), primary_key=True, nullable=False)
#     opsi = db.Column(db.String(10), nullable=False)  # BO atau WO
#     skor = db.Column(db.Integer, nullable=False)     # Nilai dari input kriteria

#     kriteria = db.relationship('Kriteria', backref=db.backref('partisipasi', lazy=True))

#     def __init__(self, nip, id_kriteria, opsi, skor):
#         self.nip = nip
#         self.id_kriteria = id_kriteria
#         self.opsi = opsi
#         self.skor = skor
# #-------------------------------------------------------------------------------------------------------------------