import google.generativeai as genai
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template

app = Flask(__name__,template_folder='./',static_folder='./')
CORS(app)

genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def index():
  return render_template('processText.html')

@app.route('/processText',methods=['POST'])
def process_text():
  req=request.get_json()
  query = req.get('query','')
  context = req.get('context','')
  if len(context):
    response = model.generate_content(f"Answer {query} based on {context}")
    return jsonify({'response':response.text})
  else:
    response = model.generate_content(query)
    return jsonify({'response':response.text})

if __name__ == "__main__":
  app.run(debug=True)