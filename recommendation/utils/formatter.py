# from ..data import TANAMAN_DATA
from ..crop_models import Crop
from .reason import generate_reason
from .confidence import get_confidence


def format_recommendation(prediction, kondisi_lahan):

    crop_ids = [item["crop"] for item in prediction]
    crops = Crop.objects.filter(slug__in=crop_ids)
    crop_map = {crop.slug: crop for crop in crops}

    rekomendasi = []

    for item in prediction:
        tanaman = crop_map.get(item["crop"])
        if tanaman is None:
            continue

        syarat = tanaman.syarat_tumbuh
        
        skor = item["score"]
        reasons = generate_reason(kondisi_lahan, {
            "nama" : tanaman.nama, 
            "syarat_tumbuh" : syarat})

        #! Ini kalo DB
        rekomendasi.append({
            "id": tanaman.slug,
            "nama": tanaman.nama,
            "nama_latin": tanaman.nama_latin,
            "jenis_tanaman": tanaman.jenis_tanaman,
            "kesuburan_ideal": syarat["kesuburan"],
            "ph_ideal": f'{syarat["ph"]["min"]} - {syarat["ph"]["max"]}',
            "elevasi_ideal": f'{syarat["elevasi"]["min"]} - {syarat["elevasi"]["max"]} mdpl',
            "skor_kesesuaian": skor,
            "tingkat_kepercayaan" : get_confidence(skor),
            "alasan_rekomendasi" : reasons,
        })
        
    return {
        "kondisi_lahan" : kondisi_lahan,
        "rekomendasi" : rekomendasi
    }        