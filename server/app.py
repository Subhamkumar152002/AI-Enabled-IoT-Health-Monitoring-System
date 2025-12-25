import json
import threading
import re
from openai import OpenAI
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory, redirect, url_for, session
from flask_socketio import SocketIO
from flask_session import Session
from ai_model import predict_disease  # AI model for disease prediction
from fall_detection import detect_fall  # Fall detection logic

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

app.secret_key = "your_secret_key"  # Replace with a secure key
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket communication

# Configure OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Default dummy data
DUMMY_DATA = {
    "heart_rate": 85,
    "spo2": 97.5,
    "temperature": 36.8,
    "acceleration": [0.1, -0.2, 9.8],
    "fall_detected": False,
    "prediction": "No Disease Detected"
}

# Store latest sensor data (Thread-Safe)
sensor_data = DUMMY_DATA.copy()
data_lock = threading.Lock()
quiz_sessions = {}

def get_health_data():
    """Return current sensor data or dummy data if no sensors detected"""
    with data_lock:
        # Check if we have real sensor data (non-dummy values)
        is_real_data = (
            sensor_data["heart_rate"] != DUMMY_DATA["heart_rate"] or
            sensor_data["spo2"] != DUMMY_DATA["spo2"] or
            sensor_data["temperature"] != DUMMY_DATA["temperature"]
        )
        return sensor_data.copy() if is_real_data else DUMMY_DATA.copy()

def generate_ai_prompt(answers, diagnosis=False):
    """Generate AI prompt using current health data"""
    health_data = get_health_data()
    
    prompt = f"""
    Patient Health Data:
    - Heart Rate: {health_data['heart_rate']} bpm
    - SpO2: {health_data['spo2']}%
    - Temperature: {health_data['temperature']}°C
    - Acceleration: {health_data['acceleration']}
    - Current Prediction: {health_data['prediction']}
    
    Previous Answers: {answers}
    
    """
    
    if diagnosis:
        prompt += """Analyze this data and:
        1. Identify the most likely cardiovascular condition
        2. Provide confidence percentage (0-100)
        3. List 3-5 recommendations
        Format response as JSON:
        {{
            "condition": "string",
            "confidence": number,
            "recommendations": ["list"]
        }}
        """
    else:
        prompt += """Generate the next yes/no question to assess cardiovascular health. 
        Format response as JSON: 
        {{
            "text": "question",
            "options": ["Yes", "No"],
            "completed": boolean
        }}
        """
    return prompt

@app.route("/post-data", methods=["POST"])
def post_data():
    global sensor_data
    try:
        data = request.get_json()
        
        if not data:
            logging.error("❌ Empty Request Received!")
            return jsonify({"status": "error", "message": "Empty request"}), 400

        # Use dummy data if sensors aren't providing valid data
        valid_data = {
            "heart_rate": float(data.get("heart_rate", DUMMY_DATA["heart_rate"])),
            "spo2": float(data.get("spo2", DUMMY_DATA["spo2"])),
            "temperature": float(data.get("temperature", DUMMY_DATA["temperature"])),
            "acceleration": data.get("acceleration", DUMMY_DATA["acceleration"])
        }

        with data_lock:
            # Update sensor data with valid values
            sensor_data.update({
                **valid_data,
                "fall_detected": detect_fall(valid_data["acceleration"]),
                "prediction": predict_disease(valid_data)
            })

            logging.info(f"📡 Updated Sensor Data: {sensor_data}")
            socketio.emit("sensor_data", sensor_data)

            if sensor_data["fall_detected"]:
                socketio.emit("fall_alert", {"message": "⚠️ Fall Detected! Immediate Attention Needed!"})

            socketio.emit("disease_prediction", {"prediction": sensor_data["prediction"]})

        return jsonify({"status": "success", "message": "Data received"}), 200

    except Exception as e:
        logging.error(f"❌ Error Processing Request: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

def clean_ai_response(response):
    """Extract and clean AI-generated JSON response"""
    try:
        # Remove markdown blocks if present
        response = response.replace('```json', '').replace('```', '').strip()
        
        # Extract valid JSON using regex (handles cases where AI adds extra text)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)  # Extract JSON content

        return response  # Return cleaned JSON string
    except Exception as e:
        logging.error(f"Error cleaning AI response: {str(e)}")
        return "{}"  # Return empty JSON if cleaning fails


@app.route("/generate_question", methods=["POST"])
def generate_question():
    try:
        data = request.json
        session_id = data.get('session_id')
        
        # Enhanced prompt with example
        prompt = generate_ai_prompt(data.get('answers', [])) + """
        Example valid response:
        {
            "text": "Do you experience chest pain during physical activity?",
            "options": ["Yes", "No"],
            "completed": false
        }
        """
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:5000"),
                "X-Title": os.getenv("SITE_NAME", "HealthMonitor")
            },
            model="meta-llama/llama-3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}  # Force JSON output
        )
        
        response_content = completion.choices[0].message.content
        cleaned_response = clean_ai_response(response_content)
        
        try:
            question_data = json.loads(cleaned_response)
        except json.JSONDecodeError:
            # Fallback to default question if JSON parsing fails
            question_data = {
                "text": "Do you experience any chest pain?",
                "options": ["Yes", "No"],
                "completed": False
            }
        
        # Add validation with defaults
        question_data.setdefault("text", "Have you experienced any chest pain recently?")
        question_data.setdefault("options", ["Yes", "No"])
        question_data.setdefault("completed", False)
        
        # Ensure options are list type
        if not isinstance(question_data["options"], list):
            question_data["options"] = ["Yes", "No"]
        
        if session_id:
            quiz_sessions[session_id] = {
                'answers': data.get('answers', []),
                'health_data': get_health_data()
            }
        
        return jsonify(question_data)
    
    except Exception as e:
        logging.error(f"AI Question Generation Error: {str(e)}")
        # Return safe default question
        return jsonify({
            "text": "Have you noticed any irregular heartbeats?",
            "options": ["Yes", "No"],
            "completed": False
        }), 200
    
