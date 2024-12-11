from app.models.model import Proyek, Kriteria
from app.database import db
from sqlalchemy.dialects.postgresql import UUID

def create_project(data):
    try:
        # Add project to the database
        proyek = Proyek(id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, server_default=db.text("uuid_generate_v4()")), description=data.get('description', ''), nama_proyek=data.get('nama_proyek',''), deskripsi=data.get('deskripsi',''), jumlah_kriteria=data.get('jumlah_kriteria',0), jumlah_responden=data.get('jumlah_responden',0), periode_mulai=data.get('periode_mulai'), periode_selesai=data.get('periode_selesai'), status=data.get('status',''), created_by=data.get('created_by',''), created_at=data.get('created_at',''))
        db.session.add(proyek)
        db.session.flush()  # Get the project ID before committing

        # Add proyek detail (kriteria) to the database
        for kriteria_ in data.get('kriteria', []):
            kriteria = Kriteria(
                id= db.Column(UUID(as_uuid=True), unique=True, nullable=False, server_default=db.text("uuid_generate_v4()")),
                id_proyek=proyek.id,
                nama_kriteria=kriteria_,
                deskripsi=kriteria_.deskripsi
            )
            db.session.add(kriteria)

        db.session.commit()
        return {"message": "Berhasil menyimpan data proyek!", "id_proyek": project.id}
    except Exception as e:
        db.session.rollback()
        return {"error": str(e)}
