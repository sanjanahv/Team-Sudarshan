# risk_engine.py

import pandas as pd 

CROPS = ["Rice", "Jowar", "Wheat", "Oats"]  # Supported crops
SOILS = ["Alluvial", "Clay", "Loamy", "Red", "Black (Regur)", "Sandy Loam"]  # Supported soils

HECTARE_PER_ACRE = 1 / 2.47105  # Conversion factor

fertilizer_data = {
    "Rice": {
        "Alluvial": 300, "Clay": 280, "Loamy": 290,
        "Red": 310, "Black (Regur)": 270, "Sandy Loam": 330
    },
    "Jowar": {
        "Alluvial": 180, "Clay": 160, "Loamy": 170,
        "Red": 190, "Black (Regur)": 165, "Sandy Loam": 210
    },
    "Wheat": {
        "Alluvial": 220, "Clay": 200, "Loamy": 210,
        "Red": 230, "Black (Regur)": 205, "Sandy Loam": 250
    },
    "Oats": {
        "Alluvial": 200, "Clay": 180, "Loamy": 190,
        "Red": 210, "Black (Regur)": 185, "Sandy Loam": 230
    }
}  # Fertilizer (kg/ha)

crop_soil_compatibility = {
    "Rice": ["Alluvial", "Clay", "Loamy"],
    "Jowar": ["Red", "Black (Regur)", "Loamy"],
    "Wheat": ["Alluvial", "Loamy", "Clay"],
    "Oats": ["Loamy", "Alluvial", "Sandy Loam"]
}  # Crop-soil compatibility

# Government data (trusted)
farmers_df = pd.read_csv("government_farmers.csv")           # farmer_id, aadhar_no, village, land_size_acres, kharif_crop, rabi_crop, soil_type, ...
dealers_df = pd.read_csv("government_dealers.csv")           # dealer_id, dealer_name, village, license_active, ...
relations_df = pd.read_csv("dealer_farmer_relationships.csv")  # dealer_id, farmer_id, claimed_fertiliser_qty_kg, relationship_status, max_allowed_txns_per_year, ...


def find_farmer(farmer_id):
    farmer_id = str(farmer_id).strip() # farmer_id as string
    rec = farmers_df[farmers_df["farmer_id"].astype(str).str.strip() == farmer_id] 
    return None if rec.empty else rec.iloc[0]


def find_dealer(dealer_id):
    dealer_id = str(dealer_id).strip() # dealer_id as string
    rec = dealers_df[dealers_df["dealer_id"].astype(str).str.strip() == dealer_id]
    return None if rec.empty else rec.iloc[0]


def get_relationship(dealer_id, farmer_id):
    rel = relations_df[
        (relations_df["dealer_id"] == dealer_id) &
        (relations_df["farmer_id"] == farmer_id) # Exact match on both IDs
    ]
    return None if rel.empty else rel.iloc[-1]


def get_farmer_crop(farmer_row):
    kharif = str(farmer_row["kharif_crop"]).strip().lower()
    rabi = str(farmer_row["rabi_crop"]).strip().lower()

    if kharif and kharif != "nan": #seasonal crop available
        return kharif.capitalize(), 0, []

    if rabi and rabi != "nan":
        return rabi.capitalize(), 0, []

    return None, 30, ["No crop declared in government record"]


def crop_match_risk(input_crop, farmer_row):
    entered = input_crop.strip().lower() # user input crop

    kharif = str(farmer_row["kharif_crop"]).strip().lower()
    rabi = str(farmer_row["rabi_crop"]).strip().lower()

    # Either match is acceptable
    if entered == kharif or entered == rabi:
        return 0, []

    # If no crop exists in govt but farmer entered something
    if (kharif == "" or kharif == "nan") and (rabi == "" or rabi == "nan"):
        return 30, ["No crop registered in government data"]

    return 40, ["Entered crop does not match government record"]


def identity_risk(farmer, dealer):
    score = 0
    reasons = []

    if farmer is None: # farmer not found
        score += 60
        reasons.append("Farmer not in government registry")

    if dealer is None: # dealer not found
        score += 80
        reasons.append("Dealer not in government registry")
    else:
        if dealer["license_active"] == False: # dealer license inactive
            score += 40
            reasons.append("Dealer license inactive")

    return score, reasons


