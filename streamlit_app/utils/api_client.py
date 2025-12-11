import os
import requests
import streamlit as st
from typing import Optional, Dict, Any
from .components import styled_error, styled_success, styled_warning, styled_info

# ─── BACKEND URL CONFIGURATION ──────────────────────────────
# Priority: Streamlit Secrets > Environment Variable > Local Fallback
if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"]
else:
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Remove trailing slash if present
BACKEND_URL = BACKEND_URL.rstrip("/")


class APIClient:
    """Client for communicating with MediSure FastAPI backend"""

    @staticmethod
    def health_check() -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(
                f"{BACKEND_URL}/health", 
                timeout=15
            )
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def wake_up_backend() -> bool:
        """
        Wake up backend if it's sleeping
        Returns True if backend is awake and ready
        """
        with st.spinner("⏳ Waking up backend service..."):
            try:
                response = requests.get(
                    f"{BACKEND_URL}/health", 
                    timeout=90
                )
                if response.status_code == 200:
                    styled_success("Backend Ready", "Backend is ready for processing!")
                    return True
                else:
                    styled_warning("Backend Warning", "Backend responded but may not be fully ready")
                    return False
            except requests.exceptions.Timeout:
                styled_error("Timeout", "Backend took too long to wake up")
                return False
            except Exception as e:
                styled_error("Connection Failed", f"Failed to wake backend: {str(e)}")
                return False

    @staticmethod
    def process_claim(file) -> Optional[Dict[Any, Any]]:
        """
        Upload claim file to backend and return full pipeline output.
        Also saves all data to Streamlit session state.
        """
        # Check if backend is awake first
        if not APIClient.health_check():
            styled_warning("Backend Sleeping", "Attempting to wake it up...")
            if not APIClient.wake_up_backend():
                styled_error("Connection Failed", "Could not connect to backend")
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
                    timeout=180
                )

            # Handle response
            if response.status_code == 200:
                result = response.json()
                
                # Save all data to session state
                APIClient._save_to_session_state(result)
                
                # Log what was saved
                extracted_data = result.get('extracted_data', {})
                styled_success(
                    "Claim Processed",
                    f"Extracted {len(extracted_data.get('diagnosis_codes', []))} diagnosis codes and "
                    f"{len(extracted_data.get('procedure_codes', []))} procedure codes"
                )
                
                return result
            
            elif response.status_code == 503:
                styled_warning("Service Unavailable", "Backend service unavailable (possibly restarting)")
                return None
            
            elif response.status_code == 504:
                styled_error("Timeout", "Processing took too long. Try a simpler document.")
                return None
            
            else:
                styled_error("Backend Error", f"Status {response.status_code}")
                with st.expander("📋 Error Details"):
                    st.code(response.text)
                return None

        except requests.exceptions.ConnectionError:
            styled_error("Connection Failed", f"Cannot connect to backend at {BACKEND_URL}")
            return None
        
        except requests.exceptions.Timeout:
            styled_error("Timeout", "Request timed out after 3 minutes")
            return None
        
        except Exception as e:
            styled_error("Processing Error", f"Unexpected error: {str(e)}")
            return None

    @staticmethod
    def _save_to_session_state(result: Dict[str, Any]):
        """Save all processing results to Streamlit session state"""
        try:
            # Save the full result
            st.session_state["CLAIM_RESULT"] = result
            
            # Save individual components for easy access
            extracted_data = result.get('extracted_data', {})
            st.session_state["EXTRACTED_DATA"] = extracted_data
            
            validation_result = result.get('validation_result', {})
            st.session_state["VALIDATION_RESULT"] = validation_result
            
            fraud_analysis = result.get('fraud_analysis', {})
            st.session_state["FRAUD_ANALYSIS"] = fraud_analysis
            
            final_decision = result.get('final_decision', {})
            st.session_state["FINAL_DECISION"] = final_decision
            
            summary = result.get('summary', {})
            st.session_state["SUMMARY"] = summary
            
            # Ensure clinical information is in extracted data
            if 'clinical_information' not in extracted_data:
                # Create clinical information from available data
                clinical_info = APIClient._create_clinical_info(extracted_data)
                if clinical_info:
                    extracted_data['clinical_information'] = clinical_info
                    st.session_state["EXTRACTED_DATA"] = extracted_data
            
            # Log success
            print(f"✅ Saved to session state: {len(extracted_data.keys())} keys")
            if 'clinical_information' in extracted_data:
                clinical_info = extracted_data['clinical_information']
                print(f"📋 Clinical info: {len(clinical_info.get('diagnoses', []))} diagnoses, "
                      f"{len(clinical_info.get('procedures', []))} procedures")
                
        except Exception as e:
            print(f"❌ Error saving to session state: {e}")

    @staticmethod
    def _create_clinical_info(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create clinical information structure from extracted data"""
        clinical_info = {
            'diagnoses': [],
            'procedures': [],
            'summary': ''
        }
        
        try:
            # Try to import medical codes module
            try:
                from ..utils.medical_codes import get_code_description, get_code_category
                use_medical_codes = True
            except ImportError:
                use_medical_codes = False
            
            # Process diagnosis codes
            diag_codes = extracted_data.get('diagnosis_codes', [])
            for code in diag_codes:
                if use_medical_codes:
                    description = get_code_description(code, is_procedure=False)
                    category = get_code_category(code, is_procedure=False)
                else:
                    description = f"ICD-10 code: {code}"
                    category = 'Unknown'
                
                clinical_info['diagnoses'].append({
                    'code': str(code),
                    'description': description,
                    'category': category
                })
            
            # Process procedure codes
            proc_codes = extracted_data.get('procedure_codes', [])
            for code in proc_codes:
                if use_medical_codes:
                    description = get_code_description(code, is_procedure=True)
                    category = get_code_category(code, is_procedure=True)
                else:
                    description = f"CPT code: {code}"
                    category = 'Unknown'
                
                clinical_info['procedures'].append({
                    'code': str(code),
                    'description': description,
                    'category': category
                })
            
            # Create summary
            if clinical_info['diagnoses'] or clinical_info['procedures']:
                summary_parts = []
                
                if clinical_info['diagnoses']:
                    diag_list = [f"{d['code']} ({d['description'].split(',')[0][:30]}...)" 
                                for d in clinical_info['diagnoses']]
                    summary_parts.append(f"Diagnoses: {', '.join(diag_list)}")
                
                if clinical_info['procedures']:
                    proc_list = [f"{p['code']} ({p['description'].split('.')[0][:30]}...)" 
                                for p in clinical_info['procedures']]
                    summary_parts.append(f"Procedures: {', '.join(proc_list)}")
                
                clinical_info['summary'] = '. '.join(summary_parts) + '.'
            
            return clinical_info
            
        except Exception as e:
            print(f"❌ Error creating clinical info: {e}")
            # Return basic structure even if there's an error
            return clinical_info

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