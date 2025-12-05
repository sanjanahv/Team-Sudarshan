# app.py

import streamlit as st
from risk_engine import evaluate_risk

st.set_page_config(page_title="Farmer Kiosk", layout="centered")

st.title("🌾 Farmer Verification & Risk Kiosk")
st.markdown("---")

st.subheader("🔍 Enter Farmer & Dealer Details")

with st.form("verify_form"):
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        farmer_id_input = st.text_input("Farmer ID*", placeholder="Enter exact farmer ID")
        dealer_id_input = st.text_input("Dealer ID*", placeholder="Enter dealer ID")
        village_input = st.text_input("Village*", placeholder="Enter village name")
    
    with col2:
        # 🔽 DROPDOWN FOR CROP TYPE
        crop_input = st.selectbox(
            "Crop Type*",
            ["", "Jowar", "Rice", "Wheat", "Oats", "Paddy"],
            index=0
        )

        # 🔽 DROPDOWN FOR SOIL TYPE
        soil_type_input = st.selectbox(
            "Soil Type*",
            ["", "Alluvial", "Clay", "Loamy", "Red", "Black (Regur)", "Sandy Loam"],
            index=0
        )

        land_input = st.number_input("Land Size (acres)", min_value=0.0, value=1.0, step=0.1)

    submitted = st.form_submit_button("Evaluate Risk")

if submitted:
    fid = farmer_id_input.strip()
    did = dealer_id_input.strip()
    vil = village_input.strip()
    cr = crop_input.strip()
    soil = soil_type_input.strip()

    if fid == "" or did == "" or vil == "" or cr == "" or soil == "":
        st.error("Please fill all required fields.")
    else:
        # Build input packet for backend
        input_farmer = {
            "farmer_id": fid,
            "Dealer_ID": did,
            "village": vil,
            "land_size": land_input,
            "Crop": cr,  # using dropdown exact text
            "Soil_Type": soil
        }

        result = evaluate_risk(input_farmer)

        st.markdown("---")
        st.subheader("🧠 Risk Evaluation Result")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Decision", result["Decision"])
        with col2:
            st.metric("Risk Score", result["Risk_Score"])

        if "Soil_Type" in input_farmer:
            st.info(f"**Soil Type:** {input_farmer['Soil_Type']}")

        if result.get("Expected_Fertilizer_kg") is not None:
            col3, col4 = st.columns(2)
            with col3:
                st.metric("Expected Fertilizer (kg)", result["Expected_Fertilizer_kg"])
            with col4:
                st.metric("Claimed Fertilizer (kg)", result["Claimed_Fertilizer_kg"])

        st.markdown("### 📝 Reasons")
        st.write(result["Reasons"] or "No specific issues detected.")

        with st.expander("📋 View All Input Parameters"):
            params_table = {
                "Parameter": ["Farmer ID", "Dealer ID", "Village", "Crop", "Soil Type", "Land Size"],
                "Value": [fid, did, vil, cr, soil, f"{land_input} acres"]
            }
            st.table(params_table)

        st.markdown("### 📝 Reasons")
        st.write(result["Reasons"] or "No specific issues detected.")

