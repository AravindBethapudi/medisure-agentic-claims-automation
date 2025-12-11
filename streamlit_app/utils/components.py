import streamlit as st
from utils.components import styled_success, styled_info, load_css, section_header
from .pdf_generator import PatientLetterPDF

st.set_page_config(page_title="Extracted Data", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

section_header("🧾 Extracted Claim Data")

# Check if we have extracted data
if "EXTRACTED_DATA" not in st.session_state or not st.session_state.EXTRACTED_DATA:
    styled_error("No Data Available", "Please upload a claim file first.")
    st.page_link("pages/1_Upload_Claim.py", label="Go to Upload Claim")
    st.stop()

data = st.session_state.EXTRACTED_DATA

# Display Key Details
st.subheader("📌 Key Details")
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Claim ID:** `{data.get('claim_id', 'N/A')}`")
    st.markdown(f"**Patient:** {data.get('patient_name', 'N/A')}")
    st.markdown(f"**Member ID:** `{data.get('member_id', 'N/A')}`")
    st.markdown(f"**Provider:** {data.get('provider_name', 'N/A')}")

with col2:
    st.markdown(f"**Provider ID:** {data.get('provider_id', 'N/A')}")
    st.markdown(f"**Service Date:** {data.get('service_date', 'N/A')}")
    st.markdown(f"**Total Amount:** `${data.get('claim_amount', 0):,.2f}`")
    st.markdown(f"**Plan Type:** {data.get('plan_type', 'N/A')}")

st.divider()

# Clinical Information with Code Descriptions
section_header("🔬 Clinical Information")

# Check if we have the new clinical information structure
if 'clinical_information' in data:
    clinical_info = data['clinical_information']
    
    # Diagnosis Codes with Descriptions
    diagnoses = clinical_info.get('diagnoses', [])
    if diagnoses:
        st.subheader("📋 Diagnosis Codes")
        for diag in diagnoses:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"**`{diag.get('code', 'N/A')}`**")
                with col2:
                    st.write(diag.get('description', 'No description available'))
                with col3:
                    st.caption(f"*{diag.get('category', 'General')}*")
            st.divider()
    
    # Procedure Codes with Descriptions
    procedures = clinical_info.get('procedures', [])
    if procedures:
        st.subheader("💉 Procedure Codes")
        for proc in procedures:
            with st.container():
                col1, col2, col3 = st.columns([1, 3, 2])
                with col1:
                    st.markdown(f"**`{proc.get('code', 'N/A')}`**")
                with col2:
                    desc = proc.get('description', 'No description available')
                    # Truncate very long descriptions
                    if len(desc) > 150:
                        desc = desc[:150] + "..."
                    st.write(desc)
                with col3:
                    st.caption(f"*{proc.get('category', 'General')}*")
            st.divider()
    
    # Clinical Summary
    clinical_summary = clinical_info.get('summary')
    if clinical_summary:
        with st.expander("📊 Clinical Summary", expanded=False):
            st.write(clinical_summary)

else:
    # Fallback to old format
    col_diag, col_proc = st.columns(2)
    
    with col_diag:
        st.subheader("📋 Diagnosis Codes")
        diag_codes = data.get('diagnosis_codes', [])
        if diag_codes:
            for i, code in enumerate(diag_codes):
                st.write(f"{i}: `{code}`")
        else:
            st.info("No diagnosis codes extracted")
    
    with col_proc:
        st.subheader("💉 Procedure Codes")
        proc_codes = data.get('procedure_codes', [])
        if proc_codes:
            for i, code in enumerate(proc_codes):
                st.write(f"{i}: `{code}`")
        else:
            st.info("No procedure codes extracted")

st.divider()

# Full Extracted Payload
with st.expander("📄 Full Extracted Payload", expanded=False):
    st.json(data)

# Navigation
st.page_link("pages3_Validation_Results.py", label="➡️ Go to Validation Results")