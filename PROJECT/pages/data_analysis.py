import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="AgriGuard | Subsidy Integrity Platform",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA LOADING ---
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

# --- LARGE SCALE DATA GENERATION (10k Farmers) ---
def create_sample_datasets():
    """Generates 10,000 farmers and ensures FAR010000 is always a valid test case."""
    np.random.seed(42)
    
    # Configuration
    N_FARMERS = 10000
    N_DEALERS = 200
    N_TRANSACTIONS = 20000
    
    villages = ['Rampur', 'Keshavpur', 'GreenVillage', 'Sonpur', 'Lakhanpur', 'Madhopur', 'Bishanpur']
    crops = ['Paddy', 'Jowar', 'Bajra', 'Wheat', 'Maize']
    
    # 1. Generate Farmers
    farmers_df = pd.DataFrame({
        'farmer_id': [f'FAR{i:06d}' for i in range(1, N_FARMERS + 1)],
        'village': np.random.choice(villages, N_FARMERS),
        'land_size_acres': np.round(np.random.uniform(0.5, 15, N_FARMERS), 2),
        'kharif_crop': np.random.choice(crops, N_FARMERS),
        'phone_no': ['9' + str(np.random.randint(100000000, 999999999)).zfill(9) for _ in range(N_FARMERS)]
    })
    
    # --- TEST CASE INJECTION: Make FAR010000 interesting ---
    # We force the last farmer (FAR010000) to have specific details for testing
    idx_10k = N_FARMERS - 1
    farmers_df.at[idx_10k, 'village'] = 'TestVillage'
    farmers_df.at[idx_10k, 'land_size_acres'] = 2.0  # Small land
    farmers_df.at[idx_10k, 'phone_no'] = '9999999999' # Shared phone number trigger
    
    # Create another farmer sharing this phone number to trigger Benami
    farmers_df.at[idx_10k - 1, 'phone_no'] = '9999999999' 

    # 2. Generate Dealers
    dealers_df = pd.DataFrame({
        'dealer_id': [f'DEA{i:04d}' for i in range(1, N_DEALERS + 1)],
        'village': np.random.choice(villages, N_DEALERS)
    })
    
    # 3. Generate Transactions
    t_farmer_ids = np.random.choice(farmers_df['farmer_id'], N_TRANSACTIONS)
    t_dealer_ids = np.random.choice(dealers_df['dealer_id'], N_TRANSACTIONS)
    
    # Ensure FAR010000 has transactions
    # We replace the last 5 transactions with FAR010000
    t_farmer_ids[-5:] = 'FAR010000'
    
    land_map = dict(zip(farmers_df['farmer_id'], farmers_df['land_size_acres']))
    t_land_sizes = np.array([land_map[fid] for fid in t_farmer_ids])
    
    t_qtys = (t_land_sizes * 200 * np.random.uniform(0.8, 1.2, N_TRANSACTIONS)).round(0)
    
    # Inject Fraud: Make FAR010000 overclaim massively
    # Since FAR010000 is at the end (-5:), we multiply those quantities
    t_qtys[-5:] = t_qtys[-5:] * 10  # 10x normal amount -> High Risk
    
    transactions_df = pd.DataFrame({
        'transaction_id': [f'TXN{i:06d}' for i in range(1, N_TRANSACTIONS + 1)],
        'date': [
            (datetime.today() - timedelta(days=np.random.randint(0, 365))).strftime('%Y-%m-%d')
            for _ in range(N_TRANSACTIONS)
        ],
        'dealer_id': t_dealer_ids,
        'farmer_id': t_farmer_ids,
        'claimed_fertiliser_qty_kg': t_qtys
    })
    
    return farmers_df, dealers_df, transactions_df

# --- FRAUD DETECTION LOGIC ---
def detect_fraud_patterns(farmers_df, transactions_df):
    results = {'high_risk': [], 'warnings': [], 'stats': {}}
    
    try:
        merged = pd.merge(transactions_df, farmers_df, on='farmer_id', how='left')
        
        if not merged.empty and 'land_size_acres' in merged.columns and 'claimed_fertiliser_qty_kg' in merged.columns:
            merged['qty_per_acre'] = merged['claimed_fertiliser_qty_kg'] / merged['land_size_acres']
            high_risk = merged[merged['qty_per_acre'] > 1500].copy()
            
            display_cols = ['farmer_id', 'dealer_id', 'claimed_fertiliser_qty_kg', 'land_size_acres', 'qty_per_acre', 'village']
            display_cols = [c for c in display_cols if c in high_risk.columns]
            
            results['high_risk'] = high_risk[display_cols].sort_values('qty_per_acre', ascending=False).head(50).to_dict('records')
            
            results['stats'] = {
                'total_high_risk': len(high_risk),
                'avg_qty_per_acre': merged['qty_per_acre'].mean().round(1),
                'max_qty_per_acre': merged['qty_per_acre'].max().round(1)
            }
        
        if 'phone_no' in farmers_df.columns:
            phone_counts = farmers_df['phone_no'].value_counts()
            duplicate_phones = phone_counts[phone_counts > 1]
            results['warnings'] = duplicate_phones.head(10).to_dict()
            
    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
    
    return results

# --- MAIN APP UI ---

st.title("🛡️ AgriGuard: Subsidy Fraud Detection Dashboard")

with st.sidebar:
    st.header("📂 Upload Datasets")
    farmers_file = st.file_uploader("1. government_farmers.csv", type=['csv'])
    dealers_file = st.file_uploader("2. government_dealers.csv", type=['csv']) 
    relationships_file = st.file_uploader("3. dealer_farmer_relationships.csv", type=['csv'])
    
    st.markdown("---")
    use_sample = st.checkbox("✅ Use Large Sample Data (10k Farmers)", value=True)

