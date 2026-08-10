# from ..data import TANAMAN_DATA
from ..crop_models import Crop
from ..utils.confidence import get_confidence
from ..utils.reason import generate_reason
from ..riwayat_models import RiwayatRekomendasi

def get_crop_detail(rekomendasi_id):
    try:
        rekomendasi = RiwayatRekomendasi.objects.select_related('crop').get(id=rekomendasi_id)
    except RiwayatRekomendasi.DoesNotExist:
        return None
    
    tanaman = rekomendasi.crop

    # kita ubah object (dari db) ke dict 
    crop_data = {
        "nama": tanaman.nama,
        "nama_latin": tanaman.nama_latin,
        "deskripsi": tanaman.deskripsi,
        "jenis_tanaman": tanaman.jenis_tanaman,
        "umur_panen": tanaman.umur_panen,
        "potensi_hasil": tanaman.potensi_hasil,
        "cara_budidaya": tanaman.cara_budidaya,
        "manfaat": tanaman.manfaat,
        "syarat_tumbuh": tanaman.syarat_tumbuh
    }
    
    
    return {
        **crop_data, 
        
        "ringkasan_rekomendasi": {
            "skor_kesesuaian": rekomendasi.skor_kesesuaian,        
            "tingkat_kepercayaan": rekomendasi.tingkat_kepercayaan,
            "alasan_rekomendasi": rekomendasi.alasan_rekomendasi, 
        }
    }