@app.route("/diagnose", methods=["POST"])
def diagnose():
    try:
        data = request.json
        session_id = data.get('session_id')
        
        current_data = get_health_data()
        
        if session_id and session_id in quiz_sessions:
            answers = quiz_sessions[session_id]['answers']
        else:
            answers = data.get('answers', [])
        
        prompt = generate_ai_prompt(answers, diagnosis=True)
        
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": os.getenv("SITE_URL", "http://localhost:5000"),
                "X-Title": os.getenv("SITE_NAME", "HealthMonitor")
            },
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_content = completion.choices[0].message.content
        cleaned_response = clean_ai_response(response_content)
        diagnosis_data = json.loads(cleaned_response)
        
        # Validate diagnosis structure
        required_keys = ['condition', 'confidence', 'severity', 'recommendations']
        if not all(key in diagnosis_data for key in required_keys):
            raise ValueError(f"Invalid diagnosis format from AI. Missing keys: {required_keys}")
        
        # Ensure recommendations are properly formatted
        if not isinstance(diagnosis_data['recommendations'], list):
            diagnosis_data['recommendations'] = [str(diagnosis_data['recommendations'])]
        
        if session_id and session_id in quiz_sessions:
            del quiz_sessions[session_id]
        
        return jsonify(diagnosis_data)
    
    except json.JSONDecodeError as e:
        logging.error(f"JSON Parse Error: {e}\nOriginal Response: {response_content}")
        return jsonify({"error": "Failed to parse diagnosis response"}), 500
    except Exception as e:
        logging.error(f"AI Diagnosis Error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@app.route("/data", methods=["GET"])
def get_data():
    return jsonify(get_health_data())

@app.route("/")
def home():
    return render_template("index.html")


# Middleware to protect routes
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if "user" in session:
        return redirect(url_for("dashboard"))  # Redirect if already logged in

    if request.method == "POST":
        # Handle signup logic here
        email = request.form.get("email")
        password = request.form.get("password")
        # Assume signup is successful
        session["user"] = email  # Store user in session
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))  # Redirect if already logged in

    if request.method == "POST":
        # Handle login logic here
        email = request.form.get("email")
        password = request.form.get("password")
        # Assume login is successful
        session["user"] = email  # Store user in session
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")

def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.pop("user", None)  # Remove user from session
    return redirect(url_for("login"))
@app.route("/collecting-data", methods=["GET"])
def collecting_data():
    return render_template("collecting-data.html")
    
@app.route("/take-test", methods=["GET"])
def quiz():
    return render_template("quiz.html")
    
@app.route("/test", methods=["POST"])
def send_dummy_data():
    global sensor_data
    try:
        dummy_data = {
            "heart_rate": 85,
            "spo2": 97.5,
            "temperature": 36.8,
            "acceleration": [0.1, -0.2, 9.8]
        }
        return post_data()
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/firebase.js')
def serve_firebase():
    return send_from_directory("static", "firebase.js", mimetype="application/javascript")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)