import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
import os
from datetime import datetime
from typing import Dict, Any, Optional
import tempfile

class PDFReportGenerator:
    """Generate formatted PDF reports with NBP company branding"""
    
    def __init__(self):
        # Use the correct logo path
        self.logo_path = r"F:\Baraaq\Test Projects\Dan - Sales Pitch Improver\unnamed (2).jpg"
        self.company_name = "NBP"
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Company header style
        self.company_style = ParagraphStyle(
            'CompanyHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#ff0000'),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#ff0000'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        )
        
        # Subsection style
        self.subsection_style = ParagraphStyle(
            'Subsection',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=HexColor('#ff0000'),
            spaceAfter=8,
            spaceBefore=12
        )
    
    def _add_header_footer(self, canvas_obj, doc):
        """Add header with logo and footer with page numbers"""
        canvas_obj.saveState()
        
        # Header with logo
        if os.path.exists(self.logo_path):
            try:
                # Add logo to header
                canvas_obj.drawImage(self.logo_path, 50, doc.height + doc.topMargin - 60, width=1.5*inch, height=0.8*inch)
            except Exception as e:
                st.warning(f"Could not add logo: {str(e)}")
        
        # Company name in header
        canvas_obj.setFont("Helvetica-Bold", 16)
        canvas_obj.setFillColor(HexColor('#ff0000'))
        canvas_obj.drawString(250, doc.height + doc.topMargin - 30, self.company_name)
        
        # Footer with page number
        canvas_obj.setFont("Helvetica", 10)
        canvas_obj.setFillColor(colors.grey)
        canvas_obj.drawString(50, 30, f"Page {doc.page}")
        
        # Footer line
        canvas_obj.setStrokeColor(HexColor('#ff0000'))
        canvas_obj.setLineWidth(1)
        canvas_obj.line(50, 50, doc.width + doc.leftMargin + doc.rightMargin - 50, 50)
        
        canvas_obj.restoreState()
    
    def _format_section(self, title: str, content: str) -> list:
        """Format a section with title and content"""
        elements = []
        
        # Add section title
        elements.append(Paragraph(title, self.section_style))
        
        # Add content
        if content:
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), self.body_style))
                    elements.append(Spacer(1, 6))
        
        return elements
    
    def _format_key_points(self, points: list) -> list:
        """Format key points as bulleted list"""
        elements = []
        
        for point in points:
            if point.strip():
                bullet_text = f"• {point.strip()}"
                elements.append(Paragraph(bullet_text, self.body_style))
                elements.append(Spacer(1, 4))
        
        return elements
    
    def generate_ai_report_pdf(self, report_data: Dict[str, Any], prospect_info: Dict[str, Any]) -> str:
        """Generate a formatted PDF report from AI report data"""
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=100
        )
        
        # Build story (content)
        story = []
        
        # Title page
        story.append(Paragraph("AI Sales Report", self.company_style))
        story.append(Spacer(1, 20))
        
        # Prospect information table
        prospect_data = [
            ["Company", prospect_info.get('company_name', 'N/A')],
            ["Industry", prospect_info.get('industry', 'N/A')],
            ["Primary Contact", prospect_info.get('primary_contact', 'N/A')],
            ["Meeting Objective", prospect_info.get('meeting_objective', 'N/A')],
            ["Report Generated", datetime.now().strftime("%B %d, %Y at %I:%M %p")]
        ]
        
        prospect_table = Table(prospect_data, colWidths=[2*inch, 4*inch])
        prospect_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#ff0000')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#ff0000')),
        ]))
        
        story.append(prospect_table)
        story.append(PageBreak())
        
        # Parse and format the AI report content
        report_content = report_data.get('report', '')
        
        # Split content into sections
        sections = self._parse_report_sections(report_content)
        
        for section_title, section_content in sections:
            if section_title and section_content:
                story.extend(self._format_section(section_title, section_content))
                story.append(Spacer(1, 12))
        
        # Add report metadata
        story.append(PageBreak())
        story.append(Paragraph("Report Details", self.section_style))
        
        metadata_data = [
            ["AI Model Used", report_data.get('model_used', 'N/A')],
            ["Tokens Used", str(report_data.get('tokens_used', 0))],
            ["Generation Time", report_data.get('generation_time', 'N/A')],
            ["Generated By", "Hyper Baraaq AI System"]
        ]
        
        metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        
        story.append(metadata_table)
        
        # Build PDF with header and footer
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return pdf_path
    
    def _parse_report_sections(self, content: str) -> list:
        """Parse AI report content into sections"""
        sections = []
        
        # Common section headers to look for
        section_headers = [
            "Executive Summary",
            "Company Analysis", 
            "Meeting Strategy",
            "Key Talking Points",
            "Value Proposition",
            "Questions to Ask",
            "Next Steps",
            "Risk Assessment"
        ]
        
        lines = content.split('\n')
        current_section = ""
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_header = False
            for header in section_headers:
                if header.lower() in line.lower() and line.endswith(':'):
                    # Save previous section
                    if current_section and current_content:
                        sections.append((current_section, '\n'.join(current_content)))
                    
                    # Start new section
                    current_section = line.rstrip(':')
                    current_content = []
                    is_header = True
                    break
            
            if not is_header and current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def generate_script_pdf(self, script_data: Dict[str, Any], prospect_info: Dict[str, Any]) -> str:
        """Generate a formatted PDF for sales scripts"""
        
        # Create temporary file for PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        # Create PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=100,
            bottomMargin=100
        )
        
        # Build story (content)
        story = []
        
        # Title page
        script_type = script_data.get('script_type', 'Sales Script')
        story.append(Paragraph(f"{script_type}", self.company_style))
        story.append(Spacer(1, 20))
        
        # Prospect information
        prospect_data = [
            ["Company", prospect_info.get('company_name', 'N/A')],
            ["Industry", prospect_info.get('industry', 'N/A')],
            ["Script Type", script_type],
            ["Tone", script_data.get('tone', 'N/A')],
            ["Generated", datetime.now().strftime("%B %d, %Y at %I:%M %p")]
        ]
        
        prospect_table = Table(prospect_data, colWidths=[2*inch, 4*inch])
        prospect_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#ff0000')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, HexColor('#ff0000')),
        ]))
        
        story.append(prospect_table)
        story.append(PageBreak())
        
        # Script content
        script_content = script_data.get('script', '')
        story.append(Paragraph("Script Content", self.section_style))
        story.append(Spacer(1, 12))
        
        # Format script content
        paragraphs = script_content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), self.body_style))
                story.append(Spacer(1, 8))
        
        # Build PDF with header and footer
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        
        return pdf_path

