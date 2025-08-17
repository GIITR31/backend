from flask import Flask, jsonify, request
from flask_cors import CORS
import os, json, traceback
import cohere
from dotenv import load_dotenv

# ---------------------------
# Setup
# ---------------------------
load_dotenv()
app = Flask(__name__)

# Allow requests from any origin to /api/* during development
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=False
)

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
print("COHERE_API_KEY prefix:", (COHERE_API_KEY or "")[:6])
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY not set in .env")

co = cohere.Client(COHERE_API_KEY)

# ---------------------------
# Data loading (defensive)
# ---------------------------
DATA_DIR = os.path.dirname(__file__)
FULL_JOURNEY_PATH = os.path.join(DATA_DIR, "full_journey.json")
EPISODES_SUMMARY_PATH = os.path.join(DATA_DIR, "episodes_summary.json")

print("FULL_JOURNEY_PATH:", FULL_JOURNEY_PATH)
print("EPISODES_SUMMARY_PATH:", EPISODES_SUMMARY_PATH)

def load_json_safe(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to load {path}: {e}")
        return fallback

full_conversation = load_json_safe(FULL_JOURNEY_PATH, [])
episodes_summary = load_json_safe(EPISODES_SUMMARY_PATH, [])

# ---------------------------
# Routes
# ---------------------------
@app.route("/api/test", methods=["GET"])
def test():
    return jsonify({"msg": "Backend is up!"})

@app.route("/api/episodes", methods=["GET"])
def get_episodes():
    return jsonify(episodes_summary)

@app.route("/api/conversation", methods=["GET"])
def get_conversation():
    return jsonify(full_conversation)

@app.route("/api/chat", methods=["POST"])
def chat():
    # Log request metadata for debugging
    print("Incoming", request.method, request.path)
    print("Origin:", request.headers.get("Origin"))
    print("Content-Type:", request.headers.get("Content-Type"))

    # Parse JSON body safely
    try:
        data = request.get_json(force=True, silent=False)
    except Exception as e:
        print("JSON parse error:", e)
        return jsonify({"answer": f"Error: invalid JSON body: {e}"}), 400

    print("Received ", data)

    user_query = (data or {}).get("query", "").strip()
    episode_id = (data or {}).get("episodeId", None)

    # Optional: pull episode context to improve answers
    context_text = ""
    if episode_id is not None and episodes_summary:
        ep = next((e for e in episodes_summary if str(e.get("id")) == str(episode_id)), None)
        if ep:
            context_text = (
                f"Episode Title: {ep.get('title','')}\n"
                f"Summary: {ep.get('summary','')}\n"
                f"Trigger: {ep.get('trigger','')}\n"
                f"Outcome: {ep.get('outcome','')}\n"
            )

    if not user_query:
        return jsonify({"answer": "Please enter a question."}), 400

    prompt = (
        "You are a helpful health-journey assistant.\n"
        f"{'Episode context:\\n' + context_text if context_text else ''}"
        f"User question: {user_query}\n"
        "Answer clearly and concisely."
    )

    try:
        resp = co.generate(
            model="command",         # "command" or "command-light" as available for your key
            prompt=prompt,
            max_tokens=200,
            temperature=0.6
        )
        answer = (resp.generations[0].text or "").strip()
        if not answer:
            answer = "I couldn't generate an answer right now."
        return jsonify({"answer": answer})
    except Exception as e:
        print("Cohere error:\n", traceback.format_exc())
        return jsonify({"answer": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    # host="0.0.0.0" if you need to access from other devices on your LAN
    print("Backend running on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
