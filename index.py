import google.generativeai as genai
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template
from io import BytesIO
from PIL import Image
import requests

app = Flask(__name__,template_folder='./',static_folder='./')
CORS(app)

genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-pro-vision')

@app.route('/')
def index():
    print('gettting')
    return render_template('processImage.html')

@app.route('/processImage',methods=['POST'])
def process_image():
    req=request.get_json()
    query = req.get('query','')
    url = req.get('url','')
    response = requests.get(url)
    try:
        response.raise_for_status()
        image_bytesio = BytesIO(response.content)
        img = Image.open(image_bytesio)
        if len(query):
            response = model.generate_content([f"Generate response in html div format for the user query: {query}",img])
            response.resolve()
            return jsonify({'response':response.text})
        else:
            response = model.generate_content(img)
            response.resolve()
            return jsonify({'response':response.text})
    except Exception:
        response = model.generate_content(query)
        return jsonify({'response':response.text})

if __name__ == "__main__":
    app.run(debug=True)