# app.py

import streamlit as st
from risk_engine import evaluate_risk

st.set_page_config(page_title="Farmer Kiosk", layout="centered")

st.title("🌾 Farmer Verification & Risk Kiosk")
st.markdown("---")

st.subheader("🔍 Enter Farmer & Dealer Details")

with st.form("verify_form"):
    farmer_id_input = st.text_input("Farmer ID*", placeholder="Enter exact farmer ID")
    dealer_id_input = st.text_input("Dealer ID*", placeholder="Enter dealer ID")
    village_input = st.text_input("Village*", placeholder="Enter village name")
    crop_input = st.text_input("Crop Type*", placeholder="Enter crop name (e.g. Rice)")
    land_input = st.number_input("Land Size (acres)", min_value=0.0, value=1.0, step=0.1)

    submitted = st.form_submit_button("Evaluate Risk")

if submitted:
    fid = farmer_id_input.strip()
    did = dealer_id_input.strip()
    vil = village_input.strip()
    cr = crop_input.strip()

    if fid == "" or did == "" or vil == "" or cr == "":
        st.error("Please fill all required fields.")
    else:
        # Build input packet for backend
        input_farmer = {
            "farmer_id": fid,
            "Dealer_ID": did,
            "village": vil,
            "land_size": land_input,
            "Crop": cr.capitalize()  # match "Rice", "Wheat", etc.
        }

        result = evaluate_risk(input_farmer)

        st.markdown("---")
        st.subheader("🧠 Risk Evaluation Result")

        st.metric("Decision", result["Decision"])
        st.metric("Risk Score", result["Risk_Score"])

        if result.get("Expected_Fertilizer_kg") is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Expected Fertilizer (kg)", result["Expected_Fertilizer_kg"])
            with col2:
                st.metric("Claimed Fertilizer (kg)", result["Claimed_Fertilizer_kg"])

        st.markdown("### 📝 Reasons")
        st.write(result["Reasons"] or "No specific issues detected.")
