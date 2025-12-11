# streamlit_app/utils/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime

class PatientLetterPDF:
    """Generate professional PDF patient letters"""
    
    @staticmethod
    def generate_pdf(letter_content: str, patient_name: str, claim_id: str) -> bytes:
        """
        Generate PDF from patient letter content
        
        Args:
            letter_content: The full patient letter text
            patient_name: Patient name for filename
            claim_id: Claim ID for filename
            
        Returns:
            PDF bytes
        """
        # Create a byte stream for the PDF
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create story (content)
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=6,
            alignment=TA_LEFT
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_LEFT,
            leading=14
        )
        
        footer_style = ParagraphStyle(
            'CustomFooter',
            parent=styles['Normal'],
            fontSize=8,
            spaceBefore=20,
            alignment=TA_CENTER
        )
        
        # Add header with logo placeholder
        story.append(Paragraph("MediSure Health Insurance", title_style))
        story.append(Paragraph("Claims Processing Department", styles['Heading3']))
        story.append(Spacer(1, 20))
        
        # Add current date
        current_date = datetime.now().strftime("%B %d, %Y")
        story.append(Paragraph(f"Date: {current_date}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Process letter content line by line
        lines = letter_content.split('\n')
        
        for line in lines:
            if line.strip():
                # Check for headings
                if line.strip().startswith("RE:") or line.strip().startswith("Dear"):
                    story.append(Paragraph(line.strip(), header_style))
                elif line.strip().startswith("Claim Details:") or line.strip().startswith("Next Steps:"):
                    story.append(Paragraph(line.strip(), header_style))
                    story.append(Spacer(1, 10))
                elif "•" in line or line.strip().startswith("1.") or line.strip().startswith("2."):
                    # Handle bullet points
                    story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{line.strip()}", body_style))
                else:
                    # Regular body text
                    story.append(Paragraph(line.strip(), body_style))
                story.append(Spacer(1, 6))
        
        # Add footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("This is an official document from MediSure Health Insurance", footer_style))
        story.append(Paragraph("For questions, call 1-800-MEDISURE or visit www.medisure.com", footer_style))
        story.append(Paragraph(f"Document ID: {claim_id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    @staticmethod
    def generate_simple_pdf(letter_content: str) -> bytes:
        """
        Simple PDF generation for quick demo
        """
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        # Set up PDF
        c.setFont("Helvetica-Bold", 14)
        c.drawString(100, 750, "MediSure Health Insurance")
        c.setFont("Helvetica", 10)
        c.drawString(100, 735, "Claims Processing Department")
        
        # Draw line
        c.line(100, 730, 500, 730)
        
        # Add date
        current_date = datetime.now().strftime("%B %d, %Y")
        c.drawString(400, 710, f"Date: {current_date}")
        
        # Add letter content
        c.setFont("Helvetica", 10)
        y_position = 680
        
        lines = letter_content.split('\n')
        for line in lines:
            if y_position < 100:  # New page if needed
                c.showPage()
                c.setFont("Helvetica", 10)
                y_position = 750
            
            if line.strip():
                # Handle bullet points
                if line.strip().startswith("•"):
                    c.drawString(120, y_position, line.strip())
                else:
                    c.drawString(100, y_position, line.strip())
                y_position -= 15
        
        # Add footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(100, 50, "Official Document - MediSure Health Insurance")
        c.drawString(100, 35, "1-800-MEDISURE | www.medisure.com")
        
        c.save()
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes