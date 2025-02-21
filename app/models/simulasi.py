import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import TIMESTAMP, func
from app.database import db
import uuid

class TaskSimulasi(db.Model):
    __tablename__ = 'task_simulasi'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    nama_task = db.Column(db.String(255), nullable=False)
    nama_metode = db.Column(db.String(255), nullable=False)
    id_proyek = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    tgl_simulasi = db.Column(db.TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self):
            return {
                "id": str(self.id),
                "nama_task": self.nama_task,
                "nama_metode": self.nama_metode,
                "id_proyek": str(self.id_proyek),
                "tgl_simulasi": self.tgl_simulasi.isoformat() if self.tgl_simulasi else None,
            }

class HasilSimulasi(db.Model):
    __tablename__ = 'hasil_simulasi'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    id_task = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    id_kriteria = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    bobot = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
