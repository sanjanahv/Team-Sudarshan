# farmer_kiosk_final.py
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Farmer Kiosk", layout="centered")

# Title
st.title("🌾 Farmer Verification Kiosk")
st.markdown("---")

# ==================== YOUR HARDCODED DATABASE ====================
FARMERS_DB = [
    {"farmer_id": "FAR000001", "village": "Neelkamal", "land_size_ha": 0.93, "crop_type": "Onion", "irrigation_type": "Rainfed", "soil_type": "Clay", "last_subsidy_date": "01-01-2024", "farm_category": "Medium (2-5ha)"},
    {"farmer_id": "FAR000002", "village": "Uttara Phalguni", "land_size_ha": 5.43, "crop_type": "Bajra", "irrigation_type": "Borewell", "soil_type": "Red", "last_subsidy_date": "01-01-2024", "farm_category": "Large (>5ha)"},
    {"farmer_id": "FAR000003", "village": "Anjaneya Layout", "land_size_ha": 3.73, "crop_type": "Ragi", "irrigation_type": "Flood", "soil_type": "Clay", "last_subsidy_date": "01-01-2024", "farm_category": "Medium (2-5ha)"},
    {"farmer_id": "FAR000004", "village": "Hanumantha Nagar", "land_size_ha": 3.32, "crop_type": "Paddy", "irrigation_type": "Rainfed", "soil_type": "Black Clay", "last_subsidy_date": "01-01-2024", "farm_category": "Medium (2-5ha)"},
    {"farmer_id": "FAR000005", "village": "Gokul Vihar", "land_size_ha": 3.99, "crop_type": "Tur/Arhar", "irrigation_type": "Rainfed", "soil_type": "Sandy", "last_subsidy_date": "01-01-2024", "farm_category": "Medium (2-5ha)"},
    {"farmer_id": "FAR000006", "village": "Pushpagiri", "land_size_ha": 0.78, "crop_type": "Jowar", "irrigation_type": "Flood", "soil_type": "Clay", "last_subsidy_date": "01-01-2024", "farm_category": "SC/ST"},
    {"farmer_id": "FAR000007", "village": "Neelkamal", "land_size_ha": 5.46, "crop_type": "Green Gram", "irrigation_type": "Flood", "soil_type": "Loamy", "last_subsidy_date": "01-01-2024", "farm_category": "Marginal"},
    {"farmer_id": "FAR000008", "village": "Dakshina Mukhi", "land_size_ha": 0.37, "crop_type": "Cotton", "irrigation_type": "Borewell", "soil_type": "Black (Regur)", "last_subsidy_date": "01-01-2024", "farm_category": "SC/ST"},
    {"farmer_id": "FAR000009", "village": "Skanda Giri", "land_size_ha": 1.02, "crop_type": "Ragi", "irrigation_type": "Rainfed", "soil_type": "Clay", "last_subsidy_date": "01-01-2024", "farm_category": "Small (<2ha)"},
    {"farmer_id": "FAR000010", "village": "Hanumantha Nagar", "land_size_ha": 2.21, "crop_type": "Potato", "irrigation_type": "Borewell", "soil_type": "Loamy", "last_subsidy_date": "01-01-2024", "farm_category": "Small (<2ha)"},
    {"farmer_id": "FAR000011", "village": "Hanumantha Nagar", "land_size_ha": 0.27, "crop_type": "Chilli", "irrigation_type": "Rainfed", "soil_type": "Clay", "last_subsidy_date": "01-01-2024", "farm_category": "SC/ST"},
    {"farmer_id": "FAR000012", "village": "Bhoga Nandeeshwara", "land_size_ha": 3.27, "crop_type": "Onion", "irrigation_type": "Borewell", "soil_type": "Clay", "last_subsidy_date": "01-01-2024", "farm_category": "Small (<2ha)"},
    {"farmer_id": "FAR000013", "village": "Pushpagiri", "land_size_ha": 1.22, "crop_type": "Okra", "irrigation_type": "Borewell", "soil_type": "Black (Regur)", "last_subsidy_date": "01-01-2024", "farm_category": "SC/ST"},
    {"farmer_id": "FAR000014", "village": "RedSoil Hamlet", "land_size_ha": 3.84, "crop_type": "Jowar", "irrigation_type": "Borewell", "soil_type": "Loamy", "last_subsidy_date": "01-01-2024", "farm_category": "Large (>5ha)"},
    {"farmer_id": "FAR000015", "village": "Gokul Vihar", "land_size_ha": 1.7, "crop_type": "Green Gram", "irrigation_type": "Sprinkler", "soil_type": "Alluvial", "last_subsidy_date": "01-01-2024", "farm_category": "Large (>5ha)"},
    {"farmer_id": "FAR000016", "village": "Bhoga Nandeeshwara", "land_size_ha": 0.5, "crop_type": "Sunflower", "irrigation_type": "Sprinkler", "soil_type": "Clay", "last_subsidy_date": "02-01-2024", "farm_category": "Small (<2ha)"},
    {"farmer_id": "FAR000017", "village": "GreenVillage", "land_size_ha": 3.32, "crop_type": "Maize", "irrigation_type": "Drip", "soil_type": "Red", "last_subsidy_date": "02-01-2024", "farm_category": "Small (<2ha)"},
    {"farmer_id": "FAR000018", "village": "Nandi Hills", "land_size_ha": 0.73, "crop_type": "Paddy", "irrigation_type": "Rainfed", "soil_type": "Laterite", "last_subsidy_date": "02-01-2024", "farm_category": "SC/ST"},
    {"farmer_id": "FAR000019", "village": "Pushpagiri", "land_size_ha": 1.69, "crop_type": "Cowpea", "irrigation_type": "Rainfed", "soil_type": "Red", "last_subsidy_date": "02-01-2024", "farm_category": "Medium (2-5ha)"},
    {"farmer_id": "FAR000020", "village": "Keshavpur", "land_size_ha": 0.2, "crop_type": "Paddy", "irrigation_type": "Rainfed", "soil_type": "Laterite", "last_subsidy_date": "02-01-2024", "farm_category": "Small (<2ha)"},
]

