import requests
import time
from django.core.cache import cache
from ml_lib.soilgrids_adapter import usda_texture_class


SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"

MAX_RETRIES = 3
RETRY_DELAYS = [3, 8, 15]

CACHE_TIMEOUT = 60 * 60 * 24 * 7


def get_soil_data(lat, lon, target_depth="0-5cm"):

    properties = [
        "phh2o",
        "nitrogen",
        "soc",
        "sand",
        "silt",
        "clay"
    ]

    params = [
        ("lon", lon),
        ("lat", lat),
        ("depth", target_depth),
        ("value", "mean"),
    ]

    for prop in properties:
        params.append(("property", prop))


    # ==========================================================
    # MOCK DATA
    # ==========================================================
    # Digunakan kalau SoilGrids gagal setelah semua retry.
    # Struktur dibuat sama dengan response SoilGrids asli.
    
    mock_soil = {
        "ph": 5.8,

        "nitrogen": {
            "value": 2.1,
            "unit": "g/kg"
        },

        "organic_carbon": {
            "value": 18.5,
            "unit": "g/kg"
        },

        "sand": {
            "value": 40.0,
            "unit": "%"
        },

        "silt": {
            "value": 35.0,
            "unit": "%"
        },

        "clay": {
            "value": 25.0,
            "unit": "%"
        },

        "tekstur_kelas": "loam",
    }


    # ==========================================================
    # REQUEST SOILGRIDS + RETRY
    # ==========================================================

    response = None
    data = None

    for attempt in range(MAX_RETRIES):

        try:

            response = requests.get(
                SOILGRIDS_URL,
                params=params,
                timeout=30,
                headers={
                    "User-Agent": "NUSA-CROP/1.0 (GEMASTIK Project)"
                }
            )

            response.raise_for_status()

            data = response.json()

            # Berhasil, keluar dari retry
            break

        except requests.Timeout:

            print(
                f"SoilGrids timeout "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

        except requests.ConnectionError:

            print(
                f"SoilGrids connection error "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

        except requests.HTTPError:

            print(
                f"SoilGrids HTTP {response.status_code} "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

            # HTTP error tertentu layak di-retry.
            # 429 = rate limit
            # 500/502/503/504 = server sementara bermasalah

            if response.status_code not in [
                429,
                500,
                502,
                503,
                504
            ]:
                break

        except requests.RequestException as e:

            print(
                f"SoilGrids request error: {e} "
                f"(attempt {attempt + 1}/{MAX_RETRIES})"
            )

            break


        # Jangan sleep kalau ini sudah attempt terakhir
        if attempt < MAX_RETRIES - 1:

            delay = RETRY_DELAYS[attempt]

            print(
                f"Retry SoilGrids dalam {delay} detik..."
            )

            time.sleep(delay)


    # ==========================================================
    # FALLBACK MOCK DATA
    # ==========================================================

    if data is None:

        print(
            "SoilGrids gagal setelah semua retry. "
            "Menggunakan MOCK DATA."
        )

        return {
            "status": "success",

            "source": "mock",

            "location": {
                "latitude": lat,
                "longitude": lon
            },

            "depth": target_depth,

            "soil": mock_soil
        }


    # ==========================================================
    # KALAU RESPONSE KOSONG
    # ==========================================================

    if "properties" not in data:

        print(
            "Response SoilGrids tidak memiliki properties. "
            "Menggunakan MOCK DATA."
        )

        return {
            "status": "success",

            "source": "mock",

            "location": {
                "latitude": lat,
                "longitude": lon
            },

            "depth": target_depth,

            "soil": mock_soil
        }


    # ==========================================================
    # PARSING DATA SOILGRIDS
    # ==========================================================

    soil_result = {}

    layers = data["properties"].get("layers", [])

    for layer in layers:

        layer_name = layer.get("name")

        unit_measure = layer.get("unit_measure", {})

        target_unit = unit_measure.get("target_units")

        d_factor = unit_measure.get("d_factor")


        # Cari depth yang sesuai
        depth_data = next(
            (
                depth
                for depth in layer.get("depths", [])
                if depth.get("label") == target_depth
            ),
            None
        )


        # Kalau depth tidak ada
        if depth_data is None:

            soil_result[layer_name] = {
                "value": None,
                "unit": target_unit
            }

            continue


        raw_value = (
            depth_data
            .get("values", {})
            .get("mean")
        )


        # Kalau value kosong
        if raw_value is None:

            converted_value = None


        # Kalau faktor konversi tidak ada
        elif d_factor is None or d_factor == 0:

            converted_value = None


        else:

            converted_value = raw_value / d_factor


        soil_result[layer_name] = {
            "value": converted_value,
            "unit": target_unit
        }


    # ==========================================================
    # HITUNG TEKSTUR TANAH
    # ==========================================================

    sand_val = soil_result.get(
        "sand",
        {}
    ).get("value")

    silt_val = soil_result.get(
        "silt",
        {}
    ).get("value")

    clay_val = soil_result.get(
        "clay",
        {}
    ).get("value")


    tekstur_kelas = None

    if (
        sand_val is not None
        and silt_val is not None
        and clay_val is not None
    ):

        tekstur_kelas = usda_texture_class(
            sand_val,
            silt_val,
            clay_val
        )


    # ==========================================================
    # RETURN DATA SOILGRIDS
    # ==========================================================

    return {
        "status": "success",

        "source": "soilgrids",

        "location": {
            "latitude": lat,
            "longitude": lon
        },

        "depth": target_depth,

        "soil": {

            "ph": (
                soil_result.get("phh2o", {}).get("value")
                if soil_result.get("phh2o")
                else None
            ),

            "nitrogen": soil_result.get(
                "nitrogen",
                {
                    "value": None,
                    "unit": "g/kg"
                }
            ),

            "organic_carbon": soil_result.get(
                "soc",
                {
                    "value": None,
                    "unit": "g/kg"
                }
            ),

            "sand": soil_result.get(
                "sand",
                {
                    "value": None,
                    "unit": None
                }
            ),

            "silt": soil_result.get(
                "silt",
                {
                    "value": None,
                    "unit": None
                }
            ),

            "clay": soil_result.get(
                "clay",
                {
                    "value": None,
                    "unit": None
                }
            ),

            "tekstur_kelas": tekstur_kelas,
        }
    }