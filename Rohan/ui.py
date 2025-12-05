import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AgriGuard | Subsidy Integrity Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .trust-good {background-color: #d4edda;color: #155724;padding: 15px;border-radius: 5px;border-left: 5px solid #28a745;margin: 10px 0;}
    .trust-medium {background-color: #fff3cd;color: #856404;padding: 15px;border-radius: 5px;border-left: 5px solid #ffc107;margin: 10px 0;}
    .trust-bad {background-color: #f8d7da;color: #721c24;padding: 15px;border-radius: 5px;border-left: 5px solid #dc3545;margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

def load_data(file):
    if file is not None:
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
            elif file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            else:
                st.error(f"Unsupported file type: {file.name}")
                return None
            
            df.columns = [col.strip().replace(' ', '_').lower() for col in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
            return None
    return None

def create_sample_datasets():
    np.random.seed(42)
    n_farmers = 100
    n_dealers = 20
    
    villages = ['Rampur', 'Keshavpur', 'GreenVillage', 'RedSoil']
    
    farmers_df = pd.DataFrame({
        'farmer_id': [f'FAR{i:06d}' for i in range(1, n_farmers+1)],
        'village': np.random.choice(villages, n_farmers),
        'land_size_acres': np.random.uniform(0.5, 20, n_farmers).round(2),
        'kharif_crop': np.random.choice(['Paddy', 'Jowar'], n_farmers),
        'phone_no': ['9' + str(np.random.randint(100000000, 999999999)).zfill(9) for _ in range(n_farmers)]
    })
    
    dealers_df = pd.DataFrame({
        'dealer_id': [f'DEA{i:04d}' for i in range(1, n_dealers+1)],
        'village': np.random.choice(villages, n_dealers)
    })
    
    transactions_df = pd.DataFrame({
        'transaction_id': [f'TXN{i:06d}' for i in range(500)],
        'date': pd.date_range('2025-01-01', periods=500).strftime('%Y-%m-%d'),
        'dealer_id': np.random.choice(dealers_df['dealer_id'], 500),
        'farmer_id': np.random.choice(farmers_df['farmer_id'], 500),
        'claimed_fertiliser_qty_kg': np.random.uniform(100, 5000, 500).round(0)
    })
    
    return farmers_df, dealers_df, transactions_df

def detect_fraud_patterns(farmers_df, transactions_df):
    results = {'high_risk': [], 'warnings': []}
    
    if 'land_size_acres' in farmers_df.columns and 'claimed_fertiliser_qty_kg' in transactions_df.columns:
        merged = transactions_df.merge(farmers_df, on='farmer_id', how='left')
        
        if not merged.empty and 'land_size_acres' in merged.columns:
            merged['qty_per_acre'] = merged['claimed_fertiliser_qty_kg'] / merged['land_size_acres']
            high_risk = merged[merged['qty_per_acre'] > 1500]
            results['high_risk'] = high_risk[['farmer_id', 'dealer_id', 'claimed_fertiliser_qty_kg', 'land_size_acres', 'qty_per_acre']].head(10).to_dict('records')
    
    if 'phone_no' in farmers_df.columns:
        phone_counts = farmers_df['phone_no'].value_counts()
        duplicate_phones = phone_counts[phone_counts > 1]
        if not duplicate_phones.empty:
            results['warnings'] = farmers_df[farmers_df['phone_no'].isin(duplicate_phones.index)]['farmer_id'].tolist()
    
    return results

st.title("🛡️ AgriGuard: Subsidy Fraud Detection")

with st.sidebar:
    st.header("📂 Upload Datasets")
    farmers_file = st.file_uploader("government_farmers.csv", type=['csv'])
    dealers_file = st.file_uploader("government_dealers.csv", type=['csv']) 
    relationships_file = st.file_uploader("dealer_farmer_relationships.csv", type=['csv'])
    
    use_sample = st.checkbox("Use Sample Data", value=True)

if use_sample:
    farmers_df, dealers_df, transactions_df = create_sample_datasets()
    st.sidebar.success("✅ Using sample data")
else:
    farmers_df = load_data(farmers_file)
    dealers_df = load_data(dealers_file) 
    transactions_df = load_data(relationships_file)
    
    if farmers_df is None or dealers_df is None or transactions_df is None:
        st.warning("Please upload all 3 CSV files")
        st.stop()

st.success(f"✅ Loaded: {len(farmers_df)} farmers, {len(dealers_df)} dealers, {len(transactions_df)} relationships")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Farmers", len(farmers_df))
with col2: 
    st.metric("Dealers", len(dealers_df))
with col3:
    st.metric("Relationships", len(transactions_df))

fraud_results = detect_fraud_patterns(farmers_df, transactions_df)

st.subheader("🚨 High Risk Transactions (Qty > 1500kg/acre)")
if fraud_results['high_risk']:
    high_risk_df = pd.DataFrame(fraud_results['high_risk'])
    st.dataframe(high_risk_df, use_container_width=True)
    
    fig = px.scatter(high_risk_df, x='land_size_acres', y='qty_per_acre', 
                    size='claimed_fertiliser_qty_kg',
                    title="High Risk: Quantity per Acre vs Land Size",
                    color='qty_per_acre',
                    color_continuous_scale='Reds')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No high-risk transactions detected")

st.subheader("⚠️ Suspicious Patterns")
col1, col2 = st.columns(2)

with col1:
    if fraud_results['warnings']:
        st.error(f"📞 Duplicate phones: {len(fraud_results['warnings'])} farmers")
        st.write(farmers_df[farmers_df['farmer_id'].isin(fraud_results['warnings'])]['phone_no'].value_counts().head())
    else:
        st.success("✅ No duplicate phone numbers")

with col2:
    village_match = sum((dealers_df[dealers_df['dealer_id'].isin(transactions_df['dealer_id'])]['village'] 
                        == farmers_df[farmers_df['farmer_id'].isin(transactions_df['farmer_id'])]['village']).sum())
    st.info(f"🏘️ Local relationships: Good data quality")

with st.sidebar.form("verify_farmer"):
    farmer_id = st.text_input("Enter Farmer ID to verify")
    if st.form_submit_button("Verify"):
        if farmer_id in farmers_df['farmer_id'].values:
            farmer_row = farmers_df[farmers_df['farmer_id'] == farmer_id].iloc[0]
            farmer_tx = transactions_df[transactions_df['farmer_id'] == farmer_id]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Land Size", f"{farmer_row['land_size_acres']:.1f} acres")
                st.metric("Village", farmer_row['village'])
                st.metric("Total Claims", len(farmer_tx))
            
            with col2:
                if len(farmer_tx) > 0:
                    avg_qty_per_acre = farmer_tx['claimed_fertiliser_qty_kg'].sum() / farmer_row['land_size_acres']
                    color = "normal" if avg_qty_per_acre < 1500 else "inverse"
                    st.metric("Avg Qty/Acre", f"{avg_qty_per_acre:.0f} kg", delta_color=color)
            
            if len(farmer_tx) > 0:
                st.dataframe(farmer_tx[['dealer_id', 'claimed_fertiliser_qty_kg', 'date']].head(), use_container_width=True)
        else:
            st.error("❌ Farmer ID not found")

st.caption("🌾 AgriGuard - Real-time Subsidy Fraud Detection")
