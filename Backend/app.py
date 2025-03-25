from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
import google.generativeai as genai  # Importing Google Gemini API

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/public')
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:8000"}})

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)  # Configure Gemini API with your key

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def process_csv(file_path):
    try:
        df = pd.read_csv(file_path, dtype=str)
        student_data = []

        for _, row in df.iterrows():
            student = {
                'STUDENT ID': row['STUDENT ID'],
                'STUDENT NAME': row['STUDENT NAME'],
                'AGE': row['AGE'],
                'GENDER': row['GENDER'],
                'YearLevel': row['YearLevel'],
                'Section': row['Section'],
                'Date': row['Date'],
            }
            for i in range(1, 51):
                student[f"Answer_{i}"] = int(row[str(i)]) if row[str(i)].isdigit() else 0
            student_data.append(student)

        return student_data

    except Exception as e:
        return [{"error": str(e)}]

def calculate_trait_score(student_data, start, end):
    scores = [student_data.get(f"Answer_{i}", 0) for i in range(start, end + 1)]
    return round(sum(scores) / len(scores), 2)

def generate_recommendations(ocean_scores):
    """
    Generate AI-based recommendations using Gemini API.
    """
    dominant_traits = []
    max_score = max(ocean_scores.values())
    for trait, score in ocean_scores.items():
        if score == max_score:
            dominant_traits.append(trait)

    prompt = f"""
    Based on the following OCEAN personality scores, provide personalized recommendations for the student:
    - Openness: {ocean_scores['Openness']}
    - Conscientiousness: {ocean_scores['Conscientiousness']}
    - Extraversion: {ocean_scores['Extraversion']}
    - Agreeableness: {ocean_scores['Agreeableness']}
    - Neuroticism: {ocean_scores['Neuroticism']}

    The most dominant trait(s) are: {", ".join(dominant_traits)}.

    Provide teaching strategies or approaches for this student based on their dominant trait(s).
    Recommendations:
    """
    try:
        # Send the request to Gemini API (Google Generative AI)
        model = genai.GenerativeModel("gemini-1.5-flash")  # Use Gemini 1.5 Flash model for fast responses
        response = model.generate_content([{"text": prompt}])
        return response.text.strip()
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

@app.route('/assess/recommendations', methods=['GET'])
def get_recommendations():
    student_id = request.args.get('student_id')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")
    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    results = process_csv(file_path)
    student_data = next((student for student in results if str(student["STUDENT ID"]) == student_id), None)

    if student_data:
        trait_scores = {
            "Openness": calculate_trait_score(student_data, 41, 50),
            "Conscientiousness": calculate_trait_score(student_data, 31, 40),
            "Extraversion": calculate_trait_score(student_data, 1, 10),
            "Agreeableness": calculate_trait_score(student_data, 21, 30),
            "Neuroticism": calculate_trait_score(student_data, 11, 20),
        }
        recommendations = generate_recommendations(trait_scores)
        return jsonify({"recommendations": recommendations}), 200

    return jsonify({"error": f"Student ID {student_id} not found"}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully"}), 200

@app.route('/students', methods=['GET'])
def get_students():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")
    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    df = pd.read_csv(file_path)
    students_data = df[["STUDENT ID", "STUDENT NAME"]].to_dict(orient='records')
    return jsonify(students_data), 200

@app.route('/assess/individual', methods=['GET'])
def assess_individual():
    student_id = request.args.get('student_id')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")
    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    results = process_csv(file_path)
    student_data = next((student for student in results if str(student["STUDENT ID"]) == student_id), None)

    if student_data:
        trait_names = {
            "Extraversion": (1, 10),
            "Neuroticism": (11, 20),
            "Agreeableness": (21, 30),
            "Conscientiousness": (31, 40),
            "Openness": (41, 50),
        }

        trait_scores = {}
        max_score = 0
        dominant_traits = []

        formatted_result = f"""
        <h3>Analysis Result for {student_data['STUDENT NAME']} (ID: {student_data['STUDENT ID']})</h3>
        """
        
        for trait, (start, end) in trait_names.items():
            scores = [student_data.get(f"Answer_{i}", 0) for i in range(start, end + 1)]
            avg_score = round(sum(scores) / len(scores), 2)
            classification = "Low" if avg_score < 3 else "Moderate" if avg_score < 4 else "High"
            color = "red" if classification == "Low" else "orange" if classification == "Moderate" else "green"

            trait_scores[trait] = avg_score
            if avg_score > max_score:
                max_score = avg_score
                dominant_traits = [trait]
            elif avg_score == max_score:
                dominant_traits.append(trait)

            formatted_result += f"<h4>{trait}: <span style='color:{color};'>{avg_score} ({classification})</span></h4>"

        dominant_text = " & ".join(dominant_traits)
        formatted_result = f"<h3 style='color:blue;'>Most Dominant Trait: {dominant_text} ({max_score})</h3>" + formatted_result

        return jsonify({"result": formatted_result}), 200

    return jsonify({"error": f"Student ID {student_id} not found"}), 404

@app.route('/assess/all', methods=['GET'])
def assess_all_students():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")
    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    results = process_csv(file_path)
    total_students = len(results)

    trait_names = {
        "Extraversion": (1, 10),
        "Neuroticism": (11, 20),
        "Agreeableness": (21, 30),
        "Conscientiousness": (31, 40),
        "Openness": (41, 50),
    }

    trait_averages = {trait: [] for trait in trait_names}

    for student in results:
        for trait, (start, end) in trait_names.items():
            scores = [student.get(f"Answer_{i}", 0) for i in range(start, end + 1)]
            avg_score = round(sum(scores) / len(scores), 2)
            trait_averages[trait].append(avg_score)

    formatted_result = f"<h3>Total Surveys: {total_students}</h3><h3>Trait Analysis:</h3>"
    for trait, scores in trait_averages.items():
        overall_avg = round(sum(scores) / len(scores), 2)
        classification = "Low" if overall_avg < 3 else "Moderate" if overall_avg < 4 else "High"
        color = "red" if classification == "Low" else "orange" if classification == "Moderate" else "green"

        formatted_result += f"<h4>{trait}: <span style='color:{color};'>{overall_avg} ({classification})</span></h4>"

    return jsonify({"result": formatted_result}), 200

@app.route('/generate-bar-chart', methods=['GET'])
def generate_bar_chart():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")

    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    results = process_csv(file_path)
    total_students = len(results)

    trait_ranges = {
        "Openness": (41, 50),
        "Conscientiousness": (31, 40),
        "Extraversion": (1, 10),
        "Agreeableness": (21, 30),
        "Neuroticism": (11, 20),
    }

    trait_averages = {}

    for trait, (start, end) in trait_ranges.items():
        total_score = sum(
            sum(student.get(f"Answer_{i}", 0) for i in range(start, end + 1)) 
            for student in results
        )
        count = total_students * 10  # 10 questions per trait
        trait_averages[trait] = round(total_score / count, 2) if count > 0 else 0

    # ✅ Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    traits = list(trait_averages.keys())
    scores = list(trait_averages.values())

    ax.barh(traits, scores, color=["green", "red", "yellow", "blue", "purple"])
    ax.set_xlabel("Average Score")
    ax.set_title("Personality Trait Averages")

    # ✅ Force save the file in `uploads`
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], "horizontal_bar_chart.png")
    plt.savefig(chart_path, bbox_inches="tight")
    plt.close()

    print("✅ Bar Chart Saved at:", chart_path)  # Debugging log

    return jsonify({"message": "Bar chart generated successfully!", "chart_url": "/uploads/horizontal_bar_chart.png"})





