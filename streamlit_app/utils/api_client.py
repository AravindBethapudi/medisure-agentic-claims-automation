import os
import requests
import streamlit as st
from typing import Optional, Dict, Any

# Get backend URL from secrets or environment
if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"]
else:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

class APIClient:

    @staticmethod
    def health_check() -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=10)
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def process_claim(file) -> Optional[Dict[Any, Any]]:
        """
        Upload claim file to backend (Render) and return full pipeline output.
        """
        try:
            files = {
                "file": (file.name, file.getvalue(), file.type)
            }

            with st.spinner("🔄 Processing claim through AI pipeline..."):
                response = requests.post(
                    f"{BACKEND_URL}/process-claim",
                    files=files,
                    timeout=180  # 3 minutes for Render (free tier can be slow)
                )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503:
                st.warning("⏳ Backend is waking up from sleep (Render free tier)")
                st.info("Please wait 30-60 seconds and try again")
                return None
            else:
                st.error(f"❌ Backend Error ({response.status_code})")
                with st.expander("Error Details"):
                    st.code(response.text)
                return None

        except requests.exceptions.ConnectionError:
            st.error(f"❌ Cannot connect to Render backend")
            st.warning("🔧 Check if your Render service is running")
            st.info(f"Backend URL: `{BACKEND_URL}`")
            return None
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out after 3 minutes")
            st.info("Render free tier may be slow. Consider upgrading for better performance.")
            return None
        
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None