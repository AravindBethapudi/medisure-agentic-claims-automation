import streamlit as st

def init_session_state():
    """
    Initialize all session state variables with default values.
    """
    if "CLAIM_RESULT" not in st.session_state:
        st.session_state["CLAIM_RESULT"] = None

def reset_state():
    """
    Reset all session state variables to their initial values.
    """
    st.session_state["CLAIM_RESULT"] = None
    st.rerun()

