from flask import Flask, request, render_template, jsonify
import re
import PyPDF2
import logging
from dotenv import load_dotenv
import google.generativeai as genai

app = Flask(__name__) 

genai.configure(api_key="{API_KEY}")
model = genai.GenerativeModel("gemini-1.5-flash")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def clean_text(text):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?]', '', text)
    return text.lower()


def get_gemini_answer(text, question):
    try:
        user_message = text + "\n" + question
        response = model.generate_content(user_message)
        gemini_response = response.text
        logger.debug(f"Model yanıtı: {gemini_response}")
        return gemini_response
    except Exception as e:
        logger.error(f"Hata oluştu: {e}")
        return f"Hata oluştu: {str(e)}"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    file = request.files['pdf_file']
    if file:
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            cleaned_text = clean_text(text)
            logger.debug(f"Temizlenmiş metin: {cleaned_text[:500]}")
            return render_template('display_text.html', text=cleaned_text)
        except Exception as e:
            logger.error(f"PDF işleme hatası: {e}")
            return f"Hata oluştu: {str(e)}"
    return "Hiçbir dosya seçilmedi!"


@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form['question']
    context = request.form['context']
    logger.debug(f"Soru: {question}")
    logger.debug(f"Metin: {context[:500]}")
    answer = get_gemini_answer(context, question)
    return jsonify({"question": question, "answer": answer})

if __name__ == '__main__':
    app.run(debug=True)
