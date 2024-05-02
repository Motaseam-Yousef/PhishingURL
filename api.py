from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Set up your Gemini API configuration using environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.0-pro-latest')

# Define function to extract text from a URL
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator='\n', strip=True)
    except requests.RequestException as e:
        return str(e)

@app.route('/check_url', methods=['GET'])
def check_url():
    url = request.args.get('url', default='https://example.com')
    
    # Extract text from URL
    extracted_text = extract_text_from_url(url)
    
    # Create the text prompt for the phishing detection
    text_prompt = f'''
    You are a Phishing detector check if this URL is a Phishing website or no : \n The url is: {url}, if it IP or http only then assume it as Phishing website,
    Also this the content of the url:\n\n {extracted_text}\n\n\n if it have any as this sentences:
    - "Verify your account to avoid suspension."
    - "Your account has been compromised. Click here to secure it."
    - "You have won a prize! Click here to claim it."
    - "Confirm your personal information to continue using our services."
    - "Urgent: Your payment information needs updating."
    - "You are eligible for a government refund."
    - "See attached invoice for your recent purchase."
    - "You've received a secure message from your bank."
    - "We have noticed unusual activity from your account."
    - "Failure to update your details will result in account closure."
    Then its a Phishing.
    Response only by Phishing YES or NO ONLY
    '''
    
    # Generate response from the model
    response = model.generate_content([text_prompt])
    
    return jsonify({"result": response.text})

if __name__ == '__main__':
    app.run(debug=True)
