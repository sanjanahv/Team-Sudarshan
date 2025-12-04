# fast_kiosk.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Farmer Kiosk", layout="centered")

# Title
st.title("🌾 Farmer Verification Kiosk")
st.markdown("---")

# Session state - simpler
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.df = None
    st.session_state.file_name = None

# File upload section
st.subheader("📁 Upload Database")

uploaded_file = st.file_uploader(
    "Choose Excel file", 
    type=['xlsx', 'xls'],
    help="Upload your farmer database"
)

if uploaded_file and not st.session_state.data_loaded:
    try:
        # Show loading
        with st.spinner(f"Loading {uploaded_file.name}..."):
            # Simple load
            st.session_state.df = pd.read_excel(uploaded_file)
            st.session_state.data_loaded = True
            st.session_state.file_name = uploaded_file.name
            
            st.success(f"✅ Loaded {len(st.session_state.df):,} records")
            
            # Quick preview
            if len(st.session_state.df) > 0:
                st.write("**Preview:**")
                st.dataframe(st.session_state.df.head(3), use_container_width=True)
                
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# If data loaded, show verification form
if st.session_state.data_loaded and st.session_state.df is not None:
    df = st.session_state.df
    
    st.markdown("---")
    st.subheader("🔍 Verify Farmer")
    
    # Find key columns
    col_names = df.columns.tolist()
    col_names_lower = [str(c).lower() for c in col_names]
    
    # Find farmer ID column
    farmer_id_col = None
    for i, name in enumerate(col_names_lower):
        if 'farmer' in name and ('id' in name or 'no' in name):
            farmer_id_col = col_names[i]
            break
        elif 'id' in name:
            farmer_id_col = col_names[i]
            break
    
    # Find village column
    village_col = None
    for i, name in enumerate(col_names_lower):
        if 'village' in name or 'gram' in name or 'town' in name:
            village_col = col_names[i]
            break
    
    # Find crop column
    crop_col = None
    for i, name in enumerate(col_names_lower):
        if 'crop' in name:
            crop_col = col_names[i]
            break
    
    # SIMPLE FORM
    with st.form("verify_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            farmer_id = st.text_input("Farmer ID/Number", placeholder="Enter ID")
            
            if village_col:
                villages = df[village_col].dropna().unique().tolist()[:50]
                if villages:
                    village = st.selectbox("Village", [""] + villages)
                else:
                    village = st.text_input("Village")
            else:
                village = st.text_input("Village")
        
        with col2:
            if crop_col:
                crops = df[crop_col].dropna().unique().tolist()[:30]
                if crops:
                    crop = st.selectbox("Crop", [""] + crops)
                else:
                    crop = st.text_input("Crop")
            else:
                crop = st.text_input("Crop")
            
            land = st.number_input("Land (acres/ha)", min_value=0.0, value=1.0, step=0.1)
        
        submitted = st.form_submit_button("✅ Check Verification")
    
    # Check verification
    if submitted:
        st.markdown("---")
        
        found = False
        match_data = {}
        
        # Check by Farmer ID
        if farmer_id and farmer_id_col:
            try:
                # Convert to string for comparison
                matches = df[df[farmer_id_col].astype(str).str.contains(str(farmer_id), na=False)]
                if not matches.empty:
                    found = True
                    match_data = matches.iloc[0].to_dict()
            except:
                pass
        
        # Check by Village + Crop
        if not found and village and crop and village_col and crop_col:
            try:
                village_matches = df[df[village_col].astype(str).str.contains(village, case=False, na=False)]
                if not village_matches.empty:
                    crop_matches = village_matches[village_matches[crop_col].astype(str).str.contains(crop, case=False, na=False)]
                    if not crop_matches.empty:
                        found = True
                        match_data = crop_matches.iloc[0].to_dict()
            except:
                pass
        
        # Show result
        if found:
            st.success("✅ **FARMER VERIFIED**")
            
            # Show details
            with st.expander("📋 Details"):
                for key, value in match_data.items():
                    if pd.notna(value):
                        st.write(f"**{key}:** {value}")
            
            # Receipt button
            if st.button("🧾 Generate Receipt", type="primary"):
                receipt = create_receipt(farmer_id, village, crop, match_data)
                st.code(receipt)
                
                # Download
                st.download_button(
                    "📥 Download Receipt",
                    receipt,
                    f"receipt_{farmer_id}.txt"
                )
        
        else:
            st.error("❌ **NOT FOUND**")
            
            # Risk dashboard option
            st.warning("This case will be sent to risk dashboard for investigation.")
            
            if st.button("🚨 Create Risk Case"):
                risk_data = {
                    'farmer_id': farmer_id,
                    'village': village,
                    'crop': crop,
                    'timestamp': datetime.now().isoformat(),
                    'database': st.session_state.file_name
                }
                
                # Save simple text file
                with open('risk_case.txt', 'w') as f:
                    f.write(f"Risk Case - {datetime.now()}\n")
                    f.write(f"Farmer ID: {farmer_id}\n")
                    f.write(f"Village: {village}\n")
                    f.write(f"Crop: {crop}\n")
                    f.write(f"Status: Needs investigation\n")
                
                st.info("✅ Risk case saved as 'risk_case.txt'")
                st.write("Send this file to risk dashboard.")

# Function to create receipt
def create_receipt(farmer_id, village, crop, match_data):
    receipt_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    receipt = f"""
=========================================
       FARMER VERIFICATION RECEIPT
=========================================
Receipt No: VER-{datetime.now().strftime('%Y%m%d%H%M%S')}
Date: {receipt_date}

VERIFICATION: ✅ CONFIRMED

Farmer Details:
---------------
Farmer ID: {farmer_id}
Village: {village}
Crop: {crop}

Database Match:
--------------"""
    
    # Add first 5 match details
    count = 0
    for key, value in match_data.items():
        if pd.notna(value) and count < 5:
            receipt += f"\n{key}: {value}"
            count += 1
    
    receipt += f"""

Status: Eligible for subsidy schemes
Next Step: Proceed to subsidy distribution
=========================================
"""
    return receipt

# Footer
st.markdown("---")
st.caption("⚡ Fast Kiosk • Upload Excel → Verify → Get Receipt")
