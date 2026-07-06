from flask import Flask, render_template , request , jsonify , redirect, url_for
from PyPDF2 import PdfReader
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL , SUPABASE_KEY)

app = Flask(__name__)

print(">>>>>>>> THIS IS THE CORRECT APP.PY <<<<<<<<")
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == 'GET':
        return redirect(url_for('home'))
    
    job_description = request.form.get('job_description', '')
    file = request.files.get('file')

    if not job_description:
        return jsonify({"error": "Job description is empty"}), 400

    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded"}), 400
    
    reader = PdfReader(file)
    text = ""

    
    for page in reader.pages:
        text += page.extract_text()

    text = text.lower()
    job_description = job_description.lower()

    matchWord = []
    unMatch_word = []

    for word in set(job_description.split()):
        if word in text:
            matchWord.append(word)
        else:
            unMatch_word.append(word)

    
    total_words = len(matchWord) + len(unMatch_word)

    score = (len(matchWord) / total_words) * 100        

    user_data = {
        "Score" : score,
        "KeyWord_exists" : matchWord,
        "KeyWord_not_exist" : unMatch_word
    }

    supabase.table("ats_results").insert({
        "job_description" : job_description,
        "score" : score,
        "matched_keywords": matchWord,
        "missing_keywords": unMatch_word
    }).execute()
    return jsonify(user_data)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)