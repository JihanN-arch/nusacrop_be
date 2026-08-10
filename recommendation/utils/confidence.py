def get_confidence(score : float) -> str:
    if score >= 0.95:
        return "Sangat Tinggi"

    elif score >= 0.85:
        return "Tinggi"

    elif score >= 0.65:
        return "Sedang"

    else:
        return "Rendah"