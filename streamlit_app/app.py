import streamlit as st
import requests
import os
from utils.components import styled_success, styled_error, styled_info, load_css
from utils.state_manager import init_session_state, reset_state

# -----------------------
# Streamlit Page Settings
# -----------------------
st.set_page_config(
    page_title="MediSure Agentic Claims",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
st.markdown(load_css(), unsafe_allow_html=True)

# -----------------------
# Initialize App State
# -----------------------
init_session_state()

# -----------------------
# Sidebar Navigation
# -----------------------
st.sidebar.markdown("<h2 class='sidebar-title'>🏥 MediSure Dashboard</h2>", unsafe_allow_html=True)

st.sidebar.page_link("pages/1_Upload_Claim.py", label="📤 Upload Claim")
st.sidebar.page_link("pages/2_Extracted_Data.py", label="📄 Extracted Data")
st.sidebar.page_link("pages/3_Validation_Results.py", label="🧪 Validation Results")
st.sidebar.page_link("pages/4_Fraud_Analysis.py", label="🕵️ Fraud Analysis")
st.sidebar.page_link("pages/5_Final_Summary.py", label="📘 Final Summary")

st.sidebar.markdown("---")
st.sidebar.button("🔄 Reset", on_click=reset_state)

# -----------------------
# Main Home Page Content
# -----------------------
st.markdown("<h1>🏥 MediSure Agentic Claims Automation</h1>", unsafe_allow_html=True)
st.write("Welcome to the MediSure Agentic Claims Automation System dashboard.")

# Instructions box (using custom styled component)
styled_info(
    "How to Use This System",
    """
    1. <b>Upload a claim file</b> (JSON, XML, PDF)<br>
    2. <b>See extracted structured values</b><br>
    3. <b>View validation results</b><br>
    4. <b>Analyze fraud signals</b><br>
    5. <b>Get the final adjudication summary</b><br><br>
    Use the left sidebar to navigate through steps after uploading a file.
    """
)

# ─── BACKEND CONNECTION (works everywhere) ──────────────────────────────

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  # local fallback

try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=8)
    if r.status_code == 200:
        styled_success("Backend Connected", "MediSure API is healthy and ready")
    else:
        styled_error("Backend Warning", f"Status {r.status_code}")
except Exception:
    styled_error("Backend Offline", f"Cannot reach API at {BACKEND_URL}")
