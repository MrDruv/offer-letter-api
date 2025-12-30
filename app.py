from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from pydantic import BaseModel
from typing import Dict, List
import io
import os
from datetime import datetime
import traceback

app = Flask(__name__, static_folder='static')

class OfferLetterRequest(BaseModel):
    company_info: Dict
    candidate_info: Dict
    role_info: Dict
    compensation_info: Dict
    template_text: str
    joining_date: str
    compliance_result: Dict

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Offer Letter API Live! POST to /generate"})

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    try:
        print("Received request:", request.json)
        data = request.json
        validated = OfferLetterRequest(**data)
        
        filename = f"offer-{uuid.uuid4().hex[:8]}.pdf"
        pdf_buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Header
        story.append(Paragraph(f"<b>{validated.company_info['name']}</b>", styles['Heading1']))
        story.append(Spacer(1, 20))
        story.append(Paragraph(f"Dear {validated.candidate_info['name']},", styles['Heading2']))
        
        # Compensation
        ctc_lakhs = validated.compensation_info['total_ctc'] / 100000
        story.append(Paragraph(f"<b>Total CTC: ₹{ctc_lakhs:.1f} Lakhs</b>", styles['Heading3']))
        story.append(Paragraph(f"Position: {validated.role_info['title']}", styles['Normal']))
        story.append(Paragraph(f"Location: {validated.role_info['location']}", styles['Normal']))
        story.append(Paragraph(f"Joining: {validated.joining_date}", styles['Normal']))
        
        doc.build(story)
        pdf_buffer.seek(0)
        
        os.makedirs('static', exist_ok=True)
        filepath = f'static/{filename}'
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        download_url = f"https://{request.host}/static/{filename}"
        
        return jsonify({
            "status": "success",
            "download_url": download_url,
            "filename": filename
        })
    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": str(e)}), 400

@app.route('/static/<filename>')
def serve_pdf(filename):
    try:
        return send_file(f'static/{filename}')
    except:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
