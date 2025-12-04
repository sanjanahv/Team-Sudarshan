# simple_kiosk_fixed_upload.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Farmer Kiosk", layout="centered")

# Title
st.title("🌾 Farmer Verification Kiosk")
st.markdown("---")

# Session state for Excel file
if 'excel_file_path' not in st.session_state:
    st.session_state.excel_file_path = None
if 'gov_df' not in st.session_state:
    st.session_state.gov_df = pd.DataFrame()

# File upload section
st.subheader("📁 Upload Government Database")

uploaded_file = st.file_uploader(
    "Choose an Excel file", 
    type=['xlsx', 'xls', 'xlsm', 'xlsb'],  # All Excel types
    help="Upload your farmer database Excel file (.xlsx, .xls, .xlsm, .xlsb)"
)

if uploaded_file is not None:
    try:
        # Get file details
        file_name = uploaded_file.name
        file_size = uploaded_file.size / 1024  # Convert to KB
        file_type = uploaded_file.type
        
        st.info(f"""
        📄 **File Details:**
        - Name: `{file_name}`
        - Size: `{file_size:.2f} KB`
        - Type: `{file_type}`
        """)
        
        # Save uploaded file temporarily
        temp_path = f"temp_{file_name}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Try different Excel reading methods
        try:
            # Try with openpyxl engine first
            st.session_state.gov_df = pd.read_excel(temp_path, engine='openpyxl')
        except:
            try:
                # Try with xlrd engine for .xls files
                st.session_state.gov_df = pd.read_excel(temp_path, engine='xlrd')
            except:
                try:
                    # Try without specifying engine
                    st.session_state.gov_df = pd.read_excel(temp_path)
                except Exception as e:
                    st.error(f"❌ Cannot read Excel file: {str(e)}")
                    st.session_state.gov_df = pd.DataFrame()
        
        if not st.session_state.gov_df.empty:
            st.session_state.excel_file_path = temp_path
            
            st.success(f"✅ File loaded successfully: {file_name}")
            st.write(f"📊 Total records: {len(st.session_state.gov_df)}")
            
            # Show preview
            with st.expander("👁️ Preview Data (First 5 rows)"):
                st.dataframe(st.session_state.gov_df.head(), use_container_width=True)
            
            # Show column info
            with st.expander("📋 Column Information"):
                st.write("**Columns in your file:**")
                col_info = []
                for col in st.session_state.gov_df.columns:
                    non_null = st.session_state.gov_df[col].notna().sum()
                    data_type = str(st.session_state.gov_df[col].dtype)
                    col_info.append({
                        'Column': col,
                        'Non-Null': non_null,
                        'Type': data_type,
                        'Sample': str(st.session_state.gov_df[col].iloc[0]) if non_null > 0 else 'N/A'
                    })
                
                col_df = pd.DataFrame(col_info)
                st.dataframe(col_df, use_container_width=True)
                
                # Check for required columns (case-insensitive)
                df_cols_lower = [str(col).lower() for col in st.session_state.gov_df.columns]
                
                # Common column name variations
                possible_farmer_id = ['farmer_id', 'farmerid', 'id', 'farmer id', 'farmer no']
                possible_village = ['village', 'village_name', 'village name', 'gram', 'town']
                possible_crop = ['crop_type', 'crop', 'cropname', 'crop name', 'crop_type']
                
                found_farmer_id = any(col in df_cols_lower for col in possible_farmer_id)
                found_village = any(col in df_cols_lower for col in possible_village)
                found_crop = any(col in df_cols_lower for col in possible_crop)
                
                st.write("**Column Detection:**")
                if found_farmer_id:
                    st.success("✅ Farmer ID column detected")
                else:
                    st.warning("⚠️ Farmer ID column not found (looking for: farmer_id, id, farmerid)")
                
                if found_village:
                    st.success("✅ Village column detected")
                else:
                    st.warning("⚠️ Village column not found (looking for: village, village_name)")
                
                if found_crop:
                    st.success("✅ Crop column detected")
                else:
                    st.warning("⚠️ Crop column not found (looking for: crop_type, crop)")
            
            # Show statistics
            with st.expander("📈 Data Statistics"):
                if 'farmer_id' in st.session_state.gov_df.columns:
                    st.write(f"**Unique Farmers:** {st.session_state.gov_df['farmer_id'].nunique()}")
                
                if 'village' in st.session_state.gov_df.columns:
                    st.write(f"**Unique Villages:** {st.session_state.gov_df['village'].nunique()}")
                    top_villages = st.session_state.gov_df['village'].value_counts().head(5)
                    st.write("**Top 5 Villages:**")
                    st.write(top_villages)
                
                if 'crop_type' in st.session_state.gov_df.columns:
                    st.write(f"**Crop Types:** {st.session_state.gov_df['crop_type'].nunique()}")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")
        st.info("""
        **Tips:**
        1. Make sure it's a valid Excel file
        2. Check if file is not corrupted
        3. Try saving as .xlsx format
        4. Make sure file is not password protected
        """)
