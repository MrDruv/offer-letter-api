@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # 1. Get data from your AI Agent
    data = request.json 
    
    # 2. Render the HTML with ALL professional placeholders
    rendered_html = render_template('offer_letter.html', 
                                    name=data.get('name'),
                                    location=data.get('location'),
                                    title=data.get('title'),
                                    department=data.get('department'),
                                    level=data.get('level'),
                                    salary=data.get('salary'),
                                    bonus=data.get('bonus'),
                                    equity=data.get('equity'),
                                    current_date=datetime.now().strftime("%B %d, %Y"))
    
    # 3. Convert HTML string to PDF in memory
    pdf_file = io.BytesIO()
    # Note: If you have a base_url, WeasyPrint can find local images/CSS
    HTML(string=rendered_html).write_pdf(target=pdf_file)
    pdf_file.seek(0)
    
    return send_file(pdf_file, 
                     mimetype='application/pdf',
                     download_name=f"Offer_{data.get('name', 'Candidate')}.pdf", 
                     as_attachment=True)
