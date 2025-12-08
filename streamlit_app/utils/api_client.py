import os
import requests
import streamlit as st
from typing import Optional, Dict, Any

# ─── BACKEND URL CONFIGURATION ──────────────────────────────
# Priority: Streamlit Secrets > Environment Variable > Local Fallback
if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"]
else:
    BACKEND_URL = os.getenv(
        "BACKEND_URL", 
        "https://medisure-agentic-claims-automation.onrender.com"
    )

# Remove trailing slash if present
BACKEND_URL = BACKEND_URL.rstrip("/")


class APIClient:
    """Client for communicating with MediSure FastAPI backend on Render"""

    @staticmethod
    def health_check() -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/health", 
                timeout=15  # Render can be slower on free tier
            )
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def wake_up_backend() -> bool:
        """
        Wake up Render backend if it's sleeping (free tier spins down after inactivity)
        Returns True if backend is awake and ready
        """
        with st.spinner("⏳ Waking up backend service (this may take 30-60 seconds)..."):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/health", 
                    timeout=90  # Give it time to wake up
                )
                if response.status_code == 200:
                    st.success("✅ Backend is ready!")
                    return True
                else:
                    st.warning("⚠️ Backend responded but may not be fully ready")
                    return False
            except requests.exceptions.Timeout:
                st.error("❌ Backend took too long to wake up")
                st.info("💡 Try again in a minute or check Render dashboard")
                return False
            except Exception as e:
                st.error(f"❌ Failed to wake backend: {str(e)}")
                return False

    @staticmethod
    def process_claim(file) -> Optional[Dict[Any, Any]]:
        """
        Upload claim file to Render backend and return full pipeline output.
        
        Args:
            file: Streamlit UploadedFile object
            
        Returns:
            Dict with processing results or None if failed
        """
        # Check if backend is awake first
        if not APIClient.health_check():
            st.warning("🔄 Backend appears to be sleeping. Attempting to wake it up...")
            if not APIClient.wake_up_backend():
                st.error("❌ Could not connect to backend")
                with st.expander("🔧 Troubleshooting"):
                    st.markdown(f"""
                    **Backend URL:** `{BACKEND_URL}`
                    
                    **Possible Issues:**
                    1. Render service is down - Check [Render Dashboard](https://dashboard.render.com)
                    2. Cold start taking longer than expected - Wait 1-2 minutes and retry
                    3. Network connectivity issues
                    
                    **Quick Tests:**
                    - Visit: [{BACKEND_URL}/docs]({BACKEND_URL}/docs)
                    - Health: [{BACKEND_URL}/health]({BACKEND_URL}/health)
                    """)
                return None
        
        try:
            # Prepare file for upload
            files = {
                "file": (file.name, file.getvalue(), file.type)
            }

            # Process the claim
            with st.spinner("🔄 Processing claim through AI pipeline..."):
                response = requests.post(
                    f"{BACKEND_URL}/process-claim",
                    files=files,
                    timeout=180  # 3 minutes timeout for AI processing
                )

            # Handle response
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 503:
                st.warning("⏳ Backend service unavailable (possibly restarting)")
                st.info("Please wait 1-2 minutes and try again")
                return None
            
            elif response.status_code == 504:
                st.error("⏱️ Gateway timeout - processing took too long")
                st.info("This claim may be too complex. Try a simpler document.")
                return None
            
            else:
                st.error(f"❌ Backend Error (Status {response.status_code})")
                with st.expander("📋 Error Details"):
                    st.code(response.text)
                return None

        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to backend")
            st.info(f"Backend URL: `{BACKEND_URL}`")
            st.warning("💡 Check if Render service is running in dashboard")
            return None
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out after 3 minutes")
            st.info("Render free tier may be slow. The service might still be processing.")
            st.warning("💡 Consider upgrading to Render paid tier for better performance")
            return None
        
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            with st.expander("🐛 Debug Info"):
                st.exception(e)
            return None

    @staticmethod
    def get_backend_info() -> Dict[str, Any]:
        """Get backend service information"""
        try:
            response = requests.get(f"{BACKEND_URL}/", timeout=10)
            if response.status_code == 200:
                return response.json()
            return {"error": f"Status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}