@app.route('/assess/ocean-averages', methods=['GET'])
def get_ocean_averages():
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], "latest_upload.csv")

    if not os.path.exists(file_path):
        return jsonify({"error": "No data available. Upload a CSV first."}), 400

    results = process_csv(file_path)
    total_students = len(results)

    trait_ranges = {
        "Openness": (41, 50),
        "Conscientiousness": (31, 40),
        "Extraversion": (1, 10),
        "Agreeableness": (21, 30),
        "Neuroticism": (11, 20),
    }

    trait_averages = {}

    # Calculate the average for each trait
    for trait, (start, end) in trait_ranges.items():
        total_score = sum(
            sum(student.get(f"Answer_{i}", 0) for i in range(start, end + 1)) 
            for student in results
        )
        count = total_students * 10  # 10 questions per trait
        trait_averages[trait] = round(total_score / count, 2) if count > 0 else 0

    return jsonify(trait_averages)

@app.route('/get-recommendation', methods=['POST'])
def get_recommendation():
    # Get the data sent from the frontend (POST request body)
    data = request.get_json()
    
    # Check if the dominant trait is present in the request
    dominant_trait = data.get("dominant_trait", "").lower()
    
    # Define recommendations for different traits
    recommendations = {
        "openness": {
            "student": "Engage in creative activities like art, writing, or brainstorming.",
            "teacher": "Encourage students to explore creativity through diverse learning materials."
        },
        "conscientiousness": {
            "student": "Set goals and stay organized.",
            "teacher": "Provide structured assignments and reward diligence."
        },
        "extraversion": {
            "student": "Engage in group activities, lead discussions, and build social connections.",
            "teacher": "Incorporate group work and interactive learning."
        },
        "agreeableness": {
            "student": "Volunteer and practice empathy.",
            "teacher": "Foster teamwork and recognize acts of kindness."
        },
        "neuroticism": {
            "student": "Practice stress management and build resilience.",
            "teacher": "Provide emotional support and teach coping strategies."
        }
    }

    # Get the recommendation for the dominant trait
    result = recommendations.get(dominant_trait)

    if result:
        return jsonify({
            "student_recommendation": result["student"],
            "teacher_strategy": result["teacher"]
        })
    else:
        return jsonify({"error": "Invalid or missing dominant trait."}), 400



@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
