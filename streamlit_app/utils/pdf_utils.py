# streamlit_app/utils/pdf_utils.py (REPLACE with HTML version)
import streamlit as st
import base64
from datetime import datetime

def create_html_download_button(letter_content: str, patient_name: str = "Patient", claim_id: str = "Unknown"):
    """
    Create an HTML file download button (users can print as PDF)
    No external dependencies needed!
    """
    if not letter_content or letter_content.strip() == "" or letter_content == "{}":
        return
    
    try:
        # Create HTML content
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MediSure Claim {claim_id} - {patient_name}</title>
    <style>
        @page {{
            margin: 0.5in;
        }}
        body {{
            font-family: 'Helvetica', 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 20px;
        }}
        .letterhead {{
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 15px;
            margin-bottom: 30px;
        }}
        .letterhead h1 {{
            color: #1e3a8a;
            margin: 0;
        }}
        .letterhead h3 {{
            color: #3b82f6;
            margin: 5px 0 0 0;
        }}
        .date {{
            text-align: right;
            color: #666;
            font-style: italic;
        }}
        .content {{
            white-space: pre-line;
            font-size: 12pt;
        }}
        .content strong {{
            font-weight: bold;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ccc;
            font-size: 10pt;
            color: #666;
        }}
        @media print {{
            .no-print {{
                display: none;
            }}
            body {{
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="letterhead">
        <h1>🏥 MediSure Health Insurance</h1>
        <h3>Claims Processing Department</h3>
        <div class="date">{datetime.now().strftime("%B %d, %Y")}</div>
    </div>
    
    <div class="content">
        {letter_content}
    </div>
    
    <div class="footer">
        <p><strong>Official Document</strong> - MediSure Health Insurance</p>
        <p>📞 1-800-MEDISURE | 📧 claims@medisure.com | 🌐 www.medisure.com</p>
        <p>Document ID: {claim_id} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p class="no-print">💡 <em>Tip: Print this page (Ctrl+P) to save as PDF</em></p>
    </div>
</body>
</html>
"""
        
        # Encode HTML for download
        b64 = base64.b64encode(html_content.encode()).decode()
        
        # Create download button
        clean_name = "".join(c for c in patient_name if c.isalnum() or c in (" ", "_")).rstrip()
        filename = f"MediSure_Claim_{claim_id}_{clean_name}.html"
        
        # Create HTML with download link
        download_html = f'''
        <a href="data:text/html;base64,{b64}" download="{filename}" 
           style="display: inline-block; padding: 10px 20px; background-color: #3b82f6; 
                  color: white; text-decoration: none; border-radius: 5px; 
                  margin: 10px 0; font-weight: bold; text-align: center;">
           📄 Download Patient Letter (HTML)
        </a>
        <p style="color: #666; font-size: 12px; margin-top: 5px;">
           <em>Open in browser and print (Ctrl+P) to save as PDF</em>
        </p>
        '''
        
        st.markdown(download_html, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Download creation failed: {str(e)}")
        # Fallback: Show copy button
        st.text_area("Copy letter text:", letter_content, height=200)