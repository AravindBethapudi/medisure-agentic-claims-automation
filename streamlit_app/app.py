import streamlit as st
import requests
import os
from utils.components import styled_success, styled_error, styled_info
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
def check_backend_status():
    """Display backend connection status with styled components"""
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if r.status_code == 200:
            data = r.json()
            st.success("🟢 **Backend Connected** - MediSure API (Render) is healthy and ready")
            
            # Show additional info if available
            if isinstance(data, dict):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", data.get("status", "healthy"))
                with col2:
                    st.metric("Service", data.get("service", "API"))
                with col3:
                    version = data.get("version", "N/A")
                    st.metric("Version", version)
            return True
        else:
            st.warning(f"⚠️ **Backend Warning** - Status {r.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        st.error("🔴 **Backend Timeout** - Render backend is slow to respond")
        st.info("⏳ Render free tier may take 30-60s to wake up from sleep")
        
        # Offer to wake it up
        if st.button("🔄 Wake Up Backend", type="secondary"):
            APIClient.wake_up_backend()
            st.rerun()
        return False
        
    except requests.exceptions.ConnectionError:
        st.error("🔴 **Backend Offline** - Cannot reach Render backend")
        with st.expander("🔧 Troubleshooting"):
            st.markdown(f"""
            **Backend URL:** `{BACKEND_URL}`
            
            **Quick Checks:**
            1. Visit [{BACKEND_URL}/docs]({BACKEND_URL}/docs) - Should show API documentation
            2. Visit [{BACKEND_URL}/health]({BACKEND_URL}/health) - Should return health status
            3. Check [Render Dashboard](https://dashboard.render.com) - Verify service is running
            
            **Common Issues:**
            - Service is sleeping (free tier) - Click "Wake Up Backend" button
            - Service is restarting - Wait 1-2 minutes
            - Deployment failed - Check Render logs
            """)
        
        if st.button("🔄 Retry Connection", type="primary"):
            st.rerun()
        return False
        
    except Exception as e:
        st.error(f"🔴 **Backend Error** - {str(e)}")
        return False
# Load custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    try:
        with open(css_path) as f:
            return f"<style>{f.read()}</style>"
    except FileNotFoundError:
        return "<style></style>"  # silent fallback

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

# Backend health check (using custom styled components)
# NEW — works both locally and on Render
# ─── BACKEND CONNECTION (works everywhere) ──────────────────────────────
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")  # local fallback

try:
    r = requests.get(f"{BACKEND_URL}/health", timeout=8)
    if r.status_code == 200:
        styled_success("Backend Connected", "MediSure API is healthy and ready")
    else:
        styled_error("Backend Warning", f"Status {r.status_code}")
except Exception:
    styled_error("Backend Offline", f"Cannot reach API at {BACKEND_URL}")