# Get unique values for dropdowns
villages = sorted(set([f["village"] for f in FARMERS_DB]))
crops = sorted(set([f["crop_type"] for f in FARMERS_DB]))
soils = sorted(set([f["soil_type"] for f in FARMERS_DB]))
irrigation_types = sorted(set([f["irrigation_type"] for f in FARMERS_DB]))
farm_categories = sorted(set([f["farm_category"] for f in FARMERS_DB]))

# Show database info
st.info(f"**Database loaded:** {len(FARMERS_DB)} farmers from {len(villages)} villages")

# ==================== VERIFICATION FORM ====================
st.markdown("---")
st.subheader("🔍 Verify Farmer")

# Simple form
farmer_id = st.text_input("Farmer ID (e.g., FAR000001):", placeholder="Enter Farmer ID")
village = st.selectbox("Village:", [""] + villages)
crop_type = st.selectbox("Crop Type:", [""] + crops)
soil_type = st.selectbox("Soil Type:", [""] + soils)
irrigation_type = st.selectbox("Irrigation Type:", [""] + irrigation_types)

if st.button("✅ Check Verification", type="primary"):
    st.markdown("---")
    
    # Search for farmer
    found_farmers = []
    
    for farmer in FARMERS_DB:
        match = True
        
        # Check each field if provided
        if farmer_id and farmer["farmer_id"].lower() != farmer_id.lower().strip():
            match = False
        if village and farmer["village"].lower() != village.lower().strip():
            match = False
        if crop_type and farmer["crop_type"].lower() != crop_type.lower().strip():
            match = False
        if soil_type and farmer["soil_type"].lower() != soil_type.lower().strip():
            match = False
        if irrigation_type and farmer["irrigation_type"].lower() != irrigation_type.lower().strip():
            match = False
        
        if match:
            found_farmers.append(farmer)
    
    # Show results
    if found_farmers:
        farmer = found_farmers[0]  # Take first match
        
        st.success("✅ **FARMER VERIFIED**")
        st.balloons()
        
        # Display farmer details
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("**📋 Government Record:**")
            st.write(f"**Farmer ID:** {farmer['farmer_id']}")
            st.write(f"**Village:** {farmer['village']}")
            st.write(f"**Land Size:** {farmer['land_size_ha']} ha")
            st.write(f"**Crop:** {farmer['crop_type']}")
            st.write(f"**Soil:** {farmer['soil_type']}")
        
        with col2:
            st.info("**📝 Your Input:**")
            st.write(f"**Farmer ID:** {farmer_id}")
            st.write(f"**Village:** {village}")
            st.write(f"**Crop:** {crop_type}")
            st.write(f"**Soil:** {soil_type}")
            st.write(f"**Irrigation:** {irrigation_type}")
        
        # Additional details
        with st.expander("📊 More Details"):
            st.write(f"**Irrigation Type:** {farmer['irrigation_type']}")
            st.write(f"**Last Subsidy Date:** {farmer['last_subsidy_date']}")
            st.write(f"**Farm Category:** {farmer['farm_category']}")
            st.write(f"**Farmer Count:** {len(found_farmers)} match(es)")
        
        # Generate receipt
        st.markdown("---")
        st.subheader("🧾 Generate Receipt")
        
        if st.button("📄 Generate Receipt", key="gen_receipt"):
            receipt = generate_receipt(farmer, farmer_id, village, crop_type)
            
            # Display receipt
            st.code(receipt)
            
            # Download button
            st.download_button(
                label="📥 Download Receipt",
                data=receipt,
                file_name=f"receipt_{farmer['farmer_id']}.txt",
                mime="text/plain"
            )
    
    else:
        st.error("❌ **FARMER NOT FOUND**")
        
        st.warning("""
        This farmer is not registered in the government database.
        
        **Possible reasons:**
        1. Farmer ID incorrect
        2. Village name doesn't match
        3. Crop type doesn't match
        4. Data entry error
        """)
        
        # Show what we have in database
        with st.expander("📋 View All Farmers in Database"):
            for f in FARMERS_DB:
                st.write(f"{f['farmer_id']} - {f['village']} - {f['crop_type']}")

