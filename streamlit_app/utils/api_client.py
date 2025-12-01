import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8000/process-claim"

class APIClient:

    @staticmethod
    def process_claim(file):
        """
        Upload claim file to FastAPI backend and return full pipeline output.
        """
        try:
            files = {
                "file": (file.name, file.getvalue(), file.type)
            }

            response = requests.post(BACKEND_URL, files=files)

            if response.status_code != 200:
                st.error(f"Backend Error: {response.text}")
                return None

            return response.json()

        except Exception as e:
            st.error(f"❌ Failed to connect to backend: {e}")
            return None
