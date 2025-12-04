import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_enhanced_synthetic_datasets():
    np.random.seed(42)
    villages = [
        'Rampur Village', 'Keshavpur', 'GreenVillage', 'RedSoil Hamlet', 'Balaji Nagar', 
        'Sundarapuram', 'Neelkamal', 'Gokul Vihar', 'Shivaji Colony', 'Lakshmi Puram',
        'Hanumantha Nagar', 'Venkatesh Pura', 'Devi Krupa', 'Raja Rajeshwari', 'Anjaneya Layout',
        'Maruthi Extension', 'Ganesha Nagar', 'Subramanya Swamy', 'Dakshina Mukhi', 'Uttara Phalguni',
        'Pushpagiri', 'Nandi Hills', 'Skanda Giri', 'Bhoga Nandeeshwara', 'Yelachaguppe'
    ]
    crops = [
        'Paddy', 'Wheat', 'Maize', 'Jowar', 'Bajra', 'Ragi', 'Tur/Arhar', 'Gram/Chana', 
        'Green Gram', 'Black Gram', 'Cowpea', 'Groundnut', 'Soybean', 'Sunflower', 'Cotton',
        'Sugarcane', 'Potato', 'Onion', 'Tomato', 'Chilli', 'Brinjal', 'Okra', 'Cauliflower'
    ]
    
    irrigation_types = [
        'Rainfed', 'Borewell', 'Drip', 'Sprinkler', 'Flood', 'Canal', 'Tank', 'Well', 
        'Micro Irrigation', 'Lift Irrigation', 'River Lift', 'Community Lift'
    ]
    soil_types = [
        'Loamy', 'Clay', 'Sandy', 'Red', 'Black (Regur)', 'Laterite', 'Alluvial', 
        'Sandy Loam', 'Silty Clay', 'Red Loam', 'Black Clay', 'Yellow Soil'
    ]
    soil_weights = np.array([0.20, 0.15, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.04, 0.03, 0.05])
    soil_weights = soil_weights / soil_weights.sum()
    irrigation_weights = np.array([0.45, 0.20, 0.08, 0.07, 0.10, 0.05, 0.02, 0.02, 0.01, 0.01, 0.01, 0.01])
    irrigation_weights = irrigation_weights / irrigation_weights.sum()
    
    farm_category_weights = np.array([0.25, 0.35, 0.25, 0.10, 0.05])
  
    n_farmers = 10000
    farmer_data = pd.DataFrame({
        'farmer_id': [f'FAR{i:06d}' for i in range(1, n_farmers+1)],
        'village': np.random.choice(villages, n_farmers),
        'land_size_ha': np.clip(np.random.exponential(2.5, n_farmers), 0.1, 25).round(2),
        'crop_type': np.random.choice(crops, n_farmers),
        'irrigation_type': np.random.choice(irrigation_types, n_farmers, p=irrigation_weights),
        'soil_type': np.random.choice(soil_types, n_farmers, p=soil_weights),
        'last_subsidy_date': pd.date_range('2024-01-01', '2025-11-01', n_farmers).strftime('%Y-%m-%d'),
        'farm_category': np.random.choice(['SC/ST', 'Small (<2ha)', 'Medium (2-5ha)', 'Large (>5ha)', 'Marginal'], 
                                        n_farmers, p=farm_category_weights)
    })
    
   
    n_dealers = 500
    dealer_data = pd.DataFrame({
        'dealer_id': [f'DEA{i:04d}' for i in range(1, n_dealers+1)],
        'dealer_name': [f'Dealer_{i:03d}_Agri' for i in range(1, n_dealers+1)],
        'village': np.random.choice(villages, n_dealers),
        'license_active': np.random.choice([True, False], n_dealers, p=[0.92, 0.08]),
        'license_expiry': pd.date_range('2025-06-01', '2028-12-31', n_dealers).strftime('%Y-%m-%d')
    })
    
    
    core_size = 19000
    core_dealer_farmer = pd.DataFrame({
        'dealer_id': np.random.choice(dealer_data['dealer_id'], core_size),
        'farmer_id': np.random.choice(farmer_data['farmer_id'], core_size),
        'relationship_start_date': pd.date_range('2023-01-01', '2025-06-30', core_size).strftime('%Y-%m-%d'),
        'relationship_status': np.random.choice(['Active', 'Inactive'], core_size, p=[0.88, 0.12]),
        'max_allowed_txns_per_year': np.random.choice([12, 24, 36, 48], core_size, p=[0.3, 0.4, 0.2, 0.1])
    })
    
    fraud_size = 1000
    fraud_dealer_farmer = pd.DataFrame({
        'dealer_id': np.random.choice(dealer_data['dealer_id'], fraud_size),
        'farmer_id': [f'FAKEFAR{i:05d}' for i in range(1, fraud_size+1)],
        'relationship_start_date': pd.date_range('2024-06-01', '2025-11-01', fraud_size).strftime('%Y-%m-%d'),
        'relationship_status': np.random.choice(['Active', 'Inactive'], fraud_size, p=[0.3, 0.7]),
        'max_allowed_txns_per_year': np.random.choice([12, 24], fraud_size)
    })
    
    dealer_farmer_data = pd.concat([core_dealer_farmer, fraud_dealer_farmer], ignore_index=True)
 
    farmer_data.to_csv('government_farmers.csv', index=False)
    dealer_data.to_csv('government_dealers.csv', index=False)
    dealer_farmer_data.to_csv('dealer_farmer_relationships.csv', index=False)
    
    print("✅ ENHANCED DATASETS GENERATED:")
    print(f"   📊 government_farmers.csv: {len(farmer_data):,} records")
    print(f"   🏪 government_dealers.csv: {len(dealer_data):,} records") 
    print(f"   🤝 dealer_farmer_relationships.csv: {len(dealer_farmer_data):,} records")
    print(f"   🎯 Legitimate pairs: {len(core_dealer_farmer):,} (95%)")
    print(f"   🚨 Fraudulent pairs: {len(fraud_dealer_farmer):,} (5%)")
    print("\n📈 Enhanced variety:")
    print(f"   🌾 {len(set(farmer_data['crop_type']))} crop types")
    print(f"   🏘️  {len(set(farmer_data['village']))} villages") 
    print(f"   💧 {len(set(farmer_data['irrigation_type']))} irrigation types")
    print(f"   🟤 {len(set(farmer_data['soil_type']))} soil types")
    
    return farmer_data, dealer_data, dealer_farmer_data

if __name__ == "__main__":
    farmer_data, dealer_data, dealer_farmer_data = generate_enhanced_synthetic_datasets()
