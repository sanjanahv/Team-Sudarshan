# ultra_fast_kiosk.py
import streamlit as st
import pandas as pd
import pickle
from datetime import datetime

st.set_page_config(page_title="Ultra Fast Kiosk", layout="centered")

# 🚀 ULTRA FAST: Load index first
@st.cache_resource
def load_index():
    try:
        with open('data_index.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

# Load index (instant)
index = load_index()

st.title("⚡ Ultra Fast Farmer Kiosk")

if index:
    st.success(f"✅ Pre-loaded: {len(index['farmer_ids']):,} farmers indexed")
    
    # Super fast form
    farmer_id = st.text_input("Enter Farmer ID:")
    
    if farmer_id:
        # 🚀 INSTANT CHECK: O(1) lookup
        if farmer_id in index['farmer_ids']:
            st.success("✅ VERIFIED - Farmer exists")
            
            # Generate receipt
            receipt = f"""
FARMER VERIFIED
===============
ID: {farmer_id}
Time: {datetime.now().strftime("%H:%M:%S")}
Status: ✅ CONFIRMED
===============
"""
            st.code(receipt)
            
            if st.button("Download Receipt"):
                st.download_button(
                    "📥 Download",
                    receipt,
                    f"receipt_{farmer_id}.txt"
                )
        else:
            st.error("❌ NOT FOUND")
            st.button("🚨 Flag for Risk")
else:
    st.info("No pre-loaded data. Run load_data.py first")

st.caption("Instant verification • Sub-second response")
