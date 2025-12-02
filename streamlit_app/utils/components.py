"""
Custom styled components for MediSure UI
BOLD, VIBRANT colors that are easy to read
"""

import streamlit as st
import os


def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass  # fails silently if file missing


def styled_success(title: str, message: str = ""):
    """BOLD GREEN success box"""
    st.markdown(f"""
        <div style="
            background-color: #22c55e;
            border-left: 8px solid #15803d;
            border-radius: 8px;
            padding: 18px 22px;
            margin: 12px 0;
        ">
            <span style="color: #ffffff; font-size: 18px; font-weight: 700;">
                ✅ {title}
            </span>
            {f'<p style="color: #ffffff; margin: 10px 0 0 0; font-size: 15px; font-weight: 500;">{message}</p>' if message else ''}
        </div>
    """, unsafe_allow_html=True)


def styled_warning(title: str, message: str = ""):
    """BOLD ORANGE warning box"""
    st.markdown(f"""
        <div style="
            background-color: #f59e0b;
            border-left: 8px solid #d97706;
            border-radius: 8px;
            padding: 18px 22px;
            margin: 12px 0;
        ">
            <span style="color: #ffffff; font-size: 18px; font-weight: 700;">
                ⚠️ {title}
            </span>
            {f'<p style="color: #ffffff; margin: 10px 0 0 0; font-size: 15px; font-weight: 500;">{message}</p>' if message else ''}
        </div>
    """, unsafe_allow_html=True)


def styled_error(title: str, message: str = ""):
    """BOLD RED error box"""
    st.markdown(f"""
        <div style="
            background-color: #ef4444;
            border-left: 8px solid #b91c1c;
            border-radius: 8px;
            padding: 18px 22px;
            margin: 12px 0;
        ">
            <span style="color: #ffffff; font-size: 18px; font-weight: 700;">
                ❌ {title}
            </span>
            {f'<p style="color: #ffffff; margin: 10px 0 0 0; font-size: 15px; font-weight: 500;">{message}</p>' if message else ''}
        </div>
    """, unsafe_allow_html=True)


def styled_info(title: str, message: str = ""):
    """BOLD BLUE info box"""
    st.markdown(f"""
        <div style="
            background-color: #3b82f6;
            border-left: 8px solid #1d4ed8;
            border-radius: 8px;
            padding: 18px 22px;
            margin: 12px 0;
        ">
            <span style="color: #ffffff; font-size: 18px; font-weight: 700;">
                ℹ️ {title}
            </span>
            {f'<p style="color: #ffffff; margin: 10px 0 0 0; font-size: 15px; font-weight: 500;">{message}</p>' if message else ''}
        </div>
    """, unsafe_allow_html=True)


def decision_card(decision: str, reason: str, confidence: float = None):
    """
    Final claim decision card with BOLD colors
    decision: APPROVE, REJECT, or MANUAL_REVIEW
    """
    styles = {
        "APPROVE": {
            "bg": "#22c55e",
            "border": "#15803d", 
            "text": "#ffffff",
            "icon": "✅"
        },
        "REJECT": {
            "bg": "#ef4444",
            "border": "#b91c1c",
            "text": "#ffffff",
            "icon": "❌"
        },
        "MANUAL_REVIEW": {
            "bg": "#f59e0b",
            "border": "#d97706",
            "text": "#ffffff",
            "icon": "⚠️"
        }
    }
    
    style = styles.get(decision, styles["MANUAL_REVIEW"])
    
    confidence_html = ""
    if confidence is not None:
        confidence_html = f'<p style="color: {style["text"]}; margin: 8px 0 0 0; font-size: 14px; font-weight: 500;">Confidence: {confidence:.0%}</p>'
    
    st.markdown(f"""
        <div style="
            background-color: {style['bg']};
            border-left: 8px solid {style['border']};
            border-radius: 10px;
            padding: 22px 26px;
            margin: 16px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3 style="color: {style['text']}; margin: 0 0 12px 0; font-size: 22px; font-weight: 700;">
                {style['icon']} Final Decision: {decision}
            </h3>
            <p style="color: {style['text']}; margin: 0; font-size: 16px; font-weight: 500;">
                <strong>Reason:</strong> {reason}
            </p>
            {confidence_html}
        </div>
    """, unsafe_allow_html=True)


def summary_card(claim_id: str, patient: str, member_id: str, plan: str, amount: float, decision: str, reasons: str):
    """Executive summary card with BOLD colors"""
    
    # Choose background based on decision
    if decision == "APPROVE":
        bg_color = "#dcfce7"
        border_color = "#22c55e"
        text_color = "#166534"
        icon = "✅"
    elif decision == "REJECT":
        bg_color = "#fee2e2"
        border_color = "#ef4444"
        text_color = "#991b1b"
        icon = "❌"
    else:  # MANUAL_REVIEW
        bg_color = "#fef3c7"
        border_color = "#f59e0b"
        text_color = "#92400e"
        icon = "⚠️"
    
    st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border: 3px solid {border_color};
            border-radius: 12px;
            padding: 22px;
            margin: 16px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h4 style="color: {text_color}; margin: 0 0 14px 0; font-size: 20px; font-weight: 700;">
                📋 Executive Summary
            </h4>
            <p style="color: {text_color}; margin: 8px 0; font-size: 17px; font-weight: 700;">
                {icon} CLAIM {claim_id} — {decision}
            </p>
            <p style="color: {text_color}; margin: 6px 0; font-size: 15px; font-weight: 600;">
                Patient: {patient} (Member ID: {member_id}) Plan: {plan}
            </p>
            <p style="color: {text_color}; margin: 6px 0; font-size: 15px; font-weight: 600;">
                Total Amount: ${amount:,.2f}
            </p>
            <p style="color: {text_color}; margin: 12px 0 0 0; font-size: 15px; font-weight: 600;">
                <strong>Decision:</strong> {decision}. {reasons}
            </p>
        </div>
    """, unsafe_allow_html=True)


def section_header(title: str, icon: str = "📌"):
    """Bold section header"""
    st.markdown(f"""
        <h2 style="
            color: #1e3a5f;
            font-size: 24px;
            font-weight: 700;
            margin: 20px 0 10px 0;
            padding-bottom: 8px;
            border-bottom: 3px solid #3b82f6;
        ">
            {icon} {title}
        </h2>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, color: str = "#3b82f6"):
    """Display a metric in a colored card"""
    st.markdown(f"""
        <div style="
            background-color: #f8fafc;
            border-left: 5px solid {color};
            border-radius: 8px;
            padding: 14px 18px;
            margin: 8px 0;
        ">
            <p style="color: #64748b; margin: 0; font-size: 13px; font-weight: 600; text-transform: uppercase;">
                {label}
            </p>
            <p style="color: #1e293b; margin: 4px 0 0 0; font-size: 20px; font-weight: 700;">
                {value}
            </p>
        </div>
    """, unsafe_allow_html=True)