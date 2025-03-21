import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.database import db
import uuid

class Kriteria(db.Model):
    __tablename__ = 'kriteria'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    id_proyek = db.Column(UUID(as_uuid=True), db.ForeignKey('proyek.id'), nullable=False)
    nama_kriteria = db.Column(db.String(255), nullable=False)
    deskripsi = db.Column(db.String(255), nullable=False)

    # proyek = db.relationship('Proyek', backref=db.backref('details', lazy=True))

    # def __repr__(self):
    #     # return f'<Proyek {self.nama_kriteria}>'
    #     return f'{self.nama_kriteria}'
    # def toJSON(self):
    #     return {
    #         "id":self.id,
    #         "id_proyek":self.id_proyek,
    #         "nama_kriteria":self.nama_kriteria,
    #         "deskripsi":self.deskripsi
    #     }
