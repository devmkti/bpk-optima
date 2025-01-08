import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
from app.database import db
from app.models.partisipate import Pegawai


# Daftar nama bulan dalam bahasa Indonesia
def list_bulan():
    return {
        1: "Januari",
        2: "Februari",
        3: "Maret",
        4: "April",
        5: "Mei",
        6: "Juni",
        7: "Juli",
        8: "Agustus",
        9: "September",
        10: "Oktober",
        11: "November",
        12: "Desember"
    }

def get_full_date(time=""):
    if time == "":
        return time

    if time and time != "0000-00-00":
        try:
            # Konversi string ke objek datetime
            time_obj = datetime.datetime.strptime(time, "%Y-%m-%d")
        except ValueError:
            return "-"
    else:
        return "-"

    # Format tanggal menjadi "j Nama_Bulan Y"
    day = time_obj.day
    month = list_bulan().get(time_obj.month, "")
    year = time_obj.year

    return f"{day} {month} {year}"

def get_namapegawai(nip):   
    nmpeg = db.session.query(Pegawai.nama).filter_by(nip = nip).all()
    return f"{nmpeg[0][0]}"

def get_namakriteria(id):   
    nmkrit = db.session.query(Kriteria.nama_kriteria).filter_by(id = id).all()
    return f"{nmkrit[0][0]}"

# def generate_random_string(*, nchars = 7, min_nupper = 3, ndigits = 3, nspecial = 3, special=string.punctuation):
#     letters = random.choices(string.ascii_lowercase, k=nchars)
#     letters_upper = random.choices(string.ascii_uppercase, k=min_nupper)
#     digits = random.choices(string.digits, k=ndigits)
#     specials = random.choices(special, k=nspecial)

#     random_string = letters + letters_upper + digits + specials
#     random.shuffle(random_string)

#     return ''.join(random_string)