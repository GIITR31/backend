from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for communication with your React frontend

# --- Configuration ---
# Set paths to your data files relative to this script
DATA_DIR = os.path.join(os.path.dirname(__file__))
FULL_JOURNEY_PATH = os.path.join(DATA_DIR, 'full_journey.json')
EPISODES_SUMMARY_PATH = os.path.join(DATA_DIR, 'episodes_summary.json')

# --- Load your JSON data ---
full_conversation = []
episodes_summary = []

try:
    with open(FULL_JOURNEY_PATH, 'r', encoding='utf-8') as f:
        full_conversation = json.load(f)
    print(f"Successfully loaded {len(full_conversation)} messages from {FULL_JOURNEY_PATH}")
except FileNotFoundError:
    print(f"Error: {FULL_JOURNEY_PATH} not found. Please ensure your JSON data is in the 'backend' directory.")
    print("Starting with empty conversation data.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {FULL_JOURNEY_PATH}. Check file validity.")
    print("Starting with empty conversation data.")

try:
    with open(EPISODES_SUMMARY_PATH, 'r', encoding='utf-8') as f:
        episodes_summary = json.load(f)
    print(f"Successfully loaded {len(episodes_summary)} episodes from {EPISODES_SUMMARY_PATH}")
except FileNotFoundError:
    print(f"Error: {EPISODES_SUMMARY_PATH} not found. Please ensure your JSON data is in the 'backend' directory.")
    print("Starting with empty episodes data.")
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON from {EPISODES_SUMMARY_PATH}. Check file validity.")
    print("Starting with empty episodes data.")

# --- API Endpoints ---

# Endpoint to get the entire 8-month conversation
@app.route('/api/conversation', methods=['GET'])
def get_conversation():
    return jsonify(full_conversation)

# Endpoint to get the structured episode summaries
@app.route('/api/episodes', methods=['GET'])
def get_episodes():
    return jsonify(episodes_summary)

# Placeholder for your chat agent logic (connects to LLM)
@app.route('/api/chat', methods=['POST'])
def chat():
    user_query = request.json.get('query')
    
    # --- LLM Integration Placeholder ---
    # This is where you would call an actual LLM (e.g., OpenAI, Anthropic, etc.)
    # and pass in context from full_conversation and episodes_summary
    
    # Example: Simple keyword response or mock LLM call
    if "apob" in user_query.lower() or "blood" in user_query.lower():
        answer = "Rohan's ApoB was a key focus after his Month 3 diagnostic panel, revealing a high level of 130 mg/dL, which triggered a new nutrition plan. (Refer to episodes related to 'The Data-Driven Wake-Up Call')."
    elif "travel" in user_query.lower():
        answer = "Rohan travels at least one week every month, often impacting his adherence. The Elyx team provides adapted plans for his trips, ensuring continuity even with his demanding schedule."
    elif "why" in user_query.lower() and "decision" in user_query.lower():
        # A very basic attempt to find a decision rationale
        if episodes_summary:
            example_episode = episodes_summary[0]
            answer = f"One key decision in '{example_episode['title']}' was triggered by: {example_episode['trigger']}. The outcome was: {example_episode['outcome']}."
        else:
            answer = "I need more context or data to explain specific decisions."
    else:
        answer = f"Thank you for your question about '{user_query}'. For this demo, I can answer questions about 'ApoB', 'travel', or 'why a decision was made'. You can refine my intelligence by integrating a full LLM and RAG."
    
    return jsonify({"answer": answer})

if __name__ == '__main__':
    # Ensure the data files exist before starting the server
    if not os.path.exists(FULL_JOURNEY_PATH):
        print(f"CRITICAL ERROR: '{FULL_JOURNEY_PATH}' not found. Please generate your full conversation data.")
        print("Backend server will start, but will serve empty data for conversation.")
    if not os.path.exists(EPISODES_SUMMARY_PATH):
        print(f"CRITICAL ERROR: '{EPISODES_SUMMARY_PATH}' not found. Please generate your episodes summary data.")
        print("Backend server will start, but will serve empty data for episodes.")
        
    print("\n--- Starting Flask Backend Server ---")
    print(f"Serving data from: {DATA_DIR}")
    print("API Endpoints:")
    print("  GET /api/conversation")
    print("  GET /api/episodes")
    print("  POST /api/chat (for AI agent queries)")
    print("Navigate your React app to http://localhost:5000\n")
    app.run(port=5000, debug=True)

