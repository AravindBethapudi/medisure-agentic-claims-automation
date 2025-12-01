import streamlit as st
from utils.components import load_css

st.set_page_config(page_title="Final Summary", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)
st.title("📘 Final Claim Summary")

# Ensure session state is available
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

summary = result.get("summary", {})
final_decision = result.get("final_decision", {})

decision = final_decision.get("decision", "UNKNOWN")
reason = final_decision.get("reason", "N/A")
confidence = final_decision.get("confidence", None)


def get_decision_style(dec):
    """Return colors for decision type"""
    styles = {
        "APPROVE": ("#22c55e", "#15803d", "✅"),      # Green
        "REJECT": ("#ef4444", "#b91c1c", "❌"),        # Red
        "DENIED": ("#ef4444", "#b91c1c", "❌"),        # Red
        "MANUAL_REVIEW": ("#f59e0b", "#d97706", "⚠️"), # Orange
    }
    return styles.get(dec, ("#6b7280", "#4b5563", "❓"))


bg_color, border_color, icon = get_decision_style(decision)

# Final decision banner
st.markdown(f"""
    <div style="
        background-color: {bg_color};
        border-left: 8px solid {border_color};
        padding: 24px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    ">
        <h2 style="color: #ffffff; margin: 0 0 12px 0; font-size: 26px; font-weight: 700;">
            {icon} Final Decision: {decision}
        </h2>
        <p style="color: #ffffff; margin: 0; font-size: 17px;">
            <strong>Reason:</strong> {reason}
        </p>
        {f'<p style="color: #ffffff; margin: 8px 0 0 0; font-size: 15px;">Confidence: {confidence:.0%}</p>' if confidence else ''}
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Executive summary
st.subheader("📝 Executive Summary")

exec_summary = summary.get("executive_summary", "No executive summary available.")
st.markdown(f"""
    <div style="
        background-color: #fef3c7;
        border: 2px solid #f59e0b;
        padding: 18px;
        border-radius: 10px;
        margin: 10px 0;
    ">
        <p style="color: #92400e; margin: 0; font-size: 16px; font-weight: 500;">
            {exec_summary}
        </p>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Detailed summary
st.subheader("📄 Detailed Summary")

with st.expander("Show Detailed Breakdown", expanded=True):
    detailed = summary.get("detailed_summary", "No details available.")
    st.text(detailed)

st.write("---")

# Action required
st.subheader("🛠️ Action Required")

actions = summary.get("action_required", "No specific action required.")

if decision == "APPROVE" or "No action" in str(actions):
    action_bg = "#22c55e"
    action_icon = "✅"
elif decision == "REJECT" or decision == "DENIED":
    action_bg = "#ef4444"
    action_icon = "❌"
else:
    action_bg = "#f59e0b"
    action_icon = "⚠️"

st.markdown(f"""
    <div style="
        background-color: {action_bg};
        padding: 16px 20px;
        border-radius: 10px;
        margin: 10px 0;
    ">
        <p style="color: #ffffff; margin: 0; font-size: 16px; font-weight: 600;">
            {action_icon} {actions}
        </p>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# Navigation button
st.page_link("pages/1_Upload_Claim.py", label="🔄 Process Another Claim")