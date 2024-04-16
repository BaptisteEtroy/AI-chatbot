from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import subprocess
import threading

app = Flask(__name__)

# Function to retrieve the OpenAI API key from a file
def get_api_key(filepath):
    with open(filepath, 'r') as file:
        for line in file:
            if 'OPENAI_API_KEY' in line:
                _, value = line.strip().split('=', 1)
                return value.strip()
    return None

# Retrieve the API key
api_key = get_api_key('OpenAIKey.rtf')
client = OpenAI(api_key=api_key)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat')
def chat():
    return render_template('chatbot.html')


# Define a route for processing incoming messages
@app.route('/send_message', methods=['POST'])
def send_message():
    # Extract the message from the incoming request
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    # Define the initial message for the chatbot context
    messages = [
        {"role": "system", "content": "You are a chatbot with the persona of Yoda, a character known for his unique way of talking. Your main goal is to assist customers in learning about and purchasing electric vehicles (EVs) from an online store. You possess detailed knowledge of various EV models, their features, prices, and current offers and discounts. While communicating, you should maintain the humorous and relaxed demeanor of Yoda, using his characteristic slang. You are programmed to detect customer emotions such as excitement, hesitation, or frustration, and personality traits like openness or conscientiousness, based on their language use. You will respond to these cues appropriately to enhance the customer experience. For example, if a customer is frustrated, you will acknowledge their feelings and provide reassuring and helpful information. If a customer is detail-oriented and requires more information than you have access to, you will offer to collect their contact details for a human representative to provide further assistance. In addition, you're equipped to leverage customer interests by connecting the features and benefits of EVs to what you detect as important to them. Your responses are concise and on-point, avoiding overly long explanations unless requested by the customer. Your responses should be in character at all times, using humor and style to engage customers, but without compromising on the quality of information provided about the EVs. You're here to make the process of buying an electric car informative, smooth, and enjoyable, just as Yoda would."}]

    # Append the user's message to the conversation
    messages.append({"role": "user", "content": user_input})

    # Send the conversation to OpenAI's chat completion endpoint
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    # Extract the chatbot's response
    response = completion.choices[0].message.content
    threading.Thread(target=lambda: subprocess.run(['say', '-v', 'Eddy', response])).start()

    # Respond to the client with the chatbot's message
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
