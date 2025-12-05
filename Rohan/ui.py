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
    .trust-good {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 10px 0;
    }
    .trust-medium {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 10px 0;
    }
    .trust-bad {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
        margin: 10px 0;
    }
    .trust-score-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .data-warning {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
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
            
            df.columns = [col.strip() for col in df.columns]
            return df
        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
            return None
    return None

def create_sample_datasets():
    """Create sample datasets for demonstration"""
    np.random.seed(42)
    
    # Sample Farmers Data
    sample_farmers = pd.DataFrame({
        'FarmerID': [f'F{i:03d}' for i in range(1, 21)],
        'Name': [f'Farmer {i}' for i in range(1, 21)],
        'District': np.random.choice(['Bangalore', 'Mysore', 'Tumkur', 'Kolar', 'Mandya'], 20),
        'LandSize_Hectares': np.round(np.random.uniform(1, 10, 20), 1),
        'PrimaryCrop': np.random.choice(['Rice', 'Wheat', 'Sugarcane', 'Cotton', 'Maize'], 20),
        'BankAccount': [f'12345678{i:02d}' for i in range(1, 21)],
        'Aadhar': [f'1234567890{i:02d}' for i in range(1, 21)]
    })
    
    # Sample Dealers Data
    sample_dealers = pd.DataFrame({
        'DealerID': [f'D{i:03d}' for i in range(1, 11)],
        'DealerName': [f'Dealer {i}' for i in range(1, 11)],
        'District': np.random.choice(['Bangalore', 'Mysore', 'Tumkur', 'Kolar'], 10)
    })
    
    # Sample Transactions Data
    transactions = []
    for i in range(1, 101):
        farmer_id = np.random.choice(sample_farmers['FarmerID'])
        dealer_id = np.random.choice(sample_dealers['DealerID'])
        date = pd.to_datetime('2024-01-01') + timedelta(days=np.random.randint(0, 365))
        
        # Get farmer's land size to calculate reasonable quantity
        farmer_land = sample_farmers[sample_farmers['FarmerID'] == farmer_id]['LandSize_Hectares'].values[0]
        reasonable_quantity = farmer_land * 100  # 100kg per hectare
        
        # Introduce some fraud patterns
        if farmer_id == 'F001':  # Over-claiming farmer
            quantity = reasonable_quantity * np.random.uniform(1.8, 2.5)
        elif farmer_id in ['F002', 'F003']:  # Benami farmers (same bank account)
            quantity = reasonable_quantity * np.random.uniform(0.8, 1.2)
        else:
            quantity = reasonable_quantity * np.random.uniform(0.5, 1.5)
        
        transactions.append({
            'TransID': f'T{i:04d}',
            'Date': date.strftime('%Y-%m-%d'),
            'DealerID': dealer_id,
            'FarmerID': farmer_id,
            'Fertilizer_Type': np.random.choice(['Urea', 'DAP', 'MOP', 'NPK']),
            'Quantity_KG': int(quantity)
        })
    
    sample_transactions = pd.DataFrame(transactions)
    
    return sample_farmers, sample_dealers, sample_transactions

def detect_fraud_patterns(merged_df, farmers_df):
    
    results = {
        'benami_farmers': pd.DataFrame(),
        'overclaim_farmers': pd.DataFrame(),
        'suspicious_dealers': pd.DataFrame(),
        'risk_scores': {}
    }
    
    if 'BankAccount' in farmers_df.columns:
        bank_counts = farmers_df['BankAccount'].value_counts()
        suspicious_banks = bank_counts[bank_counts > 1].index.tolist()
        
        if suspicious_banks:
            benami_df = farmers_df[farmers_df['BankAccount'].isin(suspicious_banks)]
            benami_df = benami_df.merge(
                farmers_df.groupby('BankAccount')['FarmerID'].count().reset_index(),
                on='BankAccount',
                suffixes=('', '_Count')
            )
            benami_df = benami_df.rename(columns={'FarmerID_Count': 'Shared_Account_Count'})
            results['benami_farmers'] = benami_df
    
    if 'LandSize_Hectares' in merged_df.columns and 'Quantity_KG' in merged_df.columns:
        merged_df['Expected_Usage_KG'] = merged_df['LandSize_Hectares'] * 100
        merged_df['Claim_Ratio'] = merged_df['Quantity_KG'] / merged_df['Expected_Usage_KG']
        
        overclaim_df = merged_df[merged_df['Claim_Ratio'] > 1.5].groupby('FarmerID').agg({
            'Quantity_KG': 'sum',
            'Expected_Usage_KG': 'sum',
            'Claim_Ratio': 'mean'
        }).reset_index()
        results['overclaim_farmers'] = overclaim_df
    
    if 'DealerID' in merged_df.columns:
        dealer_volumes = merged_df.groupby('DealerID')['Quantity_KG'].sum().reset_index()
        avg_volume = dealer_volumes['Quantity_KG'].mean()
        std_volume = dealer_volumes['Quantity_KG'].std()
        
        if not pd.isna(std_volume) and std_volume > 0:
            dealer_volumes['Z_Score'] = (dealer_volumes['Quantity_KG'] - avg_volume) / std_volume
            suspicious_dealers = dealer_volumes[dealer_volumes['Z_Score'] > 2]
            results['suspicious_dealers'] = suspicious_dealers
    
    risk_scores = {}
    for farmer_id in merged_df['FarmerID'].unique():
        score = 0
        farmer_data = merged_df[merged_df['FarmerID'] == farmer_id]
        
        if 'Claim_Ratio' in farmer_data.columns:
            max_ratio = farmer_data['Claim_Ratio'].max()
            if max_ratio > 1.5:
                score += min(50, (max_ratio - 1.5) * 20)
        
        if 'Date' in farmer_data.columns:
            farmer_data_sorted = farmer_data.sort_values('Date')
            time_diffs = farmer_data_sorted['Date'].diff().dt.total_seconds() / 3600
            
            rapid_transactions = (time_diffs < 24).sum()
            if rapid_transactions > 2:
                score += min(30, rapid_transactions * 10)
        
        if farmer_id in results['benami_farmers']['FarmerID'].values:
            score += 40
        
        risk_scores[farmer_id] = min(100, score)
    
    results['risk_scores'] = risk_scores
    
    return results

def verify_farmer_trust(farmer_id, aadhar_number, farmers_df, merged_df, fraud_results):
    
    if farmer_id not in farmers_df['FarmerID'].values:
        return {
            'status': 'error',
            'message': 'Farmer ID not found in database',
            'trust_score': 0,
            'details': {}
        }
    
    farmer_details = farmers_df[farmers_df['FarmerID'] == farmer_id].iloc[0]
    farmer_transactions = merged_df[merged_df['FarmerID'] == farmer_id]
    
    verification = {
        'farmer_id': farmer_id,
        'farmer_name': farmer_details.get('Name', 'Unknown'),
        'district': farmer_details.get('District', 'Unknown'),
        'land_size': farmer_details.get('LandSize_Hectares', 0),
        'crop': farmer_details.get('PrimaryCrop', 'Unknown'),
        'bank_account': farmer_details.get('BankAccount', 'Unknown'),
        'total_claims': len(farmer_transactions),
        'total_quantity': farmer_transactions['Quantity_KG'].sum() if not farmer_transactions.empty else 0,
        'checks_passed': 0,
        'total_checks': 5,
        'risk_factors': [],
        'trust_level': 'Unknown',
        'trust_score': 0
    }
    
    if aadhar_number:
        if 'Aadhar' in farmer_details and str(farmer_details['Aadhar']) == str(aadhar_number):
            verification['aadhar_match'] = True
            verification['checks_passed'] += 1
        else:
            verification['aadhar_match'] = False
            verification['risk_factors'].append('Aadhar number does not match')
    
    if verification['land_size'] > 0 and verification['total_quantity'] > 0:
        expected_usage = verification['land_size'] * 100
        claim_ratio = verification['total_quantity'] / expected_usage
        
        if claim_ratio <= 1.5:
            verification['checks_passed'] += 1
            verification['claim_ratio'] = round(claim_ratio, 2)
        else:
            verification['risk_factors'].append(f'Over-claiming: Using {claim_ratio:.1f}x expected amount')
            verification['claim_ratio'] = round(claim_ratio, 2)
    
    bank_account = verification['bank_account']
    if bank_account != 'Unknown':
        same_bank_count = len(farmers_df[farmers_df['BankAccount'] == bank_account])
        if same_bank_count == 1:
            verification['checks_passed'] += 1
            verification['bank_unique'] = True
        else:
            verification['risk_factors'].append(f'Bank account shared with {same_bank_count-1} other farmers')
            verification['bank_unique'] = False
    
    if not farmer_transactions.empty:
        if 'Date' in farmer_transactions.columns:
            farmer_transactions = farmer_transactions.sort_values('Date')
            time_diffs = farmer_transactions['Date'].diff().dt.total_seconds() / 3600
            
            rapid_claims = (time_diffs < 24).sum()
            if rapid_claims <= 2:
                verification['checks_passed'] += 1
                verification['transaction_pattern'] = 'Normal'
            else:
                verification['risk_factors'].append(f'Multiple claims ({rapid_claims}) within 24 hours')
                verification['transaction_pattern'] = 'Suspicious'
    
    risk_score = fraud_results['risk_scores'].get(farmer_id, 0)
    verification['risk_score'] = risk_score
    
    if risk_score < 30:
        verification['checks_passed'] += 1
    else:
        verification['risk_factors'].append(f'High risk score: {risk_score}/100')
    
    trust_score = (verification['checks_passed'] / verification['total_checks']) * 100
    trust_score = max(0, trust_score - risk_score/2)
    
    verification['trust_score'] = round(trust_score)
    
    if trust_score >= 70:
        verification['trust_level'] = 'Highly Trustworthy'
        verification['color'] = 'green'
    elif trust_score >= 40:
        verification['trust_level'] = 'Moderately Trustworthy'
        verification['color'] = 'orange'
    else:
        verification['trust_level'] = 'Requires Investigation'
        verification['color'] = 'red'
    
    return verification

st.title("🛡️ AgriGuard: Subsidy Integrity Platform")

st.sidebar.title("📂 Data Upload")
st.sidebar.info("Upload your three datasets below to begin analysis.")

with st.sidebar:
    st.header("📤 Upload Files")
    
    farmers_file = st.file_uploader(
        "1. Government → Farmers Dataset",
        type=['csv', 'xlsx'],
        key="farmers",
        help="Should contain FarmerID, Name, District, LandSize_Hectares, PrimaryCrop, BankAccount"
    )
    
    dealers_file = st.file_uploader(
        "2. Government → Dealers Dataset",
        type=['csv', 'xlsx'],
        key="dealers",
        help="Should contain DealerID, DealerName, Location"
    )
    
    transactions_file = st.file_uploader(
        "3. Dealers → Farmers Transactions",
        type=['csv', 'xlsx'],
        key="transactions",
        help="Should contain TransID, Date, DealerID, FarmerID, Fertilizer_Type, Quantity_KG"
    )
    
    st.sidebar.markdown("---")
    
    use_sample_data = st.sidebar.checkbox("📊 Use Sample Data", value=False, 
                                        help="Use built-in sample data for demonstration")

farmers_df = None
dealers_df = None
transactions_df = None
using_sample_data = False

if use_sample_data:
    st.sidebar.warning("⚠️ Using sample dataset for demonstration")
    farmers_df, dealers_df, transactions_df = create_sample_datasets()
    using_sample_data = True
else:
    farmers_df = load_data(farmers_file)
    dealers_df = load_data(dealers_file)
    transactions_df = load_data(transactions_file)

if not use_sample_data and (farmers_df is None or dealers_df is None or transactions_df is None):
    st.warning("""
    ⚠️ **No data files uploaded!** 
    
    Please either:
    1. Upload your own CSV/Excel files in the sidebar, OR
    2. Check the **"Use Sample Data"** checkbox to load built-in sample data
    """)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Required Format:**")
        st.code("""Farmers Dataset:
FarmerID,Name,District,
LandSize_Hectares,PrimaryCrop,
BankAccount,Aadhar""")
    
    with col2:
        st.markdown("**📋 Required Format:**")
        st.code("""Dealers Dataset:
DealerID,DealerName,District""")
    
    with col3:
        st.markdown("**📋 Required Format:**")
        st.code("""Transactions Dataset:
TransID,Date,DealerID,
FarmerID,Fertilizer_Type,
Quantity_KG""")
    
    st.info("💡 **Quick Start:** Check 'Use Sample Data' in the sidebar to see the system in action!")
    st.stop()

data_loaded = all(df is not None for df in [farmers_df, dealers_df, transactions_df])

if using_sample_data and data_loaded:
    st.sidebar.success("✅ Sample data loaded successfully!")
    st.sidebar.info(f"📊 Sample Data Info:")
    st.sidebar.write(f"- Farmers: {len(farmers_df)} records")
    st.sidebar.write(f"- Dealers: {len(dealers_df)} records")
    st.sidebar.write(f"- Transactions: {len(transactions_df)} records")
    
    with st.expander("📋 View Sample Data"):
        tab1, tab2, tab3 = st.tabs(["Farmers", "Dealers", "Transactions"])
        with tab1:
            st.dataframe(farmers_df.head(10), use_container_width=True)
        with tab2:
            st.dataframe(dealers_df.head(10), use_container_width=True)
        with tab3:
            st.dataframe(transactions_df.head(10), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.header("🔍 Farmer Trust Verification")

has_aadhar = False
if farmers_df is not None:
    aadhar_col = next((col for col in farmers_df.columns if 'aadhar' in col.lower()), None)
    has_aadhar = aadhar_col is not None

with st.sidebar.form("trust_verification"):
    farmer_id_input = st.text_input("Enter Farmer ID:", placeholder="e.g., F001")
    
    if has_aadhar:
        aadhar_input = st.text_input("Enter Aadhar Number (Optional):", placeholder="12-digit Aadhar")
    else:
        st.info("Aadhar column not found in data")
        aadhar_input = ""
    
    verify_button = st.form_submit_button("✅ Verify Trustworthiness")

fraud_results = None
merged_df = pd.DataFrame()

if data_loaded:
    try:
        farmer_id_col = next((col for col in farmers_df.columns if 'farmer' in col.lower() and 'id' in col.lower()), 'FarmerID')
        dealer_id_col = next((col for col in dealers_df.columns if 'dealer' in col.lower() and 'id' in col.lower()), 'DealerID')
        
        merged_df = transactions_df.merge(farmers_df, left_on='FarmerID', right_on=farmer_id_col, how='inner')
        
        if 'Date' in merged_df.columns:
            merged_df['Date'] = pd.to_datetime(merged_df['Date'], errors='coerce')
        
        fraud_results = detect_fraud_patterns(merged_df, farmers_df)
        
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")

if verify_button and farmer_id_input:
    if fraud_results is None:
        st.error("Data processing failed. Please check your data files.")
    else:
        verification_result = verify_farmer_trust(
            farmer_id_input, 
            aadhar_input, 
            farmers_df, 
            merged_df, 
            fraud_results
        )
        
        st.markdown("---")
        st.header("📋 Farmer Trust Verification Results")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Farmer: {verification_result['farmer_name']}")
            
            details_col1, details_col2 = st.columns(2)
            
            with details_col1:
                st.metric("District", verification_result['district'])
                st.metric("Land Size", f"{verification_result['land_size']} Ha")
            
            with details_col2:
                st.metric("Primary Crop", verification_result['crop'])
                st.metric("Total Claims", verification_result['total_claims'])
        
        with col2:
            trust_score = verification_result['trust_score']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=trust_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Trust Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': verification_result['color']},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 70], 'color': "lightyellow"},
                        {'range': [70, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            
            fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        if verification_result['color'] == 'green':
            st.markdown(f"""
            <div class="trust-good">
                <h3>✅ {verification_result['trust_level']}</h3>
                <p>This farmer appears to be legitimate based on available data.</p>
                <p><strong>Checks Passed:</strong> {verification_result['checks_passed']}/{verification_result['total_checks']}</p>
            </div>
            """, unsafe_allow_html=True)
        elif verification_result['color'] == 'orange':
            st.markdown(f"""
            <div class="trust-medium">
                <h3>⚠️ {verification_result['trust_level']}</h3>
                <p>This farmer has some suspicious patterns that require attention.</p>
                <p><strong>Checks Passed:</strong> {verification_result['checks_passed']}/{verification_result['total_checks']}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="trust-bad">
                <h3>❌ {verification_result['trust_level']}</h3>
                <p>This farmer shows multiple red flags that require immediate investigation.</p>
                <p><strong>Checks Passed:</strong> {verification_result['checks_passed']}/{verification_result['total_checks']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if verification_result['risk_factors']:
            st.subheader("🚨 Risk Factors Identified")
            for risk in verification_result['risk_factors']:
                st.error(f"• {risk}")
        
        st.subheader("📊 Detailed Metrics")
        
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
        
        with metrics_col1:
            st.metric("Total Quantity Claimed", f"{verification_result['total_quantity']:.0f} KG")
        
        with metrics_col2:
            if 'claim_ratio' in verification_result:
                ratio = verification_result['claim_ratio']
                if ratio > 1.5:
                    st.metric("Claim Ratio", f"{ratio:.1f}x", delta="High", delta_color="inverse")
                else:
                    st.metric("Claim Ratio", f"{ratio:.1f}x", delta="Normal", delta_color="normal")
        
        with metrics_col3:
            if 'aadhar_match' in verification_result:
                if verification_result['aadhar_match']:
                    st.metric("Aadhar Verification", "✅ Verified")
                else:
                    st.metric("Aadhar Verification", "❌ Mismatch")
        
        if not merged_df.empty:
            st.subheader("📝 Recent Transactions")
            farmer_tx = merged_df[merged_df['FarmerID'] == farmer_id_input]
            if not farmer_tx.empty:
                display_cols = ['Date', 'DealerID', 'Fertilizer_Type', 'Quantity_KG']
                available_cols = [col for col in display_cols if col in farmer_tx.columns]
                
                if available_cols:
                    st.dataframe(
                        farmer_tx[available_cols].sort_values('Date', ascending=False).head(10),
                        use_container_width=True
                    )
            else:
                st.info("No transactions found for this farmer")

if fraud_results is not None:
    st.markdown("---")
    st.header("🕵️ Fraud Detection Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        benami_count = len(fraud_results['benami_farmers'])
        st.metric("Benami Farmers Detected", benami_count)
    
    with col2:
        overclaim_count = len(fraud_results['overclaim_farmers'])
        st.metric("Over-claiming Farmers", overclaim_count)
    
    with col3:
        suspicious_count = len(fraud_results['suspicious_dealers'])
        st.metric("Suspicious Dealers", suspicious_count)
    
    tab1, tab2, tab3 = st.tabs(["📊 Global Overview", "🏢 Dealer Analytics", "👨‍🌾 Farmer Insights"])
    
    with tab1:
        st.subheader("Global Distribution Analysis")
        
        if using_sample_data:
            st.info("📊 Sample Data Analysis View")
        
        if not merged_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                if 'District' in merged_df.columns:
                    district_vol = merged_df.groupby('District')['Quantity_KG'].sum().reset_index()
                    fig = px.bar(district_vol, x='District', y='Quantity_KG',
                                title='Fertilizer Distribution by District',
                                color='Quantity_KG',
                                color_continuous_scale='Greens')
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'Fertilizer_Type' in merged_df.columns:
                    fert_dist = merged_df['Fertilizer_Type'].value_counts().reset_index()
                    fig = px.pie(fert_dist, values='count', names='Fertilizer_Type',
                                title='Fertilizer Type Distribution',
                                hole=0.3)
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Dealer Performance Analysis")
        
        if using_sample_data:
            st.info("🏢 Sample Dealer Data Analysis")
        
        if 'DealerID' in merged_df.columns:
            dealer_stats = merged_df.groupby('DealerID').agg({
                'Quantity_KG': 'sum',
                'FarmerID': 'nunique',
                'TransID': 'count'
            }).reset_index()
            
            dealer_stats.columns = ['DealerID', 'Total_Volume', 'Unique_Farmers', 'Total_Transactions']
            
            fig = px.scatter(dealer_stats, x='Total_Volume', y='Unique_Farmers',
                            size='Total_Transactions', color='DealerID',
                            title='Dealer Performance: Volume vs Farmers Served',
                            hover_data=['DealerID', 'Total_Volume', 'Unique_Farmers'])
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Farmer Insights")
        
        if using_sample_data:
            st.info("👨‍🌾 Sample Farmer Data Analysis")
        
        if not merged_df.empty and 'LandSize_Hectares' in merged_df.columns:
            fig = px.scatter(merged_df, x='LandSize_Hectares', y='Quantity_KG',
                            color='PrimaryCrop' if 'PrimaryCrop' in merged_df.columns else None,
                            size='Quantity_KG',
                            hover_data=['FarmerID', 'Name'],
                            title='Land Size vs Fertilizer Claimed',
                            labels={'LandSize_Hectares': 'Land Size (Ha)', 'Quantity_KG': 'Quantity Claimed (KG)'})
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
if using_sample_data:
    st.info("ℹ️ **Demo Mode:** Currently using built-in sample data. Upload your own files in the sidebar for real analysis.")
st.caption("🌾 AgriGuard Prototype v2.1 | Trust Verification & Fraud Detection | Secure GovTech Layer")
