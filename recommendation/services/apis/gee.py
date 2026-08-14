import os
import ee
import time
import json

MAX_RETRIES = 2
RETRY_DELAYS = [1]

_gee_initialized = False

def init_gee():
    global _gee_initialized
    if _gee_initialized:
        return
    
    # dari env
    key_json_str = os.getenv("GEE_SERVICE_ACCOUNT_KEY_JSON")
    
    if key_json_str:
        key_dict = json.loads(key_json_str)
        service_account = key_dict["client_email"]
        credentials = ee.ServiceAccountCredentials(service_account, key_data=key_json_str)
    
    #kalo lokal
    else:
        service_account = os.getenv("GEE_SERVICE_ACC_EMAIL")
        key_path = os.getenv("GEE_SERVICE_ACC_KEY_PATH")
        credentials = ee.ServiceAccountCredentials(service_account, key_path)
        
    ee.Initialize(credentials)
    _gee_initialized = True
    
def get_satellite_data(lat,lon):
    
    mock_satellite = {
        "ndvi": 0.55,
        "elevasi_m": 500,
    }
    
    # request GEE + retry
    result = None
    
    for attemp in range(MAX_RETRIES):
        try: 
            init_gee()
            point = ee.Geometry.Point([lon,lat])
    
            s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(point)
                .filterDate("2025-01-01", "2026-01-01")
                .sort("CLOUDY_PIXEL_PERCENTAGE")
                .first())
    
            # NDVI
            ndvi = s2.normalizedDifference(["B8", "B4"]).rename("NDVI")
            ndvi_value = ndvi.reduceRegion(ee.Reducer.mean(), point, 10).get("NDVI").getInfo()

            # ELEVASI
            srtm = ee.Image("USGS/SRTMGL1_003")
            elevation_value = srtm.reduceRegion(ee.Reducer.mean(), point, 30).get("elevation").getInfo()

            if ndvi_value is None or elevation_value is None:
                print(
                    f"GEE return nilai kosong"
                    f"(attempt {attemp + 1}/{MAX_RETRIES})"
                )
            else:
                result = {
                    "ndvi" : round(ndvi_value, 4),
                    "elevasi_m" : round(elevation_value),
                }
                break
        except Exception as e:
            print(
                f"GEE error: {e}"
                f"(attempt {attemp +1}/{MAX_RETRIES})"
            )
        
        if attemp < MAX_RETRIES - 1:
            delay = RETRY_DELAYS[attemp]
            print(f"Retry GEE dalam {delay} detik")
            time.sleep(delay)
            
        # fallback mock data
    if result is None:
        print("GEE gagal setelah semua retry. Menggunakan MOCK DATA")
        return{
            "status": "success",
            "source": "mock",
            "location": {"latitude": lat, "longitude": lon},
            "satellite": mock_satellite,
        }
        
    return {
        "status": "success",
        "source": "gee",
        "location": {"latitude": lat, "longitude": lon},
        "satellite": result,
    }