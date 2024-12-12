from app import db
from sqlalchemy.dialects.postgresql import UUID
from app.database import db

class Proyek(db.Model):
    __tablename__ = 'proyek'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    nama_proyek = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.String(255), nullable=True)
    jumlah_kriteria = db.Column(db.Integer, nullable=True)
    jumlah_responden = db.Column(db.Integer, nullable=True)
    periode_mulai = db.Column(db.Date, nullable=True)
    periode_selesai = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.Date)

    def __repr__(self):
        return f'<Proyek {self.nama_proyek}>'
