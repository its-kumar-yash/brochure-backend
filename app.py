from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)

CORS(app)

url = os.getenv("REACT_APP_SUPABASE_URL")
key = os.getenv("REACT_APP_SUPABASE_API_KEY")
supabase = create_client(url, key)


EDEN_API_KEY = os.getenv("REACT_APP_EDEN_API_KEY")
EDEN_API_URL = 'https://api.edenai.run/v2/text/generation'

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World'

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    tone = data['tone']
    length_map = {'Short': '4-6 sentences', 'Medium': '8-10 sentences', 'Long': '15-20 sentences'}
    length = length_map[data['length']]
    features = data['features']
    positioning = data['positioning']

    prompt = f"""
    You are a copywriter at a marketing agency working on a brochure for a real estate developer.
    Generate a narrative flow for the real estate brochure keeping in mind the brand positioning and features of the property.

    <BRAND POSITIONING>
    {positioning}
    </BRAND POSITIONING> 

    <FEATURES>
    {features}
    </FEATURES>

    Keep the tone of the narrative {tone}
    Also make sure that the length of the copy is {length}
    """

    headers = {
        'Authorization': f'Bearer {EDEN_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'providers': 'cohere',
        'text': prompt,
        'temperature': 0.2,
        'max_tokens': 250,
    }

    response = requests.post(EDEN_API_URL, headers=headers, json=data)
    response_data = response.json()
    if response.status_code == 200:
        if 'cohere' in response_data and 'generated_text' in response_data['cohere']:
            generated_copy = response_data['cohere']['generated_text']
            return jsonify({'generatedCopy': generated_copy})
        else:
            return jsonify({'error': 'Key "generated_text" not found in response', 'response': response_data})
    else:
        return jsonify({'error': response_data}), response.status_code
    
@app.route('/insert', methods=['POST'])
def insert():
    try:
        data = request.json
        print("Request data:", data)
        table = supabase.table('marketingbrochure')
        # insert_response = supabase.table('marketingbrochure').insert(data).execute()
        table.insert(data).execute()
        return jsonify("Success"), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)