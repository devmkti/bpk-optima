import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.database import db

class Proyek(db.Model):
    __tablename__ = 'proyek'
    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    nama_proyek = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.String(255), nullable=True)
    jumlah_kriteria = db.Column(db.Integer, nullable=True)
    jumlah_responden = db.Column(db.Integer, nullable=True)
    periode_mulai = db.Column(db.Date, nullable=True)
    periode_selesai = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.Date, nullable=True)

class Kriteria(db.Model):
    __tablename__ = 'kriteria'
    # id = db.Column(db.Integer, primary_key=True)
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    id_proyek = db.Column(db.Integer, db.ForeignKey('proyek.id'), nullable=False)
    nama_kriteria = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.String(255), nullable=False)

    proyek = db.relationship('Proyek', backref=db.backref('details', lazy=True))
