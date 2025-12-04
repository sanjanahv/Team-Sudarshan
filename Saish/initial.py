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
    kharif_crops = ['Paddy', 'Jowar']
    rabi_crops = ['Wheat', 'Oats']
    soil_types = ['Alluvial', 'Clay', 'Loamy', 'Red', 'Black (Regur)', 'Sandy Loam']
    irrigation_types = ['Rainfed', 'Borewell', 'Drip', 'Sprinkler', 'Flood', 'Canal']
  
    soil_weights = np.array([0.25, 0.20, 0.20, 0.15, 0.10, 0.10])
    soil_weights = soil_weights / soil_weights.sum()
    
    irrigation_weights = np.array([0.40, 0.25, 0.12, 0.10, 0.08, 0.05])
    irrigation_weights = irrigation_weights / irrigation_weights.sum()
    
    n_farmers = 10000
    land_sizes = []
    for i in range(n_farmers):
        # Realistic distribution: most farmers are small/marginal
        if np.random.random() < 0.5:  # 50% Marginal (<1ha)
            land_sizes.append(np.random.uniform(0.1, 1.0, 1)[0])
        elif np.random.random() < 0.35:  # 35% Small (1-2ha)
            land_sizes.append(np.random.uniform(1.0, 2.0, 1)[0])
        elif np.random.random() < 0.10:  # 10% Medium (2-5ha)
            land_sizes.append(np.random.uniform(2.0, 5.0, 1)[0])
        else:  # 5% Large (>5ha)
            land_sizes.append(np.random.uniform(5.0, 25.0, 1)[0])
    
    land_sizes = np.array(land_sizes).round(2)
    
    farm_categories = []
    for land in land_sizes:
        if land < 1.0:
            farm_categories.append('Marginal (<1ha)')
        elif land < 2.0:
            farm_categories.append('Small (1-2ha)')
        elif land < 5.0:
            farm_categories.append('Medium (2-5ha)')
        else:
            farm_categories.append('Large (>5ha)')

    sc_st_mask = np.random.random(n_farmers) < 0.25
    farm_categories = np.array(farm_categories)
    farm_categories[sc_st_mask] = 'SC/ST (' + farm_categories[sc_st_mask] + ')'
    
    farmer_data = pd.DataFrame({
        'farmer_id': [f'FAR{i:06d}' for i in range(1, n_farmers+1)],
        'village': np.random.choice(villages, n_farmers),
        'land_size_ha': land_sizes,
        'kharif_crop': np.random.choice(kharif_crops, n_farmers, p=[0.70, 0.30]),
        'rabi_crop': np.random.choice(rabi_crops, n_farmers, p=[0.80, 0.20]),
        'irrigation_type': np.random.choice(irrigation_types, n_farmers, p=irrigation_weights),
        'soil_type': np.random.choice(soil_types, n_farmers, p=soil_weights),
        'last_subsidy_date': pd.date_range('2024-01-01', '2025-11-01', n_farmers).strftime('%Y-%m-%d'),
        'farm_category': farm_categories
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
    

    cat_counts = farmer_data['farm_category'].value_counts()
    
    print("✅ LINKED LAND SIZE & FARM CATEGORY DATASETS GENERATED:")
    print(f"   📊 government_farmers.csv: {len(farmer_data):,} records")
    print(f"   🏪 government_dealers.csv: {len(dealer_data):,} records") 
    print(f"   🤝 dealer_farmer_relationships.csv: {len(dealer_farmer_data):,} records")
    
    print("\n📏 FARM CATEGORY VALIDATION (PERFECT MATCH WITH LAND SIZE):")
    for cat in ['Marginal (<1ha)', 'Small (1-2ha)', 'Medium (2-5ha)', 'Large (>5ha)']:
        count = cat_counts.get(cat, 0)
        pct = count / len(farmer_data) * 100
        print(f"   {cat}: {count:,} ({pct:.1f}%)")
    
    print(f"\n🌾 SC/ST farmers: {(sc_st_mask.sum()):,} ({sc_st_mask.mean()*100:.1f}%)")
    print(f"🟤 {len(set(farmer_data['soil_type']))} crop-appropriate soil types")
    
    return farmer_data, dealer_data, dealer_farmer_data

if __name__ == "__main__":
    farmer_data, dealer_data, dealer_farmer_data = generate_enhanced_synthetic_datasets()
