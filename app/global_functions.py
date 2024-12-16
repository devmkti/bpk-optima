import datetime
from sqlalchemy.ext.declarative import DeclarativeMeta
import json

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

def new_alchemy_encoder():
    _visited_objs = []

    class AlchemyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj.__class__, DeclarativeMeta):
                # don't re-visit self
                if obj in _visited_objs:
                    return None
                _visited_objs.append(obj)

                # an SQLAlchemy class
                fields = {}
                for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                    fields[field] = obj.__getattribute__(field)
                # a json-encodable dict
                return fields

            return json.JSONEncoder.default(self, obj)

    return AlchemyEncoder