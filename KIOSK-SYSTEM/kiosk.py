import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Farmer Kiosk", layout="centered")

st.title("🌾 Farmer Verification Kiosk")
st.markdown("---")

# Session State
if "df" not in st.session_state:
    st.session_state.df = None

# ------------------------- FILE UPLOAD -------------------------
st.subheader("📁 Upload Farmer Database")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.session_state.df = df
        st.success(f"Loaded {len(df):,} records.")

        with st.expander("📊 Preview (first 5 rows)"):
            st.dataframe(df.head())

    except Exception as e:
        st.error("❌ Unable to read file: " + str(e))

# ------------------------- VERIFICATION FORM -------------------------
if st.session_state.df is not None:
    df = st.session_state.df

    st.markdown("---")
    st.subheader("🔍 Verify Farmer")

    st.info(f"Available Columns: {', '.join(df.columns.tolist())}")

    # Column mapping
    with st.expander("⚙️ Column Mapping"):
        farmer_id_col = st.selectbox("Farmer ID Column", df.columns.tolist())
        village_col = st.selectbox("Village Column", df.columns.tolist())
        crop_col = st.selectbox("Crop Column", df.columns.tolist())

    # ---------------- FORM ----------------
    with st.form("verify_form"):
        farmer_id_input = st.text_input("Farmer ID*", placeholder="Enter exact ID")
        village_input = st.text_input("Village*", placeholder="Enter village name")
        crop_input = st.text_input("Crop Type*", placeholder="Enter crop name")

        land_input = st.number_input("Land Size", min_value=0.0, value=1.0, step=0.1)

        submitted = st.form_submit_button("Check Verification")

    if submitted:
        # Clean input
        fid = farmer_id_input.strip()
        vil = village_input.strip().lower()
        cr = crop_input.strip().lower()

        if fid == "" or vil == "" or cr == "":
            st.error("Please fill all required fields.")
            st.stop()

        # ---------------- SEARCH LOGIC ----------------
        df["fid_clean"] = df[farmer_id_col].astype(str).str.strip()
        df["vil_clean"] = df[village_col].astype(str).str.strip().str.lower()
        df["crop_clean"] = df[crop_col].astype(str).str.strip().str.lower()

        # Find ID
        id_match = df[df["fid_clean"] == fid]

        if id_match.empty:
            st.error("❌ THREAT: Farmer ID not found in database.")
        else:
            row = id_match.iloc[0]

            village_match = (row["vil_clean"] == vil)
            crop_match = (row["crop_clean"] == cr)

            if village_match and crop_match:
                st.success("✅ SUCCESSFUL — Exact Match Verified!")

                with st.expander("Verified Record"):
                    st.write(row)

            else:
                st.error("🚨 THREAT — Farmer found but details do NOT match.")
                if not village_match:
                    st.warning(f"Village mismatch: DB has '{row[village_col]}'")
                if not crop_match:
                    st.warning(f"Crop mismatch: DB has '{row[crop_col]}'")

