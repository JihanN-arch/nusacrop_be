import requests
from datetime import date, timedelta
from collections import defaultdict
from ml_lib.climate_features import monthly_from_daily

OPENMETEO_URL = "https://archive-api.open-meteo.com/v1/archive"

def get_weather_data(lat, lon): 
    end_date = date.today() - timedelta(days=7)
    start_date = end_date - timedelta(days=365)
    
    params = {
        "latitude" : lat,
        "longitude" : lon,
        "start_date" : start_date.isoformat(),
        "end_date" : end_date.isoformat(),
        "daily": [
                "precipitation_sum",
                "et0_fao_evapotranspiration",
                "temperature_2m_mean"
            ],
        "timezone" : "Asia/Jakarta"
    }
    
    try:
        response = requests.get(OPENMETEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
    except requests.Timeout:
        return {
            "status": "error",
            "source": "openmeteo",
            "message": "OpenMeteo timeout."
        }
    except requests.ConnectionError:
        return {
            "status": "error",
            "source": "openmeteo",
            "message": "Tidak dapat terhubung ke OpenMeteo."
        }
    except requests.HTTPError:
        return {
            "status": "error",
            "source": "openmeteo",
            "message": f"HTTP {response.status_code}",
            "http_status": response.status_code
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "source": "openmeteo",
            "message": str(e)
        }
    
    daily_data = data.get("daily", {})
    dates = daily_data.get("time", [])
    
    # curah hujan
    rainfall_val = [v for v in daily_data.get("precipitation_sum", []) if v is not None]
    total_rainfall = (sum(rainfall_val) if rainfall_val else None)
    
    # suhu rata2
    temp_val = [v for v in daily_data.get("temperature_2m_mean", []) if v is not None]
    avg_temp = (sum(temp_val) / len(temp_val) if temp_val else None)
    
    # evaporasi tahunan
    et0_val = [v for v in daily_data.get("et0_fao_evapotranspiration", [])]
    total_et0 = (sum(et0_val) if et0_val else None)

    curah_hujan_bulanan = monthly_from_daily(dates, daily_data.get("precipitation_sum", []))
    raw_monthly = monthly_from_daily(dates, daily_data.get("precipitation_sum", []))
    curah_hujan_bulanan = [round(v, 1) for v in raw_monthly] if raw_monthly else None

    return{
        "status" : "success",
        "curah_hujan_tahunan" : round(total_rainfall, 1) if total_rainfall is not None else None,
        "curah_hujan_bulanan": curah_hujan_bulanan, 
        "suhu_rata_rata" : round(avg_temp, 1) if avg_temp is not None else None,
        "et0_tahunan" : round(total_et0, 1) if total_et0 is not None else None,
        "elevasi" : data.get("elevation"),
    }
    
