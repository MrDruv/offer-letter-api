from flask import Flask, request, jsonify, send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pydantic import BaseModel
from typing import Dict
import io
import os
import uuid
import traceback

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Ensure static folder exists immediately on start
os.makedirs('static', exist_ok=True)

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "live",
        "message": "Offer Letter API Ready!",
        "endpoint": "/generate (POST)"
    })

@app.route('/generate', methods=['POST'])
def generate_offer_letter():
    try:
        data = request.get_json()
        
        # Validation
        required = ['company_info', 'candidate_info', 'role_info', 'compensation_info']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing {field}"}), 400
        
        # Setup PDF
        filename = f"offer-{uuid.uuid4().hex[:8]}.pdf"
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Content Construction
        company_name = data['company_info'].get('name', 'Company')
        story.append(Paragraph(f"<b>{company_name}</b>", styles['Title']))
        story.append(Spacer(1, 20))
        
        candidate_name = data['candidate_info'].get('name', 'Candidate')
        story.append(Paragraph(f"Dear {candidate_name},", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        role_title = data['role_info'].get('title', 'Position')
        location = data['role_info'].get('location', 'Location')
        total_ctc = data['compensation_info'].get('total_ctc', 0)
        ctc_lakhs = total_ctc / 100000
        
        story.append(Paragraph(f"<b>Position:</b> {role_title}", styles['Heading3']))
        story.append(Paragraph(f"<b>Location:</b> {location}", styles['Heading3']))
        story.append(Paragraph(f"<b>Total CTC:</b> ₹{ctc_lakhs:.1f} Lakhs/annum", styles['Heading2']))
        story.append(Paragraph(f"<b>Joining Date:</b> {data.get('joining_date', 'TBD')}", styles['Normal']))
        
        compliance = data.get('compliance_result', {})
        benefits = compliance.get('benefits', [])
        if benefits:
            story.append(Paragraph("<b>Benefits:</b>", styles['Heading3']))
            for benefit in benefits:
                story.append(Paragraph(f"• {benefit}", styles['Normal']))
        
        story.append(Spacer(1, 30))
        story.append(Paragraph("Sincerely,<br/><b>HR Manager</b>", styles['Heading2']))
        
        doc.build(story)
        pdf_buffer.seek(0)
        
        # Save to static
        filepath = os.path.join('static', filename)
        with open(filepath, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        # Construct URL (Ensure this matches your Render service name)
        # Suggestion: Use request.host_url to make it dynamic
        base_url = request.host_url.rstrip('/')
        download_url = f"{base_url}/static/{filename}"
        
        return jsonify({
            "status": "success",
            "download_url": download_url,
            "filename": filename,
            "preview": f"Generated for {candidate_name} - {role_title}"
        })
    
    except Exception as e:
        return jsonify({"status": "error", "error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/static/<filename>')
def serve_pdf(filename):
    filepath = os.path.join('static', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