def location_risk(farmer_village, dealer_village):
    if str(farmer_village).lower().strip() != str(dealer_village).lower().strip():
        return 20, ["Village mismatch"]
    return 0, []


def relationship_risk(rel):
    score = 0
    reasons = []

    if rel["relationship_status"] != "Active":
        score += 40
        reasons.append("Inactive dealer–farmer relationship")

    farmer_txn_count = relations_df[
        (relations_df["dealer_id"] == rel["dealer_id"]) &
        (relations_df["farmer_id"] == rel["farmer_id"])
    ]

    if len(farmer_txn_count) > rel["max_allowed_txns_per_year"]:
        score += 30
        reasons.append("Exceeded transaction limit")

    return score, reasons


def crop_soil_risk(crop, soil):
    if crop in crop_soil_compatibility:
        if soil not in crop_soil_compatibility[crop]:
            return 25, ["Crop–soil mismatch"]
    return 0, []


def expected_fertilizer(crop, soil, land_acres):
    land_hectares = land_acres * HECTARE_PER_ACRE
    per_ha = fertilizer_data[crop][soil]
    return land_hectares * per_ha


def quantity_risk(expected, actual):
    score = 0
    issues = []

    ratio = actual / expected

    if ratio > 1.8:
        score += 40
        issues.append("Extremely excessive fertilizer")
    elif ratio > 1.4:
        score += 25
        issues.append("Excess fertility use")
    elif ratio > 1.1:
        score += 10
        issues.append("Slight overuse")
    elif ratio < 0.6:
        score += 20
        issues.append("Unusually low usage")

    return score, issues


def decision(score):
    if score > 80:
        return "BLOCK"
    elif score > 60:
        return "REVIEW"
    elif score > 30:
        return "MONITOR"
    return "APPROVE"


def evaluate_risk(input_farmer):
    """
    input_farmer should contain:
    {
        "farmer_id": str,
        "Dealer_ID": str,
        "Crop": str,        # from UI
        "village": str,     # from UI (optional for now)
        "land_size": float  # from UI (optional, not yet used in calc)
    }
    """
    total_score = 0
    reasons = []

    dealer_id = input_farmer["Dealer_ID"]
    input_crop = input_farmer["Crop"]

    farmer = find_farmer(input_farmer["farmer_id"])
    dealer = find_dealer(dealer_id)

    # Identity
    s, r = identity_risk(farmer, dealer)
    total_score += s
    reasons += r

    if farmer is None or dealer is None:
        return {
            "Decision": decision(total_score),
            "Risk_Score": total_score,
            "Expected_Fertilizer_kg": None,
            "Claimed_Fertilizer_kg": None,
            "Reasons": " | ".join(reasons)
        }

    # Crop OR logic (from govt data)
    crop, s, r = get_farmer_crop(farmer)
    total_score += s
    reasons += r

    # User input vs govt crops
    s, r = crop_match_risk(input_crop, farmer)
    total_score += s
    reasons += r

    soil = farmer["soil_type"]

    # Crop–soil compatibility
    s, r = crop_soil_risk(input_crop, soil)
    total_score += s
    reasons += r

    # Location match (govt farmer village vs dealer village)
    s, r = location_risk(farmer["village"], dealer["village"])
    total_score += s
    reasons += r

    # Relationship check
    rel = get_relationship(dealer_id, farmer["farmer_id"])
    if rel is None:
        total_score += 50
        reasons.append("Dealer not authorised for this farmer")
        return {
            "Decision": decision(total_score),
            "Risk_Score": total_score,
            "Expected_Fertilizer_kg": None,
            "Claimed_Fertilizer_kg": None,
            "Reasons": " | ".join(reasons)
        }

    s, r = relationship_risk(rel)
    total_score += s
    reasons += r

    # Fertilizer calc
    expected = expected_fertilizer(input_crop, soil, farmer["land_size_acres"])
    claimed = rel["claimed_fertiliser_qty_kg"]

    s, r = quantity_risk(expected, claimed)
    total_score += s
    reasons += r

    return {
        "Risk_Score": total_score,
        "Decision": decision(total_score),
        "Expected_Fertilizer_kg": round(expected, 2),
        "Claimed_Fertilizer_kg": claimed,
        "Reasons": " | ".join(reasons)
    }
