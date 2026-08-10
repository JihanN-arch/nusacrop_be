def generate_reason(environment_data, crop_data):
    reasons = []

    syarat = crop_data["syarat_tumbuh"]
    nama = crop_data["nama"]

    # pH
    ph_reason = check_ph(environment_data, syarat, nama)
    if ph_reason:
        reasons.append(ph_reason)

    #curah hujan
    rainfall_reason = check_rainfall(environment_data, syarat, nama)
    if rainfall_reason:
        reasons.append(rainfall_reason)

    #elevasi
    elevation_reason = check_elevation(environment_data, syarat, nama)
    if elevation_reason:
        reasons.append(elevation_reason)


    if not reasons:
        reasons.append(
            "Rekomendasi berdasarkan kesesuaian keseluruhan kondisi lingkungan."
        )

    return reasons


def check_ph(environment_data, syarat, nama):
    ph = environment_data.get("ph_tanah")

    if ph is None:
        return None

    ph_min = float(syarat["ph"]["min"])
    ph_max = float(syarat["ph"]["max"])

    if ph_min <= ph <= ph_max:
        return f"pH tanah ({ph}) sesuai dengan kebutuhan {nama}"

    return None


def check_rainfall(environment_data, syarat, nama):
    rainfall = environment_data.get("curah_hujan")

    if rainfall is None:
        return None

    rain_min = float(syarat["curah_hujan"]["min"])
    rain_max = float(syarat["curah_hujan"]["max"])

    if rain_min <= rainfall <= rain_max:
        return (
            f"Curah hujan ({rainfall} mm/tahun) sesuai dengan kebutuhan {nama}"
        )

    return None


def check_elevation(environment_data, syarat, nama):
    elevation = environment_data.get("elevasi")

    if elevation is None:
        return None

    elev_min = float(syarat["elevasi"]["min"])
    elev_max = float(syarat["elevasi"]["max"])

    if elev_min <= elevation <= elev_max:
        return (
            f"Elevasi ({elevation} mdpl) sesuai untuk pertumbuhan {nama}"
        )

    return None