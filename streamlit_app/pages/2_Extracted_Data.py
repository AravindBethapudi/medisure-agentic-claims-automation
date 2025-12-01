import streamlit as st
import os
import json
from utils.helpers import load_css
from utils.components import load_css, styled_success, styled_error

st.set_page_config(page_title="Extracted Data", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)


st.title("🧾 Extracted Claim Data")

# Check session state
if "CLAIM_RESULT" not in st.session_state or st.session_state["CLAIM_RESULT"] is None:
    st.error("No claim has been processed yet.")
    st.page_link("pages/1_Upload_Claim.py", label="⬅️ Upload a claim file")
    st.stop()

result = st.session_state["CLAIM_RESULT"]
if result is None:
    st.error("Claim result is not available.")
    st.page_link("pages/1_Upload_Claim.py", label="⬅️ Upload a claim file")
    st.stop()

extracted = result.get("extracted", {})

# Layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📌 Key Details")

    st.write(f"**Claim ID:** {extracted.get('claim_id', 'N/A')}")
    st.write(f"**Patient:** {extracted.get('patient', {}).get('name', 'N/A')}")
    st.write(f"**Member ID:** {extracted.get('patient', {}).get('member_id', 'N/A')}")
    st.write(f"**Provider ID:** {extracted.get('provider', {}).get('id', 'N/A')}")
    st.write(f"**Service Date:** {extracted.get('date_of_service', 'N/A')}")
    st.write(f"**Total Amount:** ${extracted.get('total_amount', 0)}")

    st.write("### Diagnosis Codes")
    st.json(extracted.get("diagnosis_codes", []))

    st.write("### Procedure Codes")
    st.json(extracted.get("procedure_codes", []))

with col2:
    st.subheader("📄 Full Extracted Payload")
    st.json(extracted)

# Navigation
st.write("---")
st.page_link("pages/3_Validation_Results.py", label="➡️ Go to Validation Results", use_container_width=True)
