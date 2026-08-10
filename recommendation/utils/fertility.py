def calculate_fertility(soil):
    score = 0
    available = 0

    ph = soil.get("ph")
    if ph is not None:
        available += 1
        if 5.5 <= ph <= 7:
            score += 0.4
        elif 5 <= ph < 5.5:
            score += 0.3
        else:
            score += 0.1

    nitrogen = soil.get("nitrogen", {}).get("value")
    if nitrogen is not None:
        available += 1
        if nitrogen > 2:
            score += 0.3
        elif nitrogen > 1:
            score += 0.2
        else:
            score += 0.1

    carbon = soil.get("organic_carbon", {}).get("value")
    if carbon is not None:
        available += 1
        if carbon > 20:
            score += 0.3
        elif carbon > 10:
            score += 0.2
        else:
            score += 0.1

    if available == 0:
        return None

    return round(score, 2)