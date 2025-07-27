from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import tensorflow as tf
import numpy as np
from werkzeug.utils import secure_filename
import os
import json
import datetime
from PIL import Image
import ast
from fpdf import FPDF

app = Flask(__name__)

# Directory to store user data
BASE_DIR = "user_data"
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

# Function to create user folder
def get_user_folder(username):
    user_folder = os.path.join(BASE_DIR, username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder

# Load the trained model
MODEL_PATH = "skin_disease_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# Ensure the model is compiled properly
model.compile()

# Define allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    img = Image.open(image_path).resize((150, 150))  # Resize to (150,150,3)
    img_array = np.array(img) / 255.0  # Normalize pixel values
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array  # Shape will be (1, 150, 150, 3)


@app.route('/')
def home():
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()

        if not username:
            return '''<script>alert("Please enter a username!"); window.location.href='/login';</script>'''

        # Path to the user's JSON file INSIDE their folder
        user_file = os.path.join("user_data", username, f"{username}.json")

        if not os.path.exists(user_file):
            return '''<script>alert("User not found! Please register."); window.location.href='/signup';</script>'''

        with open(user_file, "r") as f:
            user_data = json.load(f)

        # Optionally, store username in session or pass to upload route
        return redirect(url_for('upload', username=username))  # if you want to pass username

    return render_template("login.html")



@app.route('/upload')
def upload():
    username = request.args.get('username')  # Get from URL
    if not username:
        return "Username not found in URL"
    
    return render_template('upload.html', username=username)



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        gender = request.form.get('gender')

        if not username or not age or not gender:
            return '''<script>alert("Please fill in all fields."); window.location.href='/signup';</script>'''

        base_dir = "user_data"
        user_folder = os.path.join(base_dir, username)
        user_file = os.path.join(user_folder, f"{username}.json")

        if os.path.exists(user_file):
            return '''<script>alert("User already exists! Please login."); window.location.href='/login';</script>'''

        os.makedirs(user_folder, exist_ok=True)  # ✅ Create folder for the user

        # Save user data inside the user's personal folder
        user_data = {"username": username, "age": age, "gender": gender}
        with open(user_file, "w") as f:
            json.dump(user_data, f)

        return '''<script>alert("Registration Successful! You can now login."); window.location.href='/login';</script>'''

    return render_template("signup.html")


USER_DIR = "user_data"

# Ensure the user data directory exists
if not os.path.exists(USER_DIR):
    os.makedirs(USER_DIR)

# Store Analysis Result
@app.route("/manual_save", methods=["POST"])
def manual_save():
    data = request.get_json()  # <-- VERY IMPORTANT
    username = data.get("username", "").strip()
    result = data.get("result", "").strip()

    print("DEBUG username:", username)
    print("DEBUG result:", result)
    
    if not username or not result:
        return jsonify({"error": "Missing username or result"}), 400
        
    # Convert string to dictionary (your style)
    result = result.replace("'", '"') 
    result = json.loads(result)   

    user_folder = os.path.join("user_data", username)
    print("Saving in folder:", user_folder)  # Debug Print

    os.makedirs(user_folder, exist_ok=True)

    results_file = os.path.join(user_folder, "results.json")
    print("Results file path:", results_file)  # Debug Print
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if os.path.exists(results_file):
        with open(results_file, "r") as f:
            past_results = json.load(f)
    else:
        past_results = []

    # Store the converted dictionary
    past_results.append({"timestamp": timestamp, "result": result})

    with open(results_file, "w") as f:
        json.dump(past_results, f, indent=4)

    print("Result saved successfully in file!")
    return jsonify({"message": "Result saved successfully!"})


# Generate Report (Full or Recent)
@app.route("/generate_report", methods=["GET"])
def generate_report():
    username = request.args.get("username", "").strip()
    report_type = request.args.get("type", "full")  # 'full' or 'recent'

    if not username:
        return jsonify({"error": "Username is missing"}), 400

    user_folder = os.path.join(USER_DIR, username)
    results_file = os.path.join(user_folder, "results.json")
    user_details_file = os.path.join(user_folder, f"{username}.json")
    
    if not os.path.exists(results_file) or not os.path.exists(user_details_file):
        return "Results or User Details not found!", 404
        
    with open(results_file, "r") as f:
        results = json.load(f)
    
    with open(user_details_file, 'r') as f:
        user_details = json.load(f)

    if report_type == "recent":
        results = [results[-1]]  # Get the most recent entry
    

    pdf_filename = os.path.join(user_folder, f"{username}_report.pdf")
    generate_pdf_report(username, user_details, results, pdf_filename)
    return send_file(pdf_filename, as_attachment=True)

# PDF Report Generator using FPDF
def generate_pdf_report(username, user_details, results, output_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Skin Diagnosis Report for {username}", ln=True, align="C")
    
    pdf.ln(10)  # Add some space

    # User Details
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "User Details", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, f"Name: {user_details.get('username','N/A')}", ln=True)
    pdf.cell(200, 10, f"Age: {user_details.get('age', 'N/A')}", ln=True)
    pdf.cell(200, 10, f"Gender: {user_details.get('gender', 'N/A')}", ln=True)

    pdf.ln(5)  # Line break

# Diagnosis Report
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Diagnosis Report", ln=True)

    pdf.set_font("Arial", '', 12)

    for entry in results:
        pdf.cell(200, 10, f"Date: {entry.get('timestamp', 'N/A')}", ln=True)
        pdf.cell(200, 10, f"Diagnosis: {entry['result']['disease']}", ln=True)
        pdf.cell(200, 10, f"Confidence: {entry['result']['confidence']:.2f}", ln=True)
        pdf.multi_cell(0, 10, f"Symptoms: {entry['result']['details']['Symptoms']}")
        pdf.multi_cell(0, 10, f"Possible Causes: {entry['result']['details']['Possible Causes']}")

        pdf.ln(5)  # Add space between entries

    pdf.output(output_path)

@app.route("/generate_pdf_report", methods=["POST"])
def generate_pdf_report_route():
    username = request.form.get("username", "").strip()

    if not username:
        return "Error: Username is missing", 400

    user_folder = os.path.join(USER_DIR, username)
    history_file = os.path.join(user_folder, "results.json")
    pdf_file = os.path.join(user_folder, f"{username}_report.pdf")

    if not os.path.exists(history_file):
        return "No history found.", 404

    with open(history_file, "r") as f:
        history = json.load(f)

    # Generate PDF with history
    generate_pdf_report(username, history, pdf_file)

    return send_file(pdf_file, as_attachment=True)

# Reports Page
@app.route("/reports")
def reports():
    return render_template("reports.html")


# Mapping class indices to disease names
class_labels = {
    0: "Cellulitis",
    1: "Impetigo",
    2: "Dry Skin",
    3: "Athlete's Foot",
    4: "Nail Fungus",
    5: "Ringworm",
    6: "Normal Skin",
    7: "Oily Skin",
    8: "Cutaneous Larva Migrans",
    9: "Chickenpox",
    10: "Shingles"
}

# Dictionary containing disease details
disease_info = {
    "Cellulitis": {
        "Symptoms": "Redness, swelling, tenderness, stretched appearance of the skin, pain or skin sore.",
        "Possible Causes": "Bacterial infection / break in the skin / certain conditions like diabetes, lymphedema and poor circulation can increase the risk of developing cellulitis."
    },
    "Impetigo": {
        "Symptoms": "Reddish sores or blisters that rupture, ooze and form honey-colored crusts, often around the nose and mouth.",
        "Possible Causes": "Bacterial infection / break in the skin / spread through direct skin-to-skin contact or by sharing items like towels or clothing with an infected person."
    },
    "Athlete's Foot": {
        "Symptoms": "Itching, stinging, burning sensation, redness, flakiness, peeling skin, thickened or discolored toenails, swollen and warm feet.",
        "Possible Causes": "Fungal infection / spread through direct contact with an infected person / by touching contaminated surfaces like locker room floors, shower floors or towels."
    },
    "Nail Fungus": {
        "Symptoms": "Nail brittleness, discoloration (white, yellow, brown or green), thickening, separation from the nail bed, debris or inflamation under the nail.",
        "Possible Causes": "Fungal infection / through infections in moist places like public pools, showers or locker rooms."
    },
    "Ringworm": {
        "Symptoms": "Redness, swelling, itchiness, ring-shaped rash with raised, scaly borders and a clearer center.",
        "Possible Causes": "Fungal infection / spread through direct skin-to-skin contact with an infected person or animal / by touching contaminated objects like towels, clothing or gym mats."
    },
    "Cutaneous Larva Migrans": {
        "Symptoms": "Intense itching, red, swollen lumps or blisters, winding-threadlike-raised-reddish-brown rash.",
        "Possible Causes": "Hookworm larvae (most commonly 'Dog Hookworm') / animal larvae from contaminated soil or sand."
    },
    "Chickenpox": {
        "Symptoms": "Itchy rash with small, fluid-filled blisters that eventually scab over, often accompanied by fever and fatigue.",
        "Possible Causes": "Varicella-Zoster Virus (VZV) - through respiratory droplets from coughing or sneezing of an infected person / direct contact with the fluid from chickenpox blisters."
    },
    "Shingles": {
        "Symptoms": "Painful rash with blisters, often on one side of the body or face, preceded by pain, tingling or burning.",
        "Possible Causes": "Reactivation of the Varicella-Zoster Virus, the same virus that causes chickenpox, Postherpetic Neuralgia (PHN)."
    },
    "Unknown Disease": {
        "Symptoms": "No skin disease detected.",
        "Possible Causes": "No skin disease detected."
    },
}

@app.route('/predict', methods=['POST'])
def predict():
    print("Received request!")  # Debugging step

    
    if 'file' not in request.files:
        print("No file part")
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        print("Invalid file format")
        return jsonify({"error": "Invalid file format"})

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    print("File saved at:", file_path)  # Debugging step

    img_array = preprocess_image(file_path)
    prediction = model.predict(img_array)

    print("Prediction Raw Output:", prediction)  # Debugging step

    predicted_class = np.argmax(prediction, axis=1)[0]
    confidence = np.max(prediction)
    disease_name = class_labels.get(predicted_class, "Unknown Disease")

    # Fetch disease details, default to "Unknown Disease" if not found
    disease_details = disease_info.get(disease_name, disease_info["Unknown Disease"])

    print("Predicted Class:", disease_name, "Confidence:", confidence, "Details:", disease_details)

    print("Predicted Disease Info:", disease_info.get(disease_name, {}))

    return jsonify({
        "class": int(predicted_class),
        "disease": disease_name,
        "confidence": float(confidence),
        "details": disease_details,  # Now passing disease details properly
        "file_path": f"/uploads/{filename}"
    })
   

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

