from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'

load_dotenv()

def verify_token(token):
    if token == os.environ.get('BEARER_TOKEN'):
        return True
    else:
        return False

@app.route('/', methods=['GET'])
def home():
    return "WHISPERING..."


@app.route('/whisper', methods=['POST'])
def whisper():
    if 'Authorization' not in request.headers:
        return jsonify({'error': 'Missing Token'}), 401

    token = request.headers['Authorization'].split(' ')[1]

    if not verify_token(token):
        return jsonify({'error': 'Invalid Token'}), 401
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'No selected audio file'}), 400

    filename = request.form.get('filename')
    saved_file=os.path.join(UPLOAD_FOLDER,filename)

    try:
        audio_file.save(saved_file)
        
        with open(saved_file, 'rb') as file:
            client = OpenAI()
            translation = client.audio.translations.create(
                model="whisper-1", 
                file=file
            )
        
        os.remove(saved_file)

        return jsonify({'success': translation.text}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=8080)
