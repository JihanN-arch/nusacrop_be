import requests
from ml_lib.soilgrids_adapter import usda_texture_class

SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"


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


    try:
        response = requests.get(
            SOILGRIDS_URL,
            params=params,
            timeout=30,
            headers={"User-Agent": "NUSA-CROP/1.0 (GEMASTIK Project)"}
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout:
        return {
            "status": "error",
            "source": "soilgrids",
            "message": "Request ke SoilGrids timeout.",
            "soil": None
        }
    except requests.ConnectionError:
        return {
            "status": "error",
            "source": "soilgrids",
            "message": "Tidak dapat terhubung ke SoilGrids.",
            "soil": None
        }
    except requests.HTTPError:
        return {
            "status": "error",
            "source": "soilgrids",
            "message": f"SoilGrids mengembalikan HTTP {response.status_code}.",
            "http_status": response.status_code,
            "soil": None
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "source": "soilgrids",
            "message": str(e),
            "soil": None
        }

    # Kalau response kosong
    if "properties" not in data:
        return {
        "status": "no_data",
        "source": "soilgrids",
        "message": "Data tanah tidak tersedia.",
        "soil": None
        }


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
        
        sand_val = soil_result.get("sand", {}).get("value")
        silt_val = soil_result.get("silt", {}).get("value")
        clay_val = soil_result.get("clay", {}).get("value")
        tekstur_kelas = None
        if sand_val is not None and silt_val is not None and clay_val is not None:
            tekstur_kelas = usda_texture_class(sand_val, silt_val, clay_val)
            
    return {
        "status": "success",
         
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
            "nitrogen": soil_result.get("nitrogen", {
                "value": None,
                "unit": "g/kg"
            }),
            "organic_carbon": soil_result.get("soc", {
                "value": None,
                "unit": "g/kg"
            }),
            "sand": soil_result.get("sand", {
                "value": None,
                "unit": None
            }),
            "silt": soil_result.get("silt", {
                "value": None,
                "unit": None
            }),
            "clay": soil_result.get("clay", {
                "value": None,
                "unit": None
            }),
            "tekstur_kelas" : tekstur_kelas,
        }
    }