def download_pdf_report(report_data: Dict[str, Any], prospect_info: Dict[str, Any], report_type: str = "ai_report"):
    """Generate and provide download link for PDF report"""
    
    try:
        generator = PDFReportGenerator()
        
        if report_type == "ai_report":
            pdf_path = generator.generate_ai_report_pdf(report_data, prospect_info)
            filename = f"NBP_AI_Report_{prospect_info.get('company_name', 'Prospect')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        else:
            pdf_path = generator.generate_script_pdf(report_data, prospect_info)
            filename = f"NBP_Sales_Script_{prospect_info.get('company_name', 'Prospect')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # Check if PDF was created successfully
        if not os.path.exists(pdf_path):
            st.error("❌ PDF file was not created")
            return None, None
        
        # Read the PDF file
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Clean up temporary file
        try:
            os.unlink(pdf_path)
        except Exception as e:
            st.warning(f"Could not delete temporary file: {str(e)}")
        
        # Verify PDF has content
        if len(pdf_bytes) < 1000:  # PDF should be at least 1KB
            st.error("❌ Generated PDF appears to be empty or corrupted")
            return None, None
        
        # Debug info
        st.success(f"✅ PDF generated successfully: {filename} ({len(pdf_bytes)} bytes)")
        
        return pdf_bytes, filename
        
    except Exception as e:
        st.error(f"❌ Error generating PDF: {str(e)}")
        import traceback
        st.error(f"Full error details: {traceback.format_exc()}")
        return None, None

def test_pdf_generation():
    """Test PDF generation with sample data"""
    try:
        test_report_data = {
            "report": "This is a test report.\n\nExecutive Summary: Test summary.\n\nCompany Analysis: Test analysis.",
            "model_used": "gpt-4",
            "tokens_used": 150,
            "generation_time": datetime.now().isoformat()
        }
        
        test_prospect_info = {
            "company_name": "Test Company",
            "industry": "Technology",
            "primary_contact": "John Doe",
            "meeting_objective": "Sales Discussion"
        }
        
        pdf_bytes, filename = download_pdf_report(test_report_data, test_prospect_info, "ai_report")
        
        if pdf_bytes:
            st.success("✅ Test PDF generation successful!")
            return True
        else:
            st.error("❌ Test PDF generation failed!")
            return False
            
    except Exception as e:
        st.error(f"Test failed: {str(e)}")
        return False 