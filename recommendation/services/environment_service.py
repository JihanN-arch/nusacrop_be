from concurrent.futures import ThreadPoolExecutor

from .apis.soilgrids import get_soil_data
from .apis.openmeteo import get_weather_data

from ..utils.fertility import calculate_fertility

def get_environment(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return {
            "status": "error",
            "message": f"Koordinat tidak valid: lat={lat}, lon={lon}"
        }

    with ThreadPoolExecutor(max_workers=2) as executor:
        soil_future = executor.submit(get_soil_data, lat, lon)
        weather_future = executor.submit(get_weather_data, lat, lon)

        tanah = soil_future.result()
        cuaca = weather_future.result()
        
        #! Kalo gagal fetch
        if tanah["status"] != "success":
            return tanah
        
        if cuaca["status"] != "success":
            return cuaca

    # # Validasi data tanah
    # if not tanah or "soil" not in tanah:
    #     error_msg = tanah.get("error", "Data tanah tidak ditemukan") if isinstance(tanah, dict) else "Respon tidak valid"
    #     raise ValueError(f"Gagal mendapatkan data tanah dari SoilGrids: {error_msg}")

    # # Validasi data cuaca
    # if not cuaca or "curah_hujan_tahunan" not in cuaca:
    #     raise ValueError("Gagal mendapatkan data cuaca dari OpenMeteo")

    soil = tanah["soil"]
    
    # cek field wajib dari kedua sumber sebelum lanjut
    required_soil = ["ph", "sand", "silt", "clay"]
    required_cuaca = ["curah_hujan_tahunan", "curah_hujan_bulanan", "suhu_rata_rata", "elevasi"]

    missing = []
    for f in required_soil:
        val = soil.get(f)
        if isinstance(val, dict):
            val = val.get("value")
        if val is None:
            missing.append(f"soil.{f}")

    for f in required_cuaca:
        if cuaca.get(f) is None:
            missing.append(f"cuaca.{f}")

    if missing:
        return {
            "status": "error",
            "message": f"Data lahan tidak lengkap: {', '.join(missing)}"
        }

    return {
        "status": "success",

        "curah_hujan": cuaca["curah_hujan_tahunan"],
        "curah_hujan_bulanan": cuaca["curah_hujan_bulanan"],   # <- ditambahin, wajib buat ml_lib
        "suhu": cuaca["suhu_rata_rata"],
        "et0": cuaca["et0_tahunan"],
        "elevasi": cuaca["elevasi"],

        "ph_tanah": soil["ph"],
        "nitrogen": soil["nitrogen"]["value"],
        "organic_carbon": soil["organic_carbon"]["value"],
        "tekstur_kelas": soil.get("tekstur_kelas"),   # <- ditambahin, wajib buat ml_lib

        "tekstur_tanah": {
            "sand": soil["sand"]["value"],
            "silt": soil["silt"]["value"],
            "clay": soil["clay"]["value"]
        },

        "kesuburan_tanah": calculate_fertility(soil)
    }