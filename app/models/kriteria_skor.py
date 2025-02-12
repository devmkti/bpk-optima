import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.database import db
import uuid

class KriteriaSkor(db.Model):
    __tablename__ = 'kriteria_skor'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    id_kriteria = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    id_proyek = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    nip = db.Column(db.String(255), nullable=False)
    bobot = db.Column(db.Numeric(precision=10, scale=2), nullable=False)