else:
    # Try to load default file
    try:
        # Check for any Excel file in directory
        excel_files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls', '.xlsm', '.xlsb'))]
        
        if excel_files:
            default_file = excel_files[0]  # Use first Excel file found
            st.session_state.gov_df = pd.read_excel(default_file)
            st.session_state.excel_file_path = default_file
            st.info(f"📂 Auto-loaded: `{default_file}`")
        else:
            st.warning("⚠️ No Excel file found. Please upload a file.")
    except Exception as e:
        st.warning(f"⚠️ Could not auto-load files: {str(e)}")

# Only show verification form if data is loaded
if not st.session_state.gov_df.empty:
    st.markdown("---")
    
    # Helper function to find column (case-insensitive)
    def find_column(df, possible_names):
        df_cols_lower = [str(col).lower() for col in df.columns]
        for name in possible_names:
            if name in df_cols_lower:
                # Get actual column name
                idx = df_cols_lower.index(name)
                return df.columns[idx]
        return None
    
    # Find actual column names
    farmer_id_col = find_column(st.session_state.gov_df, ['farmer_id', 'farmerid', 'id', 'farmer id', 'farmer no'])
    village_col = find_column(st.session_state.gov_df, ['village', 'village_name', 'village name', 'gram', 'town'])
    crop_col = find_column(st.session_state.gov_df, ['crop_type', 'crop', 'cropname', 'crop name'])
    land_col = find_column(st.session_state.gov_df, ['land_size_ha', 'land_size', 'land', 'area', 'area_ha'])
    soil_col = find_column(st.session_state.gov_df, ['soil_type', 'soil', 'soiltype'])
    irrigation_col = find_column(st.session_state.gov_df, ['irrigation_type', 'irrigation', 'irrigationtype'])
    
    # Get unique values for dropdowns
    try:
        if crop_col:
            crops = sorted(st.session_state.gov_df[crop_col].dropna().astype(str).unique().tolist())
        else:
            crops = ["Wheat", "Rice", "Cotton", "Sugarcane", "Vegetables"]
    except:
        crops = ["Wheat", "Rice", "Cotton", "Sugarcane", "Vegetables"]
    
    try:
        if soil_col:
            soils = sorted(st.session_state.gov_df[soil_col].dropna().astype(str).unique().tolist())
        else:
            soils = ["Black Soil", "Red Soil", "Alluvial", "Laterite"]
    except:
        soils = ["Black Soil", "Red Soil", "Alluvial", "Laterite"]
    
    try:
        if village_col:
            villages = sorted(st.session_state.gov_df[village_col].dropna().astype(str).unique().tolist())
        else:
            villages = []
    except:
        villages = []
    
    # Input Form
    st.subheader("🔍 Enter Farmer Details")
    
    with st.form("farmer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            farmer_id = st.number_input("Farmer ID", min_value=1, step=1, value=1001)
            
            # Village dropdown or input
            if villages:
                village = st.selectbox("Village", villages, help="Select your village")
            else:
                village = st.text_input("Village", placeholder="Enter village name")
            
            land_size = st.number_input("Land Size (hectares)", min_value=0.1, step=0.1, value=1.0)
        
        with col2:
            # Crop dropdown
            crop_type = st.selectbox("Crop Type", crops)
            
            # Irrigation dropdown
            irrigation = st.selectbox("Irrigation", ["Well", "Canal", "Drip", "Rainfed", "Other", "Not Specified"])
            
            # Soil type dropdown
            soil_type = st.selectbox("Soil Type", soils)
        
        submitted = st.form_submit_button("✅ Check Verification")
    
    # Check if farmer exists
    if submitted:
        st.markdown("---")
        
        found = False
        match_details = None
        
        # Check by Farmer ID
        if farmer_id_col and int(farmer_id) in st.session_state.gov_df[farmer_id_col].values:
            match = st.session_state.gov_df[st.session_state.gov_df[farmer_id_col] == int(farmer_id)].iloc[0]
            found = True
            match_details = match
        
        # If not found by ID, check by village + crop
        elif not found and village and crop_type and village_col and crop_col:
            try:
                village_match = st.session_state.gov_df[village_col].astype(str).str.lower().str.contains(village.lower(), na=False)
                crop_match = st.session_state.gov_df[crop_col].astype(str).str.lower().str.contains(crop_type.lower(), na=False)
                
                matches = st.session_state.gov_df[village_match & crop_match]
                if not matches.empty:
                    found = True
                    match_details = matches.iloc[0]
            except Exception as e:
                st.warning(f"Could not perform village+crop search: {str(e)}")
        
        # Show result
        if found and match_details is not None:
            st.success("✅ **VERIFIED - Farmer exists in database**")
            
            # Show match details
            with st.expander("📋 Match Details"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Government Record:**")
                    if farmer_id_col:
                        st.write(f"**ID:** {match_details[farmer_id_col]}")
                    if village_col:
                        st.write(f"**Village:** {match_details[village_col]}")
                    if land_col:
                        st.write(f"**Land:** {match_details[land_col]} ha")
                    if crop_col:
                        st.write(f"**Crop:** {match_details[crop_col]}")
                    if soil_col:
                        st.write(f"**Soil:** {match_details[soil_col]}")
                    if irrigation_col:
                        st.write(f"**Irrigation:** {match_details[irrigation_col]}")
                
                with col2:
                    st.write("**Your Input:**")
                    st.write(f"**ID:** {farmer_id}")
                    st.write(f"**Village:** {village}")
                    st.write(f"**Land:** {land_size} ha")
                    st.write(f"**Crop:** {crop_type}")
                    st.write(f"**Soil:** {soil_type}")
                    st.write(f"**Irrigation:** {irrigation}")
            
            # Generate Receipt
            st.markdown("---")
            st.subheader("🧾 Generate Receipt")
            
            if st.button("📄 Generate Receipt"):
                receipt_date = datetime.now().strftime("%d-%b-%Y %I:%M %p")
                
                # Build receipt
                receipt_lines = [
                    "=" * 40,
                    "       GOVERNMENT SUBSIDY RECEIPT",
                    "=" * 40,
                    f"Receipt No: SUB-{datetime.now().strftime('%Y%m%d')}-{farmer_id}",
                    f"Date: {receipt_date}",
                    "",
                    "FARMER DETAILS:",
                    "-" * 20,
                ]
                
                # Add available details
                if farmer_id_col:
                    receipt_lines.append(f"Farmer ID: {match_details[farmer_id_col]}")
                receipt_lines.append(f"Village: {village}")
                receipt_lines.append(f"Land Size: {land_size} ha")
                receipt_lines.append(f"Crop Type: {crop_type}")
                receipt_lines.append(f"Soil Type: {soil_type}")
                receipt_lines.append(f"Irrigation: {irrigation}")
                
                receipt_lines.extend([
                    "",
                    "SUBSIDY STATUS:",
                    "-" * 20,
                    "Status: ✅ VERIFIED & ELIGIBLE",
                    "",
                    f"Verification Time: {receipt_date}",
                    f"Database: {st.session_state.excel_file_path}",
                    "System: Farmer Verification Kiosk",
                    "=" * 40
                ])
                
                receipt = "\n".join(receipt_lines)
                
                # Display receipt
                st.code(receipt)
                
                # Download button
                st.download_button(
                    label="📥 Download Receipt",
                    data=receipt,
                    file_name=f"receipt_{farmer_id}.txt",
                    mime="text/plain"
                )
        
        else:
            # Farmer NOT found - Redirect to Risk Dashboard
            st.error("❌ **FARMER NOT FOUND IN DATABASE**")
            
            st.warning("""
            This farmer is not registered in the government database.
            
            **Next Steps:**
            1. This case will be sent to Risk Assessment Dashboard
            2. Fraud detection team will investigate
            3. You'll be notified of the result
            """)
            
            # Button to simulate redirect to Risk Dashboard
            if st.button("🚨 Send to Risk Dashboard"):
                # Create risk case data
                risk_data = {
                    'farmer_id': farmer_id,
                    'village': village,
                    'crop_type': crop_type,
                    'land_size': land_size,
                    'soil_type': soil_type,
                    'irrigation': irrigation,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending_investigation',
                    'database_file': st.session_state.excel_file_path
                }
                
                # Save to JSON file
                import json
                with open('risk_case.json', 'w') as f:
                    json.dump(risk_data, f, indent=2)
                
                st.info(f"""
                **✅ Risk case created!**
                
                **Data sent for investigation:**
                - Farmer ID: {farmer_id}
                - Village: {village}
                - Crop: {crop_type}
                - Land: {land_size} ha
                - Soil: {soil_type}
                - Irrigation: {irrigation}
                
                **File saved:** `risk_case.json`
                
                Your friend's risk dashboard can read this file.
                """)

# Footer
st.markdown("---")
st.caption("Farmer Verification System • Kiosk Module")
st.caption("Supports: .xlsx, .xls, .xlsm, .xlsb files")
