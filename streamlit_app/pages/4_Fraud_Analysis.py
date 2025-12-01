import streamlit as st
from utils.components import load_css

st.set_page_config(page_title="Fraud Analysis", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)
st.title("🕵️ Fraud Analysis Results")

# Check session
if "CLAIM_RESULT" not in st.session_state or st.session_state["CLAIM_RESULT"] is None:
    st.markdown("""
        <div style="background-color: #ef4444; padding: 16px; border-radius: 8px; margin: 10px 0;">
            <p style="color: #ffffff; font-weight: 600; margin: 0;">❌ No claim processed yet.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Upload_Claim.py", label="⬅️ Upload a claim file")
    st.stop()

result = st.session_state["CLAIM_RESULT"]
if result is None:
    st.error("Claim result is not available.")
    st.page_link("pages/1_Upload_Claim.py", label="⬅️ Upload a claim file")
    st.stop()

fraud = result.get("fraud_analysis", {})

risk_score = fraud.get("risk_score", 0)
risk_level = fraud.get("risk_level", "UNKNOWN")
fraud_checks = fraud.get("fraud_checks", {})
red_flags = fraud.get("red_flags", [])
recommendation = fraud.get("recommendation", "")


def get_risk_style(level):
    """Return background color and icon for risk level"""
    styles = {
        "MINIMAL": ("#22c55e", "🟢"),   # Green
        "LOW": ("#3b82f6", "🔵"),        # Blue
        "MEDIUM": ("#f59e0b", "🟠"),     # Orange
        "HIGH": ("#ef4444", "🔴"),       # Red
    }
    return styles.get(level, ("#6b7280", "⚪"))


bg_color, icon = get_risk_style(risk_level)

# Main fraud banner
st.markdown(f"""
    <div style="
        background-color: {bg_color};
        padding: 22px;
        border-radius: 12px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="color: #ffffff; margin: 0 0 10px 0; font-size: 24px;">
            {icon} Fraud Risk Level: {risk_level}
        </h2>
        <h4 style="color: #ffffff; margin: 0; font-size: 18px;">
            Risk Score: {risk_score:.2f}
        </h4>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Fraud checks section
st.header("🔍 Fraud Checks Breakdown")

if fraud_checks:
    for check_name, details in fraud_checks.items():
        # Determine color based on flagged status
        is_flagged = details.get("flagged", False)
        check_bg = "#ef4444" if is_flagged else "#22c55e"
        check_icon = "🚨" if is_flagged else "✅"
        
        st.markdown(f"""
            <div style="
                background-color: {check_bg};
                padding: 14px 18px;
                border-radius: 8px;
                margin: 10px 0;
            ">
                <h4 style="color: #ffffff; margin: 0 0 8px 0;">
                    {check_icon} {check_name.replace('_', ' ').title()}
                </h4>
                <p style="color: #ffffff; margin: 0; font-size: 14px;">
                    Score: {details.get('score', 'N/A')} | 
                    Flagged: {is_flagged}
                </p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="background-color: #22c55e; padding: 14px; border-radius: 8px;">
            <p style="color: #ffffff; margin: 0;">✅ No fraud checks data available.</p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# Red flags
st.header("🚩 Red Flags")

if red_flags and len(red_flags) > 0:
    for flag in red_flags:
        st.markdown(f"""
            <div style="
                background-color: #ef4444;
                padding: 12px 16px;
                border-radius: 8px;
                margin: 8px 0;
            ">
                <p style="color: #ffffff; margin: 0; font-size: 15px;">
                    🚩 {flag}
                </p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="background-color: #22c55e; padding: 14px 18px; border-radius: 8px;">
            <p style="color: #ffffff; margin: 0; font-weight: 600;">
                ✅ No red flags detected.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# Recommendation
st.header("📘 Fraud Recommendation")

st.markdown(f"""
    <div style="
        background-color: #3b82f6;
        padding: 16px 20px;
        border-radius: 10px;
        margin: 10px 0;
    ">
        <p style="color: #ffffff; margin: 0; font-size: 16px;">
            ℹ️ {recommendation if recommendation else "No recommendation available."}
        </p>
    </div>
""", unsafe_allow_html=True)

# Navigation
st.write("---")
st.page_link("pages/5_Final_Summary.py", label="➡️ Go to Final Summary")