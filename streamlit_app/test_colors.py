import streamlit as st
from utils.components import styled_success, styled_warning, styled_error, styled_info, decision_card, summary_card

st.set_page_config(page_title="Color Test", layout="wide")

st.title("🎨 Color Test Page - BOLD COLORS")

# Test custom components
styled_success("SUCCESS", "This should be BOLD GREEN with WHITE text")
styled_warning("WARNING", "This should be BOLD ORANGE with WHITE text")
styled_error("ERROR", "This should be BOLD RED with WHITE text")
styled_info("INFO", "This should be BOLD BLUE with WHITE text")

st.markdown("---")

# Test decision card
decision_card(
    decision="MANUAL_REVIEW",
    reason="Procedures require prior authorization: 80050",
    confidence=0.85
)

# Test summary card
summary_card(
    claim_id="CLM-001",
    patient="John Carter",
    member_id="M12345678",
    plan="PREMIUM",
    amount=430.00,
    decision="MANUAL_REVIEW",
    reasons="Procedures require prior authorization: 80050"
)