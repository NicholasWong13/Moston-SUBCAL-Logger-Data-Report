from flask import Flask, request, jsonify, send_file, render_template
from report_generation import generate_pdf_report

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-report', methods=['POST'])
def generate_report():
    try:
        pdf_file_path = generate_pdf_report()
        if pdf_file_path:
            return send_file(pdf_file_path, as_attachment=True)
        else:
            return jsonify({"message": "No matching files found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
