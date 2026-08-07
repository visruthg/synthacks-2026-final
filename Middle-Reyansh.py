from flask import Flask, render_template_string, request
import re
from datetime import datetime

app = Flask(__name__)

FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Health 360 - Report a Problem</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Nunito', 'Segoe UI', Arial, sans-serif; background: #f4f7f1; min-height: 100vh; }
        .header { background: #106c65; color: white; padding: 20px 30px; width: 100%; }
        .header h1 { font-size: 28px; margin: 0; font-weight: 800; }
        .header p { font-size: 14px; color: #c3d8c9; margin-top: 4px; }
        .container { max-width: 520px; margin: 0 auto; padding: 25px 20px; }
        .card { background: white; border-radius: 16px; padding: 22px; box-shadow: 0 3px 12px rgba(0,0,0,0.08); }
        h2 { color: #106c65; margin-bottom: 16px; }
        .quick p { font-weight: 700; color: #106c65; margin-bottom: 10px; }
        .chip { display: inline-block; background: #eef3ea; color: #106c65; border: 2px solid #cfe0c3; border-radius: 20px; padding: 6px 14px; margin: 4px; font-size: 14px; font-weight: 700; cursor: pointer; font-family: inherit; transition: 0.2s; }
        .chip:hover { background: #dcead0; }
        label { font-weight: 700; color: #333; }
        textarea { width: 100%; height: 110px; padding: 10px; font-size: 15px; font-family: inherit; border: 2px solid #c9d6cf; border-radius: 10px; margin-top: 6px; }
        textarea:focus { outline: none; border-color: #106c65; }
        input[type="submit"] { padding: 10px 22px; background: #106c65; color: white; border: none; cursor: pointer; font-size: 15px; font-family: inherit; font-weight: 700; border-radius: 10px; }
        input[type="submit"]:hover { background: #148a81; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Health 360</h1>
        <p>Your complete health support companion</p>
    </div>
    <div class="container">
        <div class="card">
            <h2>Report Your Problem</h2>
            <div class="quick">
                <p>Quick pick a common issue:</p>
                <button type="button" class="chip" onclick="pick('headache')">Headache</button>
                <button type="button" class="chip" onclick="pick('stomach ache')">Stomach ache</button>
                <button type="button" class="chip" onclick="pick('fever')">Fever</button>
                <button type="button" class="chip" onclick="pick('vomiting')">Vomiting</button>
                <button type="button" class="chip" onclick="pick('cold and cough')">Cold &amp; cough</button>
                <button type="button" class="chip" onclick="pick('throat pain')">Throat pain</button>
                <button type="button" class="chip" onclick="pick('back pain')">Back pain</button>
                <button type="button" class="chip" onclick="pick('gas or acidity')">Gas / acidity</button>
                <button type="button" class="chip" onclick="pick('chest pain')">Chest pain</button>
                <button type="button" class="chip" onclick="pick('pain in private area')">Private area pain</button>
                <button type="button" class="chip" onclick="pick('heart attack')">Heart attack</button>
                <button type="button" class="chip" onclick="pick('bleeding')">Bleeding</button>
                <button type="button" class="chip" onclick="pick('dizziness')">Dizziness</button>
                <button type="button" class="chip" onclick="pick('body pain')">Body pain</button>
                <button type="button" class="chip" onclick="pick('tiredness')">Tiredness</button>
            </div>
            <form method="POST" action="/" id="pf">
                <label for="problem">Or describe your problem:</label>
                <textarea id="problem" name="problem" placeholder="e.g. I have a stomach ache since yesterday" required></textarea>
                <input type="submit" value="Submit">
            </form>
        </div>
    </div>
    <script>
        function pick(value) {
            document.getElementById('problem').value = value;
            document.getElementById('problem').focus();
        }
    </script>
</body>
</html>
"""

RESPONSE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Health 360 - Result</title>
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Nunito', 'Segoe UI', Arial, sans-serif; background: #f4f7f1; min-height: 100vh; }
        .header { background: #106c65; color: white; padding: 20px 30px; width: 100%; }
        .header h1 { font-size: 28px; margin: 0; font-weight: 800; }
        .header p { font-size: 14px; color: #c3d8c9; margin-top: 4px; }
        .container { max-width: 560px; margin: 0 auto; padding: 25px 20px; }
        .card { background: white; border-radius: 16px; padding: 22px; box-shadow: 0 3px 12px rgba(0,0,0,0.08); margin-bottom: 20px; }
        .card h3 { margin-bottom: 8px; }
        .badge { display: inline-block; padding: 5px 16px; border-radius: 20px; font-size: 13px; font-weight: 800; color: white; margin-bottom: 12px; }
        .badge.serious { background: #d32f2f; }
        .badge.medium { background: #f57c00; }
        .badge.small { background: #8da25e; }
        .badge.nonbio { background: #7e57c2; }
        .advice { font-size: 17px; font-weight: 700; color: #333; margin-bottom: 8px; }
        .or { font-weight: 800; font-size: 13px; color: #888; margin: 12px 0 4px; }
        ul { margin: 0 0 0 18px; }
        li { font-size: 15px; line-height: 1.9; }
        .hospital-card { border-left: 6px solid #d32f2f; background: #fff5f5; }
        .hospital-card h3 { color: #d32f2f; font-size: 18px; }
        .box { margin-top: 14px; padding: 14px; border-radius: 12px; background: #fff; }
        .box p { font-size: 15px; line-height: 1.7; margin: 3px 0; }
        .ins { border: 2px solid #ffd6a5; }
        .what { border: 2px solid #ffb3b3; }
        .log { border: 2px solid #ddd; font-size: 13px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Health 360</h1>
        <p>Your complete health support companion</p>
    </div>
    <div class="container">
        <div class="card">
            <span class="badge {{ category }}">{{ title }}</span>
            <p class="advice">{{ advice }}</p>
            {% if remedy %}
            <div class="or">Try one of these:</div>
            <ul>
            {% for option in remedy %}
                <li>{{ option }}</li>
            {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% if category == 'serious' %}
        <div class="card hospital-card">
            <h3>&#128690; Hospital &amp; emergency action</h3>
            <p>Alert sent to City General Hospital &middot; Ambulance line 108</p>
            <p><strong>Emergency contacts on file:</strong> g (g) &mdash; 1</p>
            <div class="box ins">
                <strong>&#128176; Insurance support</strong>
                <p>Estimated cost &#8377; 46350.00 is above your insurance cover of &#8377; 2000.00.</p>
                <p>Would you like to apply for insurance now?</p>
            </div>
            <div class="box what">
                <strong>&#128680; Emergency</strong>
                <p>&#128203; <strong>What happened</strong></p>
                <p>Symptoms: {{ problem }} | Severity: CRITICAL</p>
            </div>
            <div class="box log">
                {% for line in log %}
                <p>{{ line }}</p>
                {% endfor %}
            </div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

CONDITIONS = [
    {
        "keywords": ["chest pain", "heart attack", "unconscious", "breathing", "heavy bleeding", "bleeding", "poison", "suicide"],
        "category": "serious",
        "title": "EMERGENCY",
        "advice": "This is a serious problem. An ambulance is on the way to your house. Do not ignore it.",
        "remedies": [
            "An ambulance is on the way to your house — hold on.",
            "Keep the person calm and lying flat on their back.",
            "Loosen tight clothing around the neck and chest.",
            "If bleeding, press a clean cloth firmly on the wound.",
            "Do not give food, water, or any medicine.",
            "Do not move the person unless absolutely necessary.",
        ],
    },
    {
        "keywords": ["love attack", "broken heart", "heartbreak", "breakup", "love", "crush", "sad", "depress", "emotional", "stress"],
        "category": "nonbio",
        "title": "Not a medical issue",
        "advice": "This is not a biological or medical problem. It will pass with time.",
        "remedies": [
            "Talk to a close friend or family member about how you feel.",
            "Take a walk or do light exercise to clear your mind.",
            "Listen to music or watch something you enjoy.",
            "Write down your thoughts in a journal.",
            "Focus on a hobby like sports, drawing, or reading.",
            "If feelings do not improve, talk to a counselor.",
        ],
    },
    {
        "keywords": ["vomit", "vomiting"],
        "category": "medium",
        "title": "Vomiting",
        "advice": "Vomiting needs care but is not an emergency.",
        "remedies": [
            "Drink ORS in small sips of water.",
            "Do not eat solid food for a few hours.",
            "Rest and avoid strong smells.",
            "Take Dolo (paracetamol) only if there is fever too.",
            "Eat something light like bananas or rice when you feel better.",
            "See a doctor if vomiting continues for more than 12 hours.",
        ],
    },
    {
        "keywords": ["stomach ache", "stomach", "belly", "tummy"],
        "category": "medium",
        "title": "Stomach ache",
        "advice": "A stomach ache needs attention but is not an emergency.",
        "remedies": [
            "Take Dolo (paracetamol) or a stomach antacid.",
            "Drink warm water and avoid cold drinks.",
            "Apply a warm compress on the stomach.",
            "Eat only light food like khichdi or curd rice.",
            "Avoid oily and spicy food.",
            "See a doctor if the pain lasts more than 2 days.",
        ],
    },
    {
        "keywords": ["fever", "temperature", "body heat"],
        "category": "medium",
        "title": "Fever",
        "advice": "A fever needs rest and hydration.",
        "remedies": [
            "Take Dolo 650 (paracetamol) as per the pack dose.",
            "Rest and keep the room cool.",
            "Place a wet cloth on the forehead.",
            "Drink plenty of water and fluids.",
            "If temperature goes above 102 F (39 C), see a doctor.",
        ],
    },
    {
        "keywords": ["headache", "head ache"],
        "category": "medium",
        "title": "Headache",
        "advice": "A headache is usually not serious.",
        "remedies": [
            "Take Dolo (paracetamol) with water.",
            "Lie down in a dark, quiet room.",
            "Drink water and avoid screens.",
            "Apply a cold cloth on the forehead.",
            "If it lasts more than 2 days, see a doctor.",
        ],
    },
    {
        "keywords": ["balls", "testicl", "private", "genital"],
        "category": "medium",
        "title": "Private area pain",
        "advice": "Pain in the private area should not be ignored.",
        "remedies": [
            "Wear loose cotton underwear.",
            "Lie down and rest; avoid heavy lifting.",
            "Apply a cold pack for 15 minutes at a time.",
            "Avoid tight clothes and long sitting.",
            "If pain is sharp or lasts more than a day, see a doctor immediately.",
        ],
    },
    {
        "keywords": ["back pain", "backache", "back ache"],
        "category": "medium",
        "title": "Back pain",
        "advice": "Back pain usually improves with rest.",
        "remedies": [
            "Rest on a hard surface with a pillow under your knees.",
            "Apply a warm compress on the back.",
            "Take Dolo (paracetamol) for the pain.",
            "Avoid bending and heavy lifting.",
            "Do light stretching only if it does not hurt.",
            "See a doctor if it lasts more than 2 days.",
        ],
    },
    {
        "keywords": ["throat", "cough", "cold"],
        "category": "medium",
        "title": "Throat / cough / cold",
        "advice": "Throat and cough issues are common and manageable.",
        "remedies": [
            "Gargle with warm salt water twice a day.",
            "Drink warm water with honey and lemon.",
            "Rest and avoid cold food and drinks.",
            "Take Dolo (paracetamol) if there is pain or fever.",
            "If the cough lasts more than a week, see a doctor.",
        ],
    },
    {
        "keywords": ["gastric", "gas", "acidity", "indigestion", "heartburn"],
        "category": "small",
        "title": "Gastric / gas",
        "advice": "This is a minor issue and should pass on its own.",
        "remedies": [
            "Drink a glass of warm water.",
            "Walk slowly for 10 minutes.",
            "Drink jeera (cumin) water.",
            "Avoid junk and spicy food.",
            "Rest on your left side to release gas.",
        ],
    },
]

SMALL_DEFAULT = {
    "category": "small",
    "title": "Small issue",
    "advice": "This is a minor issue and should pass on its own.",
    "remedies": [
        "Rest for a few hours.",
        "Drink warm water and stay hydrated.",
        "Eat light food like khichdi or curd rice.",
        "Avoid oily, spicy, and junk food today.",
        "If it does not improve by tomorrow, see a doctor.",
    ],
}


COMMON_WORDS = {
    "the", "and", "have", "with", "pain", "my", "am", "is", "of", "to", "for", "on",
    "in", "since", "from", "day", "days", "yesterday", "today", "feel", "feeling",
    "been", "not", "it", "this", "that", "you", "are", "was", "were", "very", "just",
    "has", "had", "me", "but", "so", "because", "some", "what", "when", "where",
    "stomach", "head", "leg", "arm", "hand", "foot", "body", "doctor", "medicine",
    "problem", "issue", "sick", "tired", "tiredness", "dizzy", "dizziness", "fatigue",
    "weak", "weakness", "faint", "nausea", "chills", "joint", "muscle", "rash", "burn",
    "injury", "sprain", "swelling", "swollen", "rest", "drink", "water", "food", "eat",
    "having", "getting", "got", "get",
    "again", "after", "before", "now", "much", "more", "need", "please", "help",
    "started", "took", "taking", "last", "past", "since", "hour", "hours", "week",
    "month", "night", "morning", "while", "everything", "something", "anything",
}


def is_gibberish(text):
    words = re.findall(r"[a-z]+", text.lower())
    if not words:
        return True
    matches = sum(1 for w in words if w in COMMON_WORDS)
    return matches == 0


def get_remedy(problem):
    text = problem.lower()
    for condition in CONDITIONS:
        if any(k in text for k in condition["keywords"]):
            return condition["category"], condition["title"], condition["advice"], condition["remedies"]
    if is_gibberish(text):
        return "nonbio", "Not a medical issue", "This is not a medical problem.", []
    return SMALL_DEFAULT["category"], SMALL_DEFAULT["title"], SMALL_DEFAULT["advice"], SMALL_DEFAULT["remedies"]


def hospital_log():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [
        f"{now} CRITICAL ALERT sent to City General Hospital. Ambulance: 108.",
        f"{now} Emergency contacts notified (simulated).",
        f"{now} Ambulance dispatched via 108.",
        f"{now} Estimated cost 46350.00 exceeds cover 2000.00 - insurance offered.",
        f"{now} Hospital re-notified (City General Hospital).",
    ]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        problem = request.form.get("problem", "").strip()
        if problem:
            category, title, advice, remedy = get_remedy(problem)
            log = hospital_log() if category == "serious" else []
            # TODO: send `problem` to the next part (connect with the sign-in info later)
            print("Received problem:", problem, "->", title)
            return render_template_string(RESPONSE, problem=problem, remedy=remedy, category=category, title=title, advice=advice, log=log)
    return render_template_string(FORM)


if __name__ == "__main__":
    app.run(debug=True)
