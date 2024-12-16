from app import db
from sqlalchemy.dialects.postgresql import UUID
from app.database import db
import uuid
from sqlalchemy import inspect

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

    # def __repr__(self):
    #     # return f'<Proyek {self.nama_proyek}>'
    #     return f'Proyek {self.nama_proyek}'

    # def toDict(self):
    #     return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }

    # @app.route('/contacts',methods=['GET'])
    # def getContacts():
    #     contacts = Contacts.query.all()
    #     contactsArr = []
    #     for contact in contacts:
    #         contactsArr.append(contact.toDict()) 
    #     return jsonify(contactsArr)

    # def __repr__(self):
    #     # return f'<Proyek {self.nama_proyek}>'
    #     return f'Proyek {self.nama_proyek}'
    # def toJSON(self):
    #     return {
    #         "id":self.id,
    #         "nama_proyek":self.nama_proyek,
    #         "deskripsi":self.deskripsi,
    #         "jumlah_kriteria":self.jumlah_kriteria,
    #         "jumlah_responden":self.jumlah_responden,
    #         "periode_mulai":self.periode_mulai,
    #         "periode_selesai":self.periode_selesai,
    #         "status":self.status,
    #         "created_by":self.created_by,
    #         "created_at":self.created_at
    #     }
