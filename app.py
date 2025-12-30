from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from pydantic import BaseModel
from typing import Dict, List
import io
import uuid
import os
from datetime import datetime, timedelta

app = Flask(__name__)

class OfferLetterRequest(BaseModel):
    company_info: Dict
    candidate_info: Dict
    role_info: Dict
    compensation_info: Dict
    template_text: str
    joining_date: str
    compliance_result: Dict

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    data = request.json
    validated = OfferLetterRequest(**data)
    
    filename = f"offer-letter-{validated.candidate_info['name'].replace(' ', '-')}-{validated.role_info['title'].replace(' ', '-')}.pdf"
    pdf_buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Header
    story.append(Paragraph(f"<b>{validated.company_info['name']}</b><br/>{validated.company_info.get('address', '')}<br/>Date: {datetime.now().strftime('%d %B %Y')}", styles['Heading1']))
    story.append(Spacer(1, 20))
    
    # Salutation
    story.append(Paragraph(f"Dear {validated.candidate_info['name']},", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Role Table
    role_data = [
        ['Position', validated.role_info['title']],
        ['Department', validated.role_info.get('department', 'Engineering')],
        ['Level', validated.role_info.get('level', 'Senior')],
        ['Location', validated.role_info['location']]
    ]
    table = Table(role_data)
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey), ('GRID', (0,0), (-1,-1), 1, colors.black)]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Compensation
    ctc_lakhs = validated.compensation_info['total_ctc'] / 100000
    story.append(Paragraph(f"<b>Total CTC: ₹{ctc_lakhs:.1f} Lakhs/annum</b>", styles['Heading3']))
    story.append(Paragraph(f"Joining Date: {validated.joining_date}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Benefits
    benefits = validated.compliance_result.get('benefits', [])
    story.append(Paragraph("Benefits:", styles['Heading3']))
    for benefit in benefits:
        story.append(Paragraph(f"• {benefit}", styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("Sincerely,<br/><b>HR Manager</b>", styles['Heading3']))
    
    doc.build(story)
    pdf_buffer.seek(0)
    
    os.makedirs('static', exist_ok=True)
    filepath = f'static/{filename}'
    with open(filepath, 'wb') as f:
        f.write(pdf_buffer.getvalue())
    
    download_url = f"https://{request.host}/static/{filename}"
    return jsonify({"download_url": download_url})

@app.route('/static/<filename>')
def serve_pdf(filename):
    return send_file(f'static/{filename}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
