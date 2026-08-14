from concurrent.futures import ThreadPoolExecutor

from .apis.soilgrids import get_soil_data
from .apis.openmeteo import get_weather_data
from .apis.gee import get_satellite_data

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

    with ThreadPoolExecutor(max_workers=3) as executor:
        soil_future = executor.submit(get_soil_data, lat, lon)
        weather_future = executor.submit(get_weather_data, lat, lon)
        satelit_future = executor.submit(get_satellite_data, lat, lon)

        tanah = soil_future.result()
        cuaca = weather_future.result()
        satelit = satelit_future.result()
        
        #! Kalo gagal fetch
        if tanah["status"] != "success":
            return tanah
        
        if cuaca["status"] != "success":
            return cuaca
        
        if satelit["status"] != "success":
            return satelit

    # # Validasi data tanah
    # if not tanah or "soil" not in tanah:
    #     error_msg = tanah.get("error", "Data tanah tidak ditemukan") if isinstance(tanah, dict) else "Respon tidak valid"
    #     raise ValueError(f"Gagal mendapatkan data tanah dari SoilGrids: {error_msg}")

    # # Validasi data cuaca
    # if not cuaca or "curah_hujan_tahunan" not in cuaca:
    #     raise ValueError("Gagal mendapatkan data cuaca dari OpenMeteo")

    # SOILGRIDS
    soil = tanah["soil"]
    #GEE
    satellite_data = satelit["satellite"]
    
    # cek field wajib dari ketiga sumber sebelum lanjut
    required_soil = ["ph", "sand", "silt", "clay"]
    required_cuaca = ["curah_hujan_tahunan", "curah_hujan_bulanan", "suhu_rata_rata"]
    required_satelit = ["ndvi", "elevasi_m"]
    
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
            
    for f in required_satelit:
        if satellite_data.get(f) is None:
            missing.append(f"satelit.{f}")

    if missing:
        return {
            "status": "error",
            "message": f"Data lahan tidak lengkap: {', '.join(missing)}"
        }

    return {
        "status": "success",

        #data open meteo
        "curah_hujan": cuaca["curah_hujan_tahunan"],
        "curah_hujan_bulanan": cuaca["curah_hujan_bulanan"],  
        "suhu": cuaca["suhu_rata_rata"],
        "et0": cuaca["et0_tahunan"],

        # data soilgrids
        "ph_tanah": soil["ph"],
        "nitrogen": soil["nitrogen"]["value"],
        "organic_carbon": soil["organic_carbon"]["value"],
        "tekstur_kelas": soil.get("tekstur_kelas"),   

        "tekstur_tanah": {
            "sand": soil["sand"]["value"],
            "silt": soil["silt"]["value"],
            "clay": soil["clay"]["value"]
        },
        
        #GEE
        "ndvi": satellite_data.get("ndvi"), 
        "elevasi": satellite_data["elevasi_m"], 

        "kesuburan_tanah": calculate_fertility(soil)
    }