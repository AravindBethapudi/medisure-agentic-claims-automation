import streamlit as st
from utils.api_client import APIClient
from utils.components import styled_success, styled_error, styled_info

# Page config
st.set_page_config(page_title="Upload Claim", layout="wide")

# Load global CSS
with open("assets/style.css") as css:
    st.markdown(f"<style>{css.read()}</style>", unsafe_allow_html=True)

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
if st.button("🚀 Process Claim", use_container_width=True):

    if uploaded_file is None:
        styled_error("No File Selected", "Please upload a file before processing.")
    else:
        with st.spinner("Processing your claim… Please wait ⏳"):
            result = APIClient.process_claim(uploaded_file)

        if result:
            # Save to session state
            st.session_state["CLAIM_RESULT"] = result

            styled_success("Claim Processed Successfully! 🎉")

            st.write("### Next steps:")
            st.page_link("pages/2_Extracted_Data.py", label="➡️ View Extracted Claim Data")
        else:
            styled_error("Processing Failed", "Check backend logs for details.")