# ==================== FUNCTION TO GENERATE RECEIPT ====================
def generate_receipt(farmer, input_id, input_village, input_crop):
    receipt_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    receipt = f"""
========================================================================
                 GOVERNMENT OF INDIA
            FARMER SUBSIDY VERIFICATION RECEIPT
========================================================================
Receipt No: SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}
Date: {receipt_date}
Verified By: Automated Kiosk System

========================================================================
                       VERIFICATION RESULT
                          ✅ VERIFIED
========================================================================

FARMER DETAILS:
---------------
• Farmer ID:       {farmer['farmer_id']}
• Village:         {farmer['village']}
• Land Size:       {farmer['land_size_ha']} hectares
• Crop Type:       {farmer['crop_type']}
• Soil Type:       {farmer['soil_type']}
• Irrigation:      {farmer['irrigation_type']}
• Farm Category:   {farmer['farm_category']}

SUBSIDY INFORMATION:
--------------------
• Last Subsidy:    {farmer['last_subsidy_date']}
• Eligible For:    Fertilizer, Seeds, Equipment
• Next Subsidy:    Within next 30 days
• Amount:          ₹5,000 - ₹15,000 (based on category)

VERIFICATION DETAILS:
---------------------
• Input Farmer ID: {input_id}
• Input Village:   {input_village}
• Input Crop:      {input_crop}
• Verification:    Automated database match
• Confidence:      High (Exact match found)

========================================================================
                  IMPORTANT INFORMATION
• Present this receipt at nearest agriculture office
• Subsidy will be transferred to registered bank account
• Keep this receipt for future reference
• For queries: 1800-XXX-XXXX

========================================================================
               SYSTEM GENERATED - VALID WITHOUT SIGNATURE
========================================================================
"""
    return receipt

# ==================== DATABASE VIEWER ====================
st.markdown("---")
with st.expander("📊 View Complete Database"):
    for farmer in FARMERS_DB:
        st.write(f"**{farmer['farmer_id']}** - {farmer['village']} - {farmer['crop_type']} ({farmer['land_size_ha']} ha)")

# ==================== STATISTICS ====================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Farmers", len(FARMERS_DB))
with col2:
    st.metric("Villages", len(villages))
with col3:
    st.metric("Crop Types", len(crops))

# Footer
st.markdown("---")
st.caption("🌾 Government Farmer Verification System • Pre-loaded database • Instant verification")
