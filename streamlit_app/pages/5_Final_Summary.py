import streamlit as st
from utils.components import load_css, styled_success, styled_error, styled_info, styled_warning

st.set_page_config(page_title="Final Summary", layout="wide")
st.markdown(load_css(), unsafe_allow_html=True)
st.title("Final Claim Summary")

# ===================================================================
# Check if claim was processed
# ===================================================================
if "CLAIM_RESULT" not in st.session_state or st.session_state["CLAIM_RESULT"] is None:
    st.markdown("""
        <div style="background-color: #ef4444; padding: 16px; border-radius: 8px; margin: 10px 0;">
            <p style="color: #ffffff; font-weight: 600; margin: 0;">No claim processed yet.</p>
        </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Upload_Claim.py", label="Upload a claim file")
    st.stop()

result = st.session_state["CLAIM_RESULT"]
if result is None:
    styled_error("No Result", "Claim result is not available.")
    st.page_link("pages/1_Upload_Claim.py", label="Upload a claim file")
    st.stop()

summary = result.get("summary", {})
final_decision = result.get("final_decision", {})

decision = final_decision.get("decision", "UNKNOWN")
reason = final_decision.get("reason", "N/A")
confidence = final_decision.get("confidence", None)

# ===================================================================
# Decision banner styling
# ===================================================================
def get_decision_style(dec):
    styles = {
        "APPROVE": ("#22c55e", "#15803d", "✅"),
        "REJECT": ("#ef4444", "#b91c1c", "❌"),
        "DENIED": ("#ef4444", "#b91c1c", "❌"),
        "MANUAL_REVIEW": ("#f59e0b", "#d97706", "⚠️"),
    }
    return styles.get(dec, ("#6b7280", "#4b5563", "❓"))

bg_color, border_color, icon = get_decision_style(decision)

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

# ===================================================================
# Executive Summary
# ===================================================================
st.subheader("Executive Summary")
exec_summary = summary.get("executive_summary", "No executive summary available.")
st.markdown(f"""
    <div style="background-color: #fef3c7; border: 2px solid #f59e0b; padding: 18px; border-radius: 10px; margin: 10px 0;">
        <p style="color: #92400e; margin: 0; font-size: 16px; font-weight: 500;">
            {exec_summary}
        </p>
    </div>
""", unsafe_allow_html=True)

st.write("---")

# ===================================================================
# Patient Letter (optional)
# ===================================================================
patient_letter = summary.get("patient_letter", "")
if patient_letter and patient_letter.strip() and patient_letter != "{}":
    st.subheader("Patient Letter")
    st.markdown(f"""
        <div style="background-color: #f0f9ff; border: 2px solid #3b82f6; padding: 20px; border-radius: 10px; margin: 10px 0;">
            <p style="color: #1e3a8a; margin: 0; font-size: 15px; line-height: 1.6; white-space: pre-line;">
                {patient_letter}
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.write("---")

## In pages/5_Final_Summary.py, replace the PDF section with:

if patient_letter and patient_letter.strip() and patient_letter != "{}":
    # ... existing patient letter display ...
    
    # ADD HTML DOWNLOAD BUTTON HERE
    st.write("")  # Add spacing
    
    try:
        from utils.pdf_utils import create_html_download_button
        
        # Get patient info
        patient_name = "Patient"
        claim_id = "Unknown"
        
        if "CLAIM_RESULT" in st.session_state:
            extracted = st.session_state.CLAIM_RESULT.get("extracted_data", {})
            patient_name = extracted.get("patient_name", "Patient")
            claim_id = extracted.get("claim_id", "Unknown")
        
        # Create download button
        create_html_download_button(patient_letter, patient_name, claim_id)
        
    except ImportError:
        # Simple fallback
        st.download_button(
            label="📄 Download Letter (Text)",
            data=patient_letter,
            file_name=f"MediSure_Claim_{claim_id}.txt",
            mime="text/plain"
        )
    
    st.write("---")
# ===================================================================
# Detailed Breakdown
# ===================================================================
st.subheader("Detailed Summary")
breakdown = summary.get("detailed_breakdown")
if breakdown:
    # Use a single expander for the entire detailed breakdown
    with st.expander("Show Detailed Breakdown", expanded=True):
        # Claim Information
        st.markdown("#### 📋 Claim Information")
        claim_info = breakdown.get("claim_information", {})
        col1, col2 = st.columns(2)
        with col1:
            for key in ['claim_id', 'patient_name', 'member_id', 'service_date']:
                if key in claim_info:
                    st.write(f"**{key.replace('_', ' ').title()}:** {claim_info[key]}")
        with col2:
            for key in ['provider', 'total_amount', 'plan_type', 'extraction_method']:
                if key in claim_info:
                    st.write(f"**{key.replace('_', ' ').title()}:** {claim_info[key]}")
        
        st.write("---")
        
        # Clinical Information with Code Descriptions - NO NESTED EXPANDER
        clinical_info = breakdown.get("clinical_information", {})
        if clinical_info:
            st.markdown("#### 🔬 Clinical Information")
            
            # Diagnosis Codes with Descriptions
            diagnoses = clinical_info.get("diagnoses", [])
            if diagnoses:
                st.markdown("##### 📋 Diagnosis Codes")
                for diag in diagnoses:
                    with st.container():
                        col1, col2, col3 = st.columns([1, 3, 2])
                        with col1:
                            st.markdown(f"**`{diag.get('code', 'N/A')}`**")
                        with col2:
                            st.write(diag.get('description', 'No description available'))
                        with col3:
                            st.caption(f"*{diag.get('category', 'General')}*")
                    st.divider()
            
            # Procedure Codes with Descriptions
            procedures = clinical_info.get("procedures", [])
            if procedures:
                st.markdown("##### 💉 Procedure Codes")
                for proc in procedures:
                    with st.container():
                        col1, col2, col3 = st.columns([1, 3, 2])
                        with col1:
                            st.markdown(f"**`{proc.get('code', 'N/A')}`**")
                        with col2:
                            desc = proc.get('description', 'No description available')
                            # Truncate very long descriptions
                            if len(desc) > 200:
                                desc = desc[:200] + "..."
                            st.write(desc)
                        with col3:
                            st.caption(f"*{proc.get('category', 'General')}*")
                    st.divider()
            
            # Clinical Summary - Use a container instead of expander
            clinical_summary = clinical_info.get('summary')
            if clinical_summary:
                st.markdown("##### 📊 Clinical Summary")
                st.info(clinical_summary)
            
            st.write("---")
        
        # Validation Results
        st.markdown("#### ✅ Validation Results")
        validation = breakdown.get("validation_results", {})
        col_val1, col_val2 = st.columns(2)
        
        with col_val1:
            for check in ['eligibility', 'coverage']:
                if check in validation:
                    check_data = validation[check]
                    icon = check_data.get('icon', '❓')
                    status = check_data.get('status', 'UNKNOWN')
                    reason_text = check_data.get('reason', 'N/A')
                    
                    if status == 'PASSED':
                        st.success(f"{icon} **{check.title()}:** {status}")
                    elif status == 'FAILED':
                        st.error(f"{icon} **{check.title()}:** {status}")
                    else:
                        st.info(f"{icon} **{check.title()}:** {status}")
                    
                    if reason_text != 'N/A':
                        st.caption(f"↳ {reason_text}")
        
        with col_val2:
            for check in ['authorization', 'business_rules']:
                if check in validation:
                    check_data = validation[check]
                    icon = check_data.get('icon', '❓')
                    status = check_data.get('status', 'UNKNOWN')
                    reason_text = check_data.get('reason', 'N/A')
                    
                    if status == 'PASSED':
                        st.success(f"{icon} **{check.replace('_', ' ').title()}:** {status}")
                    elif status == 'FAILED':
                        st.error(f"{icon} **{check.replace('_', ' ').title()}:** {status}")
                    else:
                        st.info(f"{icon} **{check.replace('_', ' ').title()}:** {status}")
                    
                    if reason_text != 'N/A':
                        st.caption(f"↳ {reason_text}")
        
        st.write("---")
        
        # Fraud Analysis
        st.markdown("#### 🔍 Fraud Analysis")
        fraud = breakdown.get("fraud_analysis", {})
        if fraud:
            col_fraud1, col_fraud2 = st.columns(2)
            with col_fraud1:
                risk_level = fraud.get('risk_level', 'LOW')
                risk_score = fraud.get('risk_score', '0%')
                icon = fraud.get('icon', '🟢')
                
                if risk_level == 'HIGH':
                    st.error(f"{icon} **Risk Level:** {risk_level}")
                elif risk_level == 'MEDIUM':
                    st.warning(f"{icon} **Risk Level:** {risk_level}")
                else:
                    st.success(f"{icon} **Risk Level:** {risk_level}")
                
                st.write(f"**Risk Score:** {risk_score}")
            
            with col_fraud2:
                flags = fraud.get('flags', [])
                if flags:
                    st.write("**Red Flags:**")
                    for flag in flags:
                        st.write(f"• {flag}")
                
                recommendation = fraud.get('recommendation')
                if recommendation:
                    st.write(f"**Recommendation:** {recommendation}")
        
        # Final Decision Details
        final_info = breakdown.get("final_decision", {})
        if final_info:
            st.write("---")
            st.markdown("#### 🎯 Final Decision Details")
            st.write(f"**Decision:** {final_info.get('decision', 'UNKNOWN')}")
            st.write(f"**Reason:** {final_info.get('reason', 'N/A')}")
            timestamp = final_info.get('timestamp')
            if timestamp:
                st.write(f"**Processed:** {timestamp}")

# ===================================================================
# ACTION REQUIRED
# ===================================================================
raw_actions = summary.get("action_required", [])

# Normalize to clean list
if isinstance(raw_actions, str):
    actions = [raw_actions.strip()] if raw_actions.strip() else []
elif isinstance(raw_actions, list):
    actions = [str(a).strip() for a in raw_actions if str(a).strip()]
else:
    actions = []

# These phrases mean "we're done"
resolved_keywords = [
    "no further action", "no action required", "no specific action",
    "claim approved", "payment will be processed", "all set", "nothing further"
]

claim_is_resolved = (
    len(actions) == 0 or
    any(any(k in action.lower() for k in resolved_keywords) for action in actions)
)

if claim_is_resolved:
    # Fully approved → clean positive message
    styled_success("Claim Approved", "Payment will be processed within 5-7 business days.")
    styled_info("No Action Required", "No further action required from patient")
else:
    # Something needs to be done → show the section
    st.subheader("📋 Action Required")
    for action in actions:
        action_low = action.lower()
        if any(k in action_low for k in ["contact", "call", "appeal", "submit", "clarification", "provide", "missing", "upload"]):
            styled_info("Action Item", action)
        else:
            styled_error("Action Required", action)

# ===================================================================
# Bottom navigation
# ===================================================================
st.write("---")
st.page_link("pages/1_Upload_Claim.py", label="🔄 Process Another Claim")