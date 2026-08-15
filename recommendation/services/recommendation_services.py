from ..ml.ml_model import predict
from ..utils.formatter import format_recommendation
from .environment_service import get_environment
from ..models.riwayat_models import RiwayatPencarian, RiwayatRekomendasi
from ..models.crop_models import Crop

def get_recommendation(data, anonymous_id):

    # ini ntar isinya API cuaca, satelit, dll
    kondisi_lahan = get_environment(
        data["lat"],
        data["lon"]
    )
    if kondisi_lahan["status"] != "success":
        return kondisi_lahan

    # predict hasil ML
    prediction_result = predict(kondisi_lahan)
    if prediction_result["status"] != "success":
        return prediction_result


    prediction = prediction_result["data"]
    formatted = format_recommendation(
        prediction,
        kondisi_lahan
    )
    
    #ini di snapshot untuk riwayat
    riwayat = RiwayatPencarian.objects.create(
        anonymous_id=anonymous_id,
        nama_lokasi = data.get("nama_lokasi"),
        lat=data["lat"],
        lon=data["lon"],
        musim_target=data.get("musim_target"),
        curah_hujan=kondisi_lahan["curah_hujan"],
        ph_tanah=kondisi_lahan["ph_tanah"],
        elevasi=kondisi_lahan["elevasi"],
        ndvi=kondisi_lahan.get("ndvi"),
        suhu=kondisi_lahan["suhu"],
        et0=kondisi_lahan.get("et0"),
        nitrogen=kondisi_lahan.get("nitrogen"),
        organic_carbon=kondisi_lahan.get("organic_carbon"),
        tekstur_tanah=kondisi_lahan.get("tekstur_tanah", {}),
        kesuburan_tanah=kondisi_lahan["kesuburan_tanah"], 
    )
    
    for i, item in enumerate(formatted["rekomendasi"], start=1):
        crop = Crop.objects.get(slug=item["id"])
        rek = RiwayatRekomendasi.objects.create(
            riwayat=riwayat,
            crop=crop,
            skor_kesesuaian=item["skor_kesesuaian"],
            ranking=i,
            tingkat_kepercayaan=item["tingkat_kepercayaan"],
            alasan_rekomendasi=item["alasan_rekomendasi"],
        )
        item["rekomendasi_id"] = rek.id

    return {
        "status": "success",
        "recommendation": formatted
    }