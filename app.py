
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import docx
import fitz  # PyMuPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Basit Türkçe yazım kontrol fonksiyonu
def basic_spell_check(text):
    mistakes = []
    if "calisma" in text:
        mistakes.append('“calisma” → “çalışma”')
    if "  " in text:
        mistakes.append('İki boşluk tespit edildi')
    if not text.strip().endswith((".", "!", "?")):
        mistakes.append("Cümle sonu noktalama eksik")
    return mistakes

def extract_text_from_pdf(path):
    text = ""
    doc = fitz.open(path)
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "
".join([para.text for para in doc.paragraphs])

def extract_text_from_image(path):
    return pytesseract.image_to_string(Image.open(path), lang='tur')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'pdf':
                content = extract_text_from_pdf(filepath)
            elif ext == 'docx':
                content = extract_text_from_docx(filepath)
            elif ext in ['jpg', 'jpeg', 'png']:
                content = extract_text_from_image(filepath)
            else:
                content = ""

            errors = basic_spell_check(content)

    return render_template('panel.html', errors=errors)

if __name__ == '__main__':
    app.run(debug=True)
