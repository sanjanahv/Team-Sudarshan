import pandas as pd

CROPS = ["Rice", "Jowar", "Wheat", "Oats"] # Supported crops

SOILS = ["Alluvial", "Clay", "Loamy", "Red", "Black (Regur)", "Sandy Loam"]

# Crop–soil realism table
crop_soil_compatibility = {
    "Rice": ["Alluvial", "Clay", "Loamy"],
    "Jowar": ["Red", "Black (Regur)", "Loamy"],
    "Wheat": ["Alluvial", "Loamy", "Clay"],
    "Oats": ["Loamy", "Alluvial", "Sandy Loam"] 
} # crop: [compatible soils

farmers_df = pd.read_csv("Gov_Farmers.csv")   # Aadhaar,Name,Place,Crop,Land_Acres,Soil_Type,Phone
dealers_df = pd.read_csv("Gov_Dealers.csv")   # Dealer_ID,Dealer_Name,Place,License_Status
claims_df  = pd.read_csv("Dealer_Claims.csv") # Dealer_ID,Aadhaar,Date,Fertilizer_kg


def find_farmer(name, aadhaar):
    """
    Docstring for find_farmer
    
    :param name: to match the name
    :param aadhaar: to evaluate the identity
    """
    aadhaar = str(aadhaar).strip()
    match = farmers_df[
        (farmers_df["Aadhaar"].astype(str).str.strip() == aadhaar) &
        (farmers_df["Name"].str.lower().str.strip() == name.lower().strip())
    ]
    return None if match.empty else match.iloc[0]


def find_dealer(dealer_id):
    """
    Docstring for find_dealer
    
    :param dealer_id: to find in registry
    """
    dealers = dealers_df[dealers_df["Dealer_ID"].astype(str) == str(dealer_id)] #match dealer_id
    return None if dealers.empty else dealers.iloc[0]


def identity_risk(farmer, dealer):
    """
    Docstring for identity_risk
    
    :param farmer: to check if it matches government records
    :param dealer: to check if it matches government records
    """
    score = 0 #initialise to zero
    reasons = [] #list to hold reasons

    if farmer is None: #farmer not found
        score += 60
        reasons.append("Farmer not in government database")

    if dealer is None: #dealer not found
        score += 80
        reasons.append("Dealer not found in registry")
    else:
        if str(dealer["License_Status"]).lower() != "active": #license inactive
            score += 30
            reasons.append("Dealer license inactive")

    return score, reasons


def crop_input_risk(crop): 
    """
    Docstring for crop_input_risk
    
    :param crop: if crop present in supported crops
    """
    if crop not in CROPS: #check if crop is valid
        return 40, ["Crop not recognized"]
    return 0, []


def soil_input_risk(soil):
    """
    Docstring for soil_input_risk
    
    :param soil: if soil present in supported soils
    """
    if soil not in SOILS: #check if soil is valid
        return 30, ["Soil type not recognized"]
    return 0, []


def crop_soil_risk(crop, soil):
    """
    Docstring for crop_soil_risk
    
    :param crop: if crop present in supported crops
    :param soil: if soil compatible with crop
    """
    if crop in crop_soil_compatibility: #key
        if soil not in crop_soil_compatibility[crop]:#value
            return 25, ["Crop–soil mismatch"] #key value mismatch
    return 0, []


def location_risk(farmer_place, dealer_place):
    """
    Docstring for location_risk
    
    :param farmer_place: if farmer and dealer places match
    :param dealer_place: if farmer and dealer places match
    """
    if str(farmer_place).lower().strip() != str(dealer_place).lower().strip():
        return 20, ["Dealer–farmer location mismatch"] #places do not match
    return 0, []


def velocity_risk(dealer_id):
    """
    Docstring for velocity_risk
    
    :param dealer_id: to check number of claims made by dealer
    """
    dealer_records = claims_df[claims_df["Dealer_ID"] == dealer_id]

    if len(dealer_records) > 50:
        return 30, ["Very high dealer activity"] #more than 50 claims
    elif len(dealer_records) > 20:
        return 10, ["High dealer activity"] #more than 20 claims

    return 0, []
