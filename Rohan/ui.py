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
    
    villages = ['Rampur Village', 'Keshavpur', 'GreenVillage']
    
    farmers_df = pd.DataFrame({
        'farmer_id': [f'FAR{i:06d}' for i in range(1, 101)],
        'village': np.random.choice(villages, 100),
        'land_size_acres': np.round(np.random.uniform(0.5, 20, 100), 2),
        'kharif_crop': np.random.choice(['Paddy', 'Jowar'], 100),
        'phone_no': ['9' + str(np.random.randint(100000000, 999999999)).zfill(9) for _ in range(100)]
    })
    
    dealers_df = pd.DataFrame({
        'dealer_id': [f'DEA{i:04d}' for i in range(1, 21)],
        'village': np.random.choice(villages, 20)
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
    results = {'high_risk': [], 'warnings': [], 'stats': {}}
    
    try:
        merged = pd.merge(transactions_df, farmers_df, on='farmer_id', how='left')
        
        if not merged.empty and 'land_size_acres' in merged.columns and 'claimed_fertiliser_qty_kg' in merged.columns:
            merged['qty_per_acre'] = merged['claimed_fertiliser_qty_kg'] / merged['land_size_acres']
            high_risk = merged[merged['qty_per_acre'] > 1500][['farmer_id', 'dealer_id', 'claimed_fertiliser_qty_kg', 'land_size_acres', 'qty_per_acre', 'village']].head(10)
            results['high_risk'] = high_risk.to_dict('records')
            
            results['stats'] = {
                'total_high_risk': len(high_risk),
                'avg_qty_per_acre': merged['qty_per_acre'].mean().round(1),
                'max_qty_per_acre': merged['qty_per_acre'].max().round(1)
            }
        
        if 'phone_no' in farmers_df.columns:
            phone_counts = farmers_df['phone_no'].value_counts()
            duplicate_phones = phone_counts[phone_counts > 1]
            results['warnings'] = duplicate_phones.head().to_dict()
            
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
    
    return results

st.title("🛡️ AgriGuard: Subsidy Fraud Detection Dashboard")

with st.sidebar:
    st.header("📂 Upload Datasets")
    farmers_file = st.file_uploader("1. government_farmers.csv", type=['csv'])
    dealers_file = st.file_uploader("2. government_dealers.csv", type=['csv']) 
    relationships_file = st.file_uploader("3. dealer_farmer_relationships.csv", type=['csv'])
    
    use_sample = st.checkbox("✅ Use Sample Data (Recommended)", value=True)

if use_sample:
    farmers_df, dealers_df, transactions_df = create_sample_datasets()
    st.sidebar.success("✅ Sample data loaded")
    st.sidebar.info("💡 Click 'Verify Farmer' below to test")
else:
    farmers_df = load_data(farmers_file)
    dealers_df = load_data(dealers_file)
    transactions_df = load_data(relationships_file)
    
    if any(df is None for df in [farmers_df, dealers_df, transactions_df]):
        st.warning("❌ Please upload all 3 CSV files or use sample data")
        st.stop()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👨‍🌾 Farmers", f"{len(farmers_df):,}")
with col2: 
    st.metric("🏪 Dealers", f"{len(dealers_df):,}")
with col3:
    st.metric("🤝 Relationships", f"{len(transactions_df):,}")

fraud_results = detect_fraud_patterns(farmers_df, transactions_df)

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🚨 High Risk Transactions")
    if fraud_results.get('high_risk'):
        high_risk_df = pd.DataFrame(fraud_results['high_risk'])
        st.dataframe(high_risk_df, use_container_width=True, height=300)
    else:
        st.info("✅ No high-risk transactions (>1500kg/acre)")

with col2:
    st.subheader("📊 Key Metrics")
    if 'stats' in fraud_results:
        st.metric("High Risk Cases", fraud_results['stats'].get('total_high_risk', 0))
        st.metric("Avg Qty/Acre", f"{fraud_results['stats'].get('avg_qty_per_acre', 0)} kg")
        st.metric("Max Qty/Acre", f"{fraud_results['stats'].get('max_qty_per_acre', 0)} kg")

st.markdown("---")

st.subheader("🔍 Geo Analysis - Dealer-Farmer Village Match")
try:
    merged_geo = pd.merge(transactions_df, farmers_df[['farmer_id', 'village']], on='farmer_id')
    merged_geo = pd.merge(merged_geo, dealers_df[['dealer_id', 'village']], on='dealer_id', suffixes=['_farmer', '_dealer'])
    
    village_match = (merged_geo['village_farmer'] == merged_geo['village_dealer']).mean() * 100
    st.metric("Local Dealer Match", f"{village_match:.1f}%")
    
    fig = px.histogram(merged_geo, x='village_farmer', color='village_farmer',
                      title="Farmer Village Distribution", 
                      category_orders={'village_farmer': sorted(merged_geo['village_farmer'].unique())})
    st.plotly_chart(fig, use_container_width=True)
except:
    st.info("✅ Geo analysis ready - upload dealer village data for full analysis")

st.markdown("---")

st.subheader("👤 Verify Specific Farmer")
with st.columns(1)[0]:
    col1, col2 = st.columns(2)
    with col1:
        farmer_id = st.text_input("Enter Farmer ID", placeholder="FAR000001")
    with col2:
        if st.button("🔍 Verify Farmer"):
            if farmer_id in farmers_df['farmer_id'].values:
                farmer_row = farmers_df[farmers_df['farmer_id'] == farmer_id].iloc[0]
                farmer_tx = transactions_df[transactions_df['farmer_id'] == farmer_id]
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("🌾 Village", farmer_row['village'])
                    st.metric("📏 Land", f"{farmer_row['land_size_acres']:.1f} acres")
                with c2:
                    st.metric("🌱 Kharif Crop", farmer_row['kharif_crop'])
                    st.metric("📞 Phone", farmer_row['phone_no'][:4] + "****")
                with c3:
                    st.metric("Claims", len(farmer_tx))
                    if len(farmer_tx) > 0:
                        total_qty = farmer_tx['claimed_fertiliser_qty_kg'].sum()
                        avg_per_acre = total_qty / farmer_row['land_size_acres']
                        color = "normal" if avg_per_acre < 1500 else "inverse"
                        st.metric("Qty/Acre", f"{avg_per_acre:.0f} kg", delta_color=color)
                
                if len(farmer_tx) > 0:
                    st.dataframe(farmer_tx[['dealer_id', 'claimed_fertiliser_qty_kg']].head(), use_container_width=True)
            else:
                st.error("❌ Farmer ID not found")
        else:
            st.info("👆 Enter Farmer ID above and click Verify")

st.markdown("---")
st.caption("🌾 AgriGuard v3.0 | Real-time Subsidy Fraud Detection | Compatible: farmer_id, dealer_id, land_size_acres")
