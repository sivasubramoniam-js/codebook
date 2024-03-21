import google.generativeai as genai
from flask_cors import CORS
from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__,template_folder='./',static_folder='./')
CORS(app)

genai.configure(api_key='API_KEY')
model = genai.GenerativeModel('gemini-pro')

def create_table(query, table_name):
  conn = sqlite3.connect('database.db')
  model_resp = model.generate_content(f"generate sql query for {query} without any additional text. i just need only the query.")
  restructured_query = model_resp.text.replace('`',"'").replace('sql','').replace("'''","")
  cursor = conn.cursor()
  cursor.execute(restructured_query)
  conn.commit()

def query_table(query, table_name):
  conn = sqlite3.connect('database.db')
  cursor = conn.cursor()
  cursor2 = conn.cursor()
  table_structure_query = f"PRAGMA table_info({table_name})"
  cursor.execute(table_structure_query)
  table_structure = cursor.fetchone()
  tab_structure = table_structure[0]

  model_resp = model.generate_content(f"considering the table structure {tab_structure}, generate sql query for {query} without any additional text")
  restructured_query = model_resp.text.replace('`',"'").replace('sql','').replace("'''","")
  cursor2.execute(restructured_query)
  filtered_res = cursor2.fetchall()
  result = []
  is_insert_query = model.generate_content(f"what type of query this is '{restructured_query}', insert or update or delete")
  try:
    if is_insert_query.text[:6] in ['Insert', 'insert', 'Update', 'update', 'Delete', 'delete']:
      conn.commit()
      cursor3 = conn.cursor()
      cursor3.execute(f'SELECT * FROM {table_name}')
      result = cursor3.fetchall()
    else:
      for res in filtered_res:
        result.append(res)
  except:
    conn.close()
  html_resp = model.generate_content(f"considering table structure {tab_structure} and table values {result} in the form of dictionary, generate html table showing all the table records with all the fields which can be appended to the html body element. Don't generate any additional text. If the {query} is to exclude any columns, then exclude those columns from the html table as well.")
  conn.close()
  structured_html_resp = html_resp.text.replace('`',"'").replace('html','').replace("'","")
  return structured_html_resp

@app.route('/')
def index():
  return render_template('processText.html')

@app.route('/processText',methods=['POST'])
def process_text():
  req=request.get_json()
  query = req.get('query','')

  is_create_table = model.generate_content(f"is this query '{query}' to create the table ?").text
  table_name = model.generate_content(f"What is the table name mentioned here '{query}'. Show only the table name without any additional text.")
  if is_create_table[:2] in ['No', 'no']:
    response = query_table(query, table_name.text)
  else:
    create_table(query, table_name.text)
    response = f'{table_name} table created successfully'
  return jsonify({'response':response})

if __name__ == "__main__":
  app.run(debug=True)