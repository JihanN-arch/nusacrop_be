from .dummy_model import dummy_predict
# p
from ml_lib import NusaCropModel
_model = NusaCropModel()

def predict(kondisi_lahan):
    try:
        hasil = _model.recommend(
            ph=kondisi_lahan["ph_tanah"],
            temp_c=kondisi_lahan["suhu"],
            elevation_m=kondisi_lahan["elevasi"],
            soil_texture=kondisi_lahan["tekstur_kelas"],
            monthly_rain=kondisi_lahan["curah_hujan_bulanan"],
            top_k=5,
        )
    except ValueError as e:
        return {"status": "error", "message": f"Model gagal memproses data: {str(e)}"}
    
    rekomendasi = [
        {"crop": item["crop_code"], "score": round(item["skor_aturan"] / 100, 2)}
        for item in hasil
    ]
    return {"status": "success", "data": rekomendasi}
    
    # kalo dummy
    # return dummy_predict(features)
    