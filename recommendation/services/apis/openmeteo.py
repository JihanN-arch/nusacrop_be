import requests
import time
from datetime import date, timedelta
from collections import defaultdict
from ml_lib.climate_features import monthly_from_daily

OPENMETEO_URL = "https://archive-api.open-meteo.com/v1/archive"

MAX_RETRIES = 2 
RETRY_DELAYS = [1]


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
    
    # mock data
    mock_weather = {
        "curah_hujan_tahunan": 2100.0,
        "curah_hujan_bulanan": [
            250.0, 230.0, 210.0, 180.0, 120.0, 80.0,
            60.0, 50.0, 70.0, 130.0, 200.0, 240.0,
        ],
        "suhu_rata_rata": 27.0,
        "et0_tahunan": 1400.0,
    }
    
    # req open-meteo + retry
    response = None
    data = None
    
    for attempt in range(MAX_RETRIES):
        
        try:
            response = requests.get(OPENMETEO_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            break
            
        except requests.Timeout:
            print(f"OpenMeteo timeout (attempt {attempt + 1}/{MAX_RETRIES})")
            
        except requests.ConnectionError:
            print(f"OpenMeteo connection error (attempt {attempt + 1}/{MAX_RETRIES})")
            
        except requests.HTTPError:
            print(
                f"OpenMeteo HTTP {response.status_code} "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )
            if response.status_code not in [429,500,502,503,504]:
                break
            
        except requests.RequestException as e:
            print(f"OpenMeteo request error: {e} (attempt {attempt + 1}/{MAX_RETRIES})")
            break
        
        if attempt < MAX_RETRIES -1:
            delay = RETRY_DELAYS[attempt]
            print(f"Retry OpenMeteo dalam {delay} detik")
            time.sleep(delay)
    
    # fallback mock data
    if data is None:
        print("OpenMeteo gagal setelah semua retry. Menggunakan MOCK DATA")
        
        return{
            "status": "success",
            "source": "mock",
            **mock_weather,
        }
        
    # parsing data meteo     
    daily_data = data.get("daily", {})
    dates = daily_data.get("time", [])
    
    # curah hujan tahunan
    rainfall_val = [v for v in daily_data.get("precipitation_sum", []) if v is not None]
    total_rainfall = (sum(rainfall_val) if rainfall_val else None)
    
    # suhu rata2
    temp_val = [v for v in daily_data.get("temperature_2m_mean", []) if v is not None]
    avg_temp = (sum(temp_val) / len(temp_val) if temp_val else None)
    
    # evaporasi tahunan
    et0_val = [v for v in daily_data.get("et0_fao_evapotranspiration", [])]
    total_et0 = (sum(et0_val) if et0_val else None)

    # curah hujan bulanan
    curah_hujan_bulanan = monthly_from_daily(dates, daily_data.get("precipitation_sum", []))
    raw_monthly = monthly_from_daily(dates, daily_data.get("precipitation_sum", []))
    curah_hujan_bulanan = [round(v, 1) for v in raw_monthly] if raw_monthly else None


    # kalo ada data yg kuranng dia bakal kirim mock data keselurhn
    if total_rainfall is None and avg_temp is None:
        print("OpenMeteo response tidak memiliki data yang valid. Menggunakan MOCK DATA.")
        
        return {
            "status": "success",
            "source": "mock",
            **mock_weather,
        }
    
    # return data klo succes   
    return{
        "status": "success",
        "source": "openmeteo",
        "curah_hujan_tahunan": round(total_rainfall, 1) if total_rainfall is not None else None,
        "curah_hujan_bulanan": curah_hujan_bulanan,
        "suhu_rata_rata": round(avg_temp, 1) if avg_temp is not None else None,
        "et0_tahunan": round(total_et0, 1) if total_et0 is not None else None,
    }
    
