import streamlit as st
from utils.api_client import APIClient
from pathlib import Path
from utils.components import styled_success, styled_error, styled_info, load_css

st.set_page_config(page_title="Upload Claim", layout="wide")

# Load CSS
st.markdown(load_css(), unsafe_allow_html=True)

# Page Title
st.title("📤 Upload Claim File")
st.write("Upload a claim file in **JSON**, **XML**, or **PDF** format to begin processing.")

# File uploader
uploaded_file = st.file_uploader(
    "Choose a claim file",
    type=["json", "xml", "pdf"],
    help="Accepted formats: .json, .xml, .pdf"
)

# Button to trigger backend processing
if st.button("🚀 Process Claim", use_container_width=True, type="primary"):
    if uploaded_file is None:
        styled_error("No File Selected", "Please upload a file before processing.")
    else:
        # Show file info
        file_info = f"**File:** {uploaded_file.name} ({uploaded_file.size:,} bytes)"
        st.markdown(file_info)
        
        # Process the claim
        result = APIClient.process_claim(uploaded_file)

        if result:
            # Verify data was saved
            if "EXTRACTED_DATA" in st.session_state and st.session_state.EXTRACTED_DATA:
                extracted = st.session_state.EXTRACTED_DATA
                
                # Show success with details
                diagnosis_count = len(extracted.get('diagnosis_codes', []))
                procedure_count = len(extracted.get('procedure_codes', []))
                
                styled_success(
                    "✅ Claim Processed Successfully!",
                    f"Extracted {diagnosis_count} diagnosis codes and {procedure_count} procedure codes"
                )
                
                # Show patient info
                patient_name = extracted.get('patient_name', 'Unknown')
                claim_amount = extracted.get('claim_amount', 0)
                st.info(f"**Patient:** {patient_name} | **Amount:** ${claim_amount:,.2f}")
                
            st.write("### Next steps:")
            st.page_link("pages/2_Extracted_Data.py", label="➡️ View Extracted Claim Data", icon="📋")
            st.page_link("pages/5_Final_Summary.py", label="➡️ View Final Summary", icon="📊")
        else:
            styled_error("Processing Failed", "Check backend logs for details.")