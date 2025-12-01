import streamlit as st

st.set_page_config(page_title="Color Test", layout="wide")

st.title("🎨 Color Test Page")

# Test 1: Direct inline HTML (this MUST work)
st.markdown("""
    <div style="
        background-color: #d3f9d8;
        border-left: 6px solid #2f9e44;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 10px 0;
    ">
        <span style="color: #2f9e44; font-size: 18px; font-weight: 600;">
            ✅ SUCCESS - This should be GREEN
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="
        background-color: #fff3cd;
        border-left: 6px solid #e67700;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 10px 0;
    ">
        <span style="color: #e67700; font-size: 18px; font-weight: 600;">
            ⚠️ WARNING - This should be ORANGE/YELLOW
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="
        background-color: #ffe0e0;
        border-left: 6px solid #e03131;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 10px 0;
    ">
        <span style="color: #c92a2a; font-size: 18px; font-weight: 600;">
            ❌ ERROR - This should be RED
        </span>
    </div>
""", unsafe_allow_html=True)

# Test 2: Streamlit default (for comparison)
st.success("Default Streamlit Success")
st.warning("Default Streamlit Warning")
st.error("Default Streamlit Error")