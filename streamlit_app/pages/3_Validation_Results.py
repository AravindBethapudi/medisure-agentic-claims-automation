import streamlit as st
from utils.components import load_css

st.set_page_config(page_title="Validation", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)

st.title("🔍 Validation Results")

# Check if claim processed
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

validation = result.get("validation", {})
validation_results = validation.get("details", {})


def status_box(title, result_dict):
    """Colored status box with BOLD, VISIBLE colors"""
    status = result_dict.get("status", "UNKNOWN")
    reason = result_dict.get("reason", "N/A")

    if status == "PASSED":
        bg_color = "#22c55e"      # Bold green
        text_color = "#ffffff"    # White text
        icon = "✅"
    elif status == "FAILED":
        bg_color = "#ef4444"      # Bold red
        text_color = "#ffffff"
        icon = "❌"
    else:  # NEEDS_REVIEW, UNKNOWN, etc.
        bg_color = "#f59e0b"      # Bold orange
        text_color = "#ffffff"
        icon = "⚠️"

    st.markdown(f"""
        <div style="
            background-color: {bg_color};
            padding: 18px;
            border-radius: 10px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <h4 style="color: {text_color}; margin: 0 0 10px 0; font-size: 18px;">
                {icon} {title}
            </h4>
            <p style="color: {text_color}; margin: 5px 0; font-size: 15px;">
                <strong>Status:</strong> {status}
            </p>
            <p style="color: {text_color}; margin: 5px 0; font-size: 14px;">
                <strong>Reason:</strong> {reason}
            </p>
        </div>
    """, unsafe_allow_html=True)


# Top-level decision
decision = validation.get("decision", "UNKNOWN")

# Decision color
if decision == "APPROVE":
    dec_bg = "#22c55e"
    dec_icon = "✅"
elif decision == "REJECT" or decision == "DENIED":
    dec_bg = "#ef4444"
    dec_icon = "❌"
else:
    dec_bg = "#3b82f6"
    dec_icon = "🧿"

st.markdown(f"""
    <div style="
        background-color: {dec_bg};
        padding: 16px 20px;
        border-radius: 10px;
        margin: 15px 0;
    ">
        <h3 style="color: #ffffff; margin: 0; font-size: 20px;">
            {dec_icon} Overall Validation Decision: {decision}
        </h3>
    </div>
""", unsafe_allow_html=True)

# Message
message = validation.get("message", "")
if message:
    st.markdown(f"""
        <div style="
            background-color: #3b82f6;
            padding: 14px 18px;
            border-radius: 8px;
            margin: 10px 0;
        ">
            <p style="color: #ffffff; margin: 0; font-size: 15px;">
                ℹ️ {message}
            </p>
        </div>
    """, unsafe_allow_html=True)

st.write("---")

# 4 validation blocks
st.header("Validation Checks")

col1, col2 = st.columns(2)

with col1:
    status_box("Eligibility Check", validation_results.get("eligibility", {}))
    status_box("Authorization Check", validation_results.get("authorization", {}))

with col2:
    status_box("Coverage Check", validation_results.get("coverage", {}))
    status_box("Business Rules Evaluation", validation_results.get("business_rules", {}))

# Navigation
st.write("---")
st.page_link("pages/4_Fraud_Analysis.py", label="➡️ Go to Fraud Analysis")