import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from services.chat import chat_with_rag
from ingest import ingest_pdf

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB Limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Ingestion logic
            ingest_pdf(filepath)
            return jsonify({"message": f"Successfully ingested {filename}", "filename": filename})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Invalid file type. Only PDFs allowed."}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_query = data.get("query")
    
    if not user_query:
        return jsonify({"error": "Empty query"}), 400

    try:
        # gpt-4o-mini + Pinecone logic
        answer = chat_with_rag(user_query)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()