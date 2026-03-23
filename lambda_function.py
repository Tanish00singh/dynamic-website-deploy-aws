import json
import math

def lambda_handler(event, context):
    """
    Health Calculator Lambda — pure math, zero external APIs.
    Calculates: BMI, BMR, TDEE, ideal weight, water intake,
                macro split, health category, tips.
    """

    # ── CORS preflight (browser sends OPTIONS before POST) ──
    if event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return cors_response(200, "")

    # ── Parse body ──
    try:
        body = json.loads(event.get("body") or "{}")
    except Exception:
        return cors_response(400, {"error": "Invalid JSON in request body"})

    # ── Validate inputs ──
    try:
        weight_kg = float(body["weight_kg"])   # e.g. 70
        height_cm = float(body["height_cm"])   # e.g. 175
        age       = int(body["age"])            # e.g. 25
        gender    = body["gender"].lower()      # "male" or "female"
        activity  = body.get("activity", "moderate").lower()
        # activity options: sedentary | light | moderate | active | very_active
    except (KeyError, ValueError, TypeError) as e:
        return cors_response(400, {"error": f"Missing or invalid field: {e}"})

    # ── Guard rails ──
    if not (1 <= weight_kg <= 300):
        return cors_response(400, {"error": "Weight must be between 1 and 300 kg"})
    if not (50 <= height_cm <= 250):
        return cors_response(400, {"error": "Height must be between 50 and 250 cm"})
    if not (1 <= age <= 120):
        return cors_response(400, {"error": "Age must be between 1 and 120"})
    if gender not in ("male", "female"):
        return cors_response(400, {"error": "Gender must be 'male' or 'female'"})

    height_m = height_cm / 100

    # ════════════════════════════════════════
    # 1. BMI  (Body Mass Index)
    # ════════════════════════════════════════
    bmi = round(weight_kg / (height_m ** 2), 1)

    if bmi < 18.5:
        bmi_category = "Underweight"
        bmi_color    = "blue"
    elif bmi < 25:
        bmi_category = "Normal weight"
        bmi_color    = "green"
    elif bmi < 30:
        bmi_category = "Overweight"
        bmi_color    = "orange"
    elif bmi < 35:
        bmi_category = "Obese (Class I)"
        bmi_color    = "red"
    elif bmi < 40:
        bmi_category = "Obese (Class II)"
        bmi_color    = "red"
    else:
        bmi_category = "Obese (Class III)"
        bmi_color    = "red"

    # ════════════════════════════════════════
    # 2. BMR  (Basal Metabolic Rate)
    #    Mifflin-St Jeor Equation
    # ════════════════════════════════════════
    if gender == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    bmr = round(bmr)

    # ════════════════════════════════════════
    # 3. TDEE  (Total Daily Energy Expenditure)
    #    = BMR × activity multiplier
    # ════════════════════════════════════════
    activity_multipliers = {
        "sedentary":   1.2,    # desk job, no exercise
        "light":       1.375,  # light exercise 1-3 days/week
        "moderate":    1.55,   # moderate exercise 3-5 days/week
        "active":      1.725,  # hard exercise 6-7 days/week
        "very_active": 1.9     # physical job + hard exercise
    }
    multiplier = activity_multipliers.get(activity, 1.55)
    tdee = round(bmr * multiplier)

    # ════════════════════════════════════════
    # 4. Calorie goals
    # ════════════════════════════════════════
    calories_maintain  = tdee
    calories_lose      = tdee - 500    # ~0.5 kg/week loss
    calories_gain      = tdee + 300    # lean muscle gain

    # ════════════════════════════════════════
    # 5. Ideal Body Weight range
    #    Devine formula + 10% range
    # ════════════════════════════════════════
    height_inches = height_cm / 2.54
    if gender == "male":
        ibw = 50 + 2.3 * max(0, height_inches - 60)
    else:
        ibw = 45.5 + 2.3 * max(0, height_inches - 60)

    ibw_low  = round(ibw * 0.9, 1)
    ibw_high = round(ibw * 1.1, 1)

    # Healthy BMI weight range (18.5 – 24.9)
    healthy_low  = round(18.5 * (height_m ** 2), 1)
    healthy_high = round(24.9 * (height_m ** 2), 1)

    # ════════════════════════════════════════
    # 6. Daily water intake (ml)
    #    Base: 35 ml per kg body weight
    #    +500 ml if active or very_active
    # ════════════════════════════════════════
    water_ml = round(weight_kg * 35)
    if activity in ("active", "very_active"):
        water_ml += 500
    water_liters = round(water_ml / 1000, 1)
    water_glasses = math.ceil(water_ml / 250)   # 250 ml per glass

    # ════════════════════════════════════════
    # 7. Macro split (grams) for maintenance
    #    Protein: 0.8g × weight (sedentary) → 2g × weight (active)
    #    Fat: 25-30% of calories
    #    Carbs: remainder
    # ════════════════════════════════════════
    protein_per_kg = {"sedentary":0.8,"light":1.2,"moderate":1.6,"active":2.0,"very_active":2.2}
    protein_g = round(weight_kg * protein_per_kg.get(activity, 1.6))
    fat_g     = round((tdee * 0.28) / 9)          # 28% of calories from fat
    carb_cals = tdee - (protein_g * 4) - (fat_g * 9)
    carb_g    = round(max(0, carb_cals) / 4)

    # ════════════════════════════════════════
    # 8. Body fat % estimate
    #    US Navy / Deurenberg formula
    # ════════════════════════════════════════
    # Deurenberg: BF% = (1.2 × BMI) + (0.23 × age) − (10.8 × sex) − 5.4
    sex_val = 1 if gender == "male" else 0
    body_fat_pct = round((1.2 * bmi) + (0.23 * age) - (10.8 * sex_val) - 5.4, 1)
    body_fat_pct = max(3, body_fat_pct)   # clamp minimum

    if gender == "male":
        if body_fat_pct < 6:    bf_category = "Essential fat"
        elif body_fat_pct < 14: bf_category = "Athlete"
        elif body_fat_pct < 18: bf_category = "Fitness"
        elif body_fat_pct < 25: bf_category = "Average"
        else:                   bf_category = "Above average"
    else:
        if body_fat_pct < 14:   bf_category = "Essential fat"
        elif body_fat_pct < 21: bf_category = "Athlete"
        elif body_fat_pct < 25: bf_category = "Fitness"
        elif body_fat_pct < 32: bf_category = "Average"
        else:                   bf_category = "Above average"

    # ════════════════════════════════════════
    # 9. Weight to lose/gain (kg)
    # ════════════════════════════════════════
    midpoint_healthy = (healthy_low + healthy_high) / 2
    weight_diff = round(weight_kg - midpoint_healthy, 1)

    if weight_diff > 0:
        weight_goal_msg = f"Lose ~{weight_diff} kg to reach healthy midpoint"
        weeks_to_goal   = math.ceil(abs(weight_diff) / 0.5)
    elif weight_diff < 0:
        weight_goal_msg = f"Gain ~{abs(weight_diff)} kg to reach healthy midpoint"
        weeks_to_goal   = math.ceil(abs(weight_diff) / 0.25)
    else:
        weight_goal_msg = "You are at your ideal weight midpoint!"
        weeks_to_goal   = 0

    # ════════════════════════════════════════
    # 10. Personalized tips
    # ════════════════════════════════════════
    tips = []

    if bmi < 18.5:
        tips.append("Increase calorie-dense, nutritious foods like nuts, avocado, and whole grains.")
        tips.append("Focus on strength training to build lean muscle mass.")
    elif bmi >= 25:
        tips.append("Create a moderate calorie deficit of 300–500 kcal/day for sustainable loss.")
        tips.append("Prioritize high-volume, low-calorie foods like vegetables and lean proteins.")

    if activity == "sedentary":
        tips.append("Aim for at least 30 minutes of walking daily — it makes a measurable difference.")
    elif activity in ("active", "very_active"):
        tips.append("Ensure adequate sleep (7–9 hours) to support recovery from intense training.")

    if protein_g < 100:
        tips.append("Boost protein intake with eggs, lentils, Greek yogurt, or chicken breast.")

    if age >= 40:
        tips.append("Include calcium and vitamin D sources to maintain bone density.")

    if gender == "female" and age < 50:
        tips.append("Ensure adequate iron intake — leafy greens, legumes, and lean red meat are great sources.")

    tips.append(f"Drink {water_liters}L of water daily — spread across {water_glasses} glasses.")
    tips.append("Track your meals for just 2 weeks — awareness alone improves food choices significantly.")

    # ════════════════════════════════════════
    # 11. Build response
    # ════════════════════════════════════════
    result = {
        "bmi": {
            "value":    bmi,
            "category": bmi_category,
            "color":    bmi_color
        },
        "bmr":  bmr,
        "tdee": tdee,
        "calories": {
            "maintain": calories_maintain,
            "lose":     calories_lose,
            "gain":     calories_gain
        },
        "ideal_weight": {
            "devine_range_kg":  [ibw_low, ibw_high],
            "healthy_bmi_range_kg": [healthy_low, healthy_high]
        },
        "water": {
            "liters":  water_liters,
            "ml":      water_ml,
            "glasses": water_glasses
        },
        "macros": {
            "protein_g": protein_g,
            "fat_g":     fat_g,
            "carbs_g":   carb_g
        },
        "body_fat": {
            "estimated_pct": body_fat_pct,
            "category":      bf_category
        },
        "weight_goal": {
            "message":        weight_goal_msg,
            "weeks_estimate": weeks_to_goal
        },
        "tips": tips
    }

    return cors_response(200, result)


def cors_response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type":                "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers":"Content-Type",
            "Access-Control-Allow-Methods":"POST, OPTIONS"
        },
        "body": json.dumps(body) if body != "" else ""
    }
