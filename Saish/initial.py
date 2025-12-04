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
        if np.random.random() < 0.5:
            land_sizes.append(np.random.uniform(0.1, 1.0))
        elif np.random.random() < 0.35:
            land_sizes.append(np.random.uniform(1.0, 2.0))
        elif np.random.random() < 0.10:
            land_sizes.append(np.random.uniform(2.0, 5.0))
        else:
            land_sizes.append(np.random.uniform(5.0, 25.0))
    
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
    
    farmer_aadhar = []
    for _ in range(n_farmers):
        part1 = str(np.random.randint(1000, 9999)).zfill(4)
        part2 = str(np.random.randint(100000000, 999999999)).zfill(9)
        farmer_aadhar.append(part1 + part2)
    
    farmer_phone = ['9' + str(np.random.randint(100000000, 999999999)).zfill(9) for _ in range(n_farmers)]
    
    farmer_data = pd.DataFrame({
        'farmer_id': [f'FAR{i:06d}' for i in range(1, n_farmers+1)],
        'aadhar_no': farmer_aadhar,
        'phone_no': farmer_phone,
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
    
    dealer_aadhar = []
    for _ in range(n_dealers):
        part1 = str(np.random.randint(2000, 2999)).zfill(4)
        part2 = str(np.random.randint(100000000, 999999999)).zfill(9)
        dealer_aadhar.append(part1 + part2)
    
    dealer_data = pd.DataFrame({
        'dealer_id': [f'DEA{i:04d}' for i in range(1, n_dealers+1)],
        'aadhar_no': dealer_aadhar,
        'dealer_name': [f'Dealer_{i:03d}_Agri' for i in range(1, n_dealers+1)],
        'village': np.random.choice(villages, n_dealers),
        'license_active': np.random.choice([True, False], n_dealers, p=[0.92, 0.08]),
        'license_expiry': pd.date_range('2025-06-01', '2028-12-31', n_dealers).strftime('%Y-%m-%d')
    })
    
    core_size = 19000
    core_dealer_farmer = pd.DataFrame({
        'dealer_id': np.random.choice(dealer_data['dealer_id'], core_size),
        'dealer_aadhar': '',
        'farmer_id': np.random.choice(farmer_data['farmer_id'], core_size),
        'relationship_date': pd.date_range('2023-01-01', '2025-06-30', core_size).strftime('%Y-%m-%d'),
        'claimed_fertiliser_qty_kg': np.random.uniform(500, 5000, core_size).round(0),
        'relationship_status': np.random.choice(['Active', 'Inactive'], core_size, p=[0.88, 0.12]),
        'max_allowed_txns_per_year': np.random.choice([12, 24, 36, 48], core_size, p=[0.3, 0.4, 0.2, 0.1])
    })
    
    for idx in core_dealer_farmer.index:
        dealer_id = core_dealer_farmer.loc[idx, 'dealer_id']
        matching_aadhar = dealer_data[dealer_data['dealer_id'] == dealer_id]['aadhar_no'].iloc[0]
        core_dealer_farmer.loc[idx, 'dealer_aadhar'] = matching_aadhar
    
    fraud_size = 1000
    fraud_dealer_farmer = pd.DataFrame({
        'dealer_id': np.random.choice(dealer_data['dealer_id'], fraud_size),
        'dealer_aadhar': np.random.choice(dealer_data['aadhar_no'].tolist() + ['FAKEAADHAR123456789012'], fraud_size),
        'farmer_id': [f'FAKEFAR{i:05d}' for i in range(1, fraud_size+1)],
        'relationship_date': pd.date_range('2024-06-01', '2025-11-01', fraud_size).strftime('%Y-%m-%d'),
        'claimed_fertiliser_qty_kg': np.random.uniform(10000, 50000, fraud_size).round(0),
        'relationship_status': np.random.choice(['Active', 'Inactive'], fraud_size, p=[0.3, 0.7]),
        'max_allowed_txns_per_year': np.random.choice([12, 24], fraud_size)
    })
    
    dealer_farmer_data = pd.concat([core_dealer_farmer, fraud_dealer_farmer], ignore_index=True)
    
    farmer_data.to_csv('government_farmers.csv', index=False)
    dealer_data.to_csv('government_dealers.csv', index=False)
    dealer_farmer_data.to_csv('dealer_farmer_relationships.csv', index=False)
    
    print("✅ Datasets generated successfully!")
    print(f"   📊 Farmers: {len(farmer_data):,} | 🏪 Dealers: {len(dealer_data):,} | 🤝 Relationships: {len(dealer_farmer_data):,}")
    
    return farmer_data, dealer_data, dealer_farmer_data

if __name__ == "__main__":
    farmer_data, dealer_data, dealer_farmer_data = generate_enhanced_synthetic_datasets()