if use_sample:
    # Use session state to keep data persistent
    if 'farmers_df' not in st.session_state:
        with st.spinner("Generating 10,000 farmers and 20,000 transactions..."):
            f, d, t = create_sample_datasets()
            st.session_state['farmers_df'] = f
            st.session_state['dealers_df'] = d
            st.session_state['trans_df'] = t
    
    farmers_df = st.session_state['farmers_df']
    dealers_df = st.session_state['dealers_df']
    transactions_df = st.session_state['trans_df']
    
    st.sidebar.success("✅ Large scale sample data loaded")
else:
    farmers_df = load_data(farmers_file)
    dealers_df = load_data(dealers_file)
    transactions_df = load_data(relationships_file)
    
    if any(df is None for df in [farmers_df, dealers_df, transactions_df]):
        st.warning("❌ Please upload all 3 CSV files or use sample data")
        st.stop()

# Top Metrics
col1, col2, col3 = st.columns(3)
with col1: st.metric("👨‍🌾 Farmers", f"{len(farmers_df):,}")
with col2: st.metric("🏪 Dealers", f"{len(dealers_df):,}")
with col3: st.metric("🤝 Transactions", f"{len(transactions_df):,}")

# Run Detection
fraud_results = detect_fraud_patterns(farmers_df, transactions_df)

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("🚨 Top High Risk Transactions")
    if fraud_results.get('high_risk'):
        st.dataframe(pd.DataFrame(fraud_results['high_risk']), use_container_width=True, height=300)
    else:
        st.success("✅ No high-risk transactions (>1500kg/acre) detected.")

with col2:
    st.subheader("📊 Key Metrics")
    if 'stats' in fraud_results:
        st.metric("High Risk Alerts", fraud_results['stats'].get('total_high_risk', 0))
        st.metric("Avg Usage (kg/acre)", f"{fraud_results['stats'].get('avg_qty_per_acre', 0)}")
        st.metric("Max Outlier (kg/acre)", f"{fraud_results['stats'].get('max_qty_per_acre', 0)}")

st.markdown("---")

# Farmer Verification Tool
st.subheader("👤 Verify Specific Farmer")
with st.container():
    col1, col2 = st.columns([1, 2])
    with col1:
        # PRE-FILLED WITH VALID TEST ID
        search_input = st.text_input("Enter Farmer ID", value="FAR010000")
        check_btn = st.button("🔍 Verify Farmer")
        
    with col2:
        if check_btn and search_input:
            # --- ROBUST SMART SEARCH LOGIC ---
            raw_input = search_input.strip()
            
            # 1. Extract digits only to handle "FAR 10000" or "10000"
            digits = "".join(filter(str.isdigit, raw_input))
            
            search_candidates = []
            
            # Candidate A: Exact input
            search_candidates.append(raw_input)
            
            # Candidate B: Formatted ID (FAR + 6 digits)
            if digits:
                formatted_id = f"FAR{int(digits):06d}"
                search_candidates.append(formatted_id)
                # Also try without FAR if the dataset uses plain numbers
                search_candidates.append(digits) 
                try:
                    search_candidates.append(int(digits)) 
                except: pass

            # Try to find a match
            found_id = None
            for candidate in search_candidates:
                if candidate in farmers_df['farmer_id'].values:
                    found_id = candidate
                    break
            
            if found_id:
                st.success(f"**Found Farmer:** {found_id}")
                
                # Fetch Data
                farmer_row = farmers_df[farmers_df['farmer_id'] == found_id].iloc[0]
                farmer_tx = transactions_df[transactions_df['farmer_id'] == found_id]
                
                # Profile
                c1, c2, c3 = st.columns(3)
                with c1: st.metric("Village", farmer_row['village'])
                with c2: st.metric("Land Size", f"{farmer_row['land_size_acres']:.2f} ac")
                with c3: st.metric("Crop", farmer_row['kharif_crop'])
                
                # Transaction Analysis
                total_qty = farmer_tx['claimed_fertiliser_qty_kg'].sum() if not farmer_tx.empty else 0
                avg_per_acre = total_qty / farmer_row['land_size_acres'] if farmer_row['land_size_acres'] > 0 else 0
                
                # Risk Logic
                is_high_risk = avg_per_acre > 1500
                
                # Benami Check (Shared Phone)
                phone = str(farmer_row['phone_no'])
                is_benami = False
                if 'warnings' in fraud_results and phone in fraud_results['warnings']:
                    is_benami = True
                
                # Status Display
                if is_high_risk or is_benami:
                    st.error("🔴 **HIGH RISK DETECTED**")
                    if is_high_risk:
                        st.write(f"⚠️ **Over-claiming:** {total_qty} kg for {farmer_row['land_size_acres']} acres ({avg_per_acre:.0f} kg/acre)")
                    if is_benami:
                        st.write(f"⚠️ **Benami Suspect:** Phone number `{phone}` is shared with other farmers.")
                else:
                    st.success("🟢 **NORMAL STATUS**")
                    st.write(f"Total Claimed: **{total_qty} kg** (Avg {avg_per_acre:.0f} kg/acre)")
                
                if not farmer_tx.empty:
                    st.dataframe(farmer_tx, use_container_width=True)
                else:
                    st.info("No transaction history found.")
            else:
                st.error(f"❌ Farmer ID '{search_input}' not found.")
                st.write(f"Tried searching for: {', '.join(map(str, search_candidates))}")
                st.info("Tip: The sample dataset uses IDs like **FAR000001** to **FAR010000**.")

st.markdown("---")
st.caption("🌾 AgriGuard v3.0 | Real-time Subsidy Fraud Detection")