"""
===============================================================================
 Health 360 - Merged App (sign-in + problem report + medical assistant)
===============================================================================
Combines three parts into ONE file:

  Part 1 (friend's): email/password sign-in, personal details, emergency
        contacts, insurance, hospital finder, profile view/edit.
  Part 2 (yours):    symptom report with quick-pick chips, immediate remedies,
        non-medical detection for gibberish / "love attack" etc.
  Part 3:            severity classification (low/medium/high/critical),
        home remedies with a reaction-time safety timer, automatic ambulance
        dispatch when the timer expires, hospital / contacts / insurance
        actions, full history, and a JSON API for external integration.

RUNNING
-------
    pip install flask
    python app.py
    then open http://127.0.0.1:5000
===============================================================================
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import threading
import time
import urllib.parse
import urllib.request
import uuid
import webbrowser
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import (Flask, jsonify, redirect, render_template,
                   request, session, url_for)


APP_NAME: str = "Health 360"
HOST: str = "127.0.0.1"
PORT: int = 5000
SECRET_KEY: str = "health360-merged-secret-change-me"

TIMER_MODE: str = "real"
INSURANCE_COVER_LIMIT: float = 2000.0
SWEEP_INTERVAL: float = 2.0


HOSPITAL_API_URL: str = ""
AMBULANCE_API_URL: str = ""
CONTACT_SMS_API_URL: str = ""

AMBULANCE_PHONE: str = "108"
DEFAULT_HOSPITAL: str = "City General Hospital"


SEVERITY_RULES: Dict[str, List[str]] = {
    "critical": [
        "unconscious", "not breathing", "no pulse", "severe bleeding", "heart attack",
        "chest pain", "stroke", "seizure", "overdose", "paralysis", "blue lips",
        "gasping", "suicidal", "drowning", "electrocution", "poison", "poisoning",
        "coughing blood", "severe burns",
    ],
    "high": [
        "high fever", "vomiting blood", "severe pain", "difficulty breathing",
        "swollen", "broken bone", "fracture", "blood in stool", "fainting",
        "blood in vomit", "fever 104", "blurry vision", "weakness one side",
        "heavy bleeding", "bleeding",
    ],
    "medium": [
        "fever", "headache", "stomach", "belly", "tummy", "nausea", "vomiting",
        "diarrhea", "cough", "throat", "pain", "rash", "allergy", "sneezing",
        "runny nose", "dizziness", "cold", "insect bite", "gastric", "gas",
        "acidity", "indigestion", "heartburn", "back", "balls", "testicl",
        "private", "genital",
    ],
    "nonbio": [
        "love attack", "broken heart", "heartbreak", "breakup", "love", "crush",
        "sad", "depress", "emotional", "stress",
    ],
}


@dataclass(frozen=True)
class Remedy:
    medicine: str
    dosage: str
    category: str
    reaction_minutes: int
    note: str
    price: float


@dataclass(frozen=True)
class RemedyRule:
    keywords: List[str]
    diagnosis: str
    remedy: Remedy


REMEDY_RULES: List[RemedyRule] = [
    RemedyRule(["headache", "head ache"], "Likely tension / mild headache",
               Remedy("Paracetamol (Acetaminophen)", "500 mg every 6 hours, max 3/day",
                      "Painkiller", 30, "Take with food and stay hydrated.", 45.0)),
    RemedyRule(["fever", "temperature", "body heat"], "Mild to moderate fever",
               Remedy("Ibuprofen (or Paracetamol)", "200 mg every 6-8 hours with food",
                      "Antipyretic", 30, "Drink plenty of fluids; monitor temperature.", 60.0)),
    RemedyRule(["cough", "throat"], "Cough / throat irritation",
               Remedy("Warm salt-water gargle + cough syrup", "Gargle every 4 hours; 1 tsp at bedtime",
                      "Soothing", 30, "Do not take with other cold medicines.", 95.0)),
    RemedyRule(["cold", "runny nose", "sneezing"], "Common cold / mild allergy",
               Remedy("Cetirizine (antihistamine)", "10 mg once daily",
                      "Antihistamine", 30, "May cause drowsiness - avoid driving.", 55.0)),
    RemedyRule(["stomach", "belly", "tummy", "indigestion"], "Indigestion / mild gastritis",
               Remedy("Antacid (Omeprazole)", "20 mg before breakfast",
                      "Antacid", 30, "Avoid spicy and oily food today. Eat khichdi or curd rice.", 70.0)),
    RemedyRule(["vomit", "nausea"], "Mild nausea / vomiting",
               Remedy("ORS + ginger tea", "Sip ORS slowly every 15 minutes",
                      "Rehydration", 30, "No solid food for a few hours. See a doctor if it lasts over 12 hours.", 40.0)),
    RemedyRule(["diarrhea"], "Mild gastroenteritis",
               Remedy("ORS + Loperamide", "ORS after each loose stool; 2 mg after first",
                      "Anti-diarrheal", 30, "Hydration is the priority.", 85.0)),
    RemedyRule(["gastric", "gas", "acidity", "heartburn"], "Gas / acidity",
               Remedy("Antacid + jeera water", "1 glass warm water + antacid as directed",
                      "Antacid", 30, "Walk slowly and rest on your left side.", 40.0)),
    RemedyRule(["dizz"], "Possible low blood pressure",
               Remedy("ORS + salty snack + rest", "Drink ORS and lie down",
                      "Rehydration", 30, "Rise slowly from sitting.", 30.0)),
    RemedyRule(["back", "backache"], "Back pain",
               Remedy("Warm compress + Paracetamol", "500 mg every 6 hours; warm pack 15 min",
                      "Painkiller", 30, "Rest on a hard surface; avoid bending and heavy lifting.", 60.0)),
    RemedyRule(["balls", "testicl", "private", "genital"], "Private area pain",
               Remedy("Cold pack + rest", "Cold pack 15 minutes at a time",
                      "Soothing", 30, "Wear loose underwear. If sharp or over a day, see a doctor now.", 50.0)),
    RemedyRule(["allergy", "rash", "insect bite"], "Mild allergic reaction",
               Remedy("Cetirizine + calamine lotion", "10 mg once; apply lotion on rash",
                      "Antihistamine", 30, "If hives spread or lips swell, call emergency.", 90.0)),
    RemedyRule(["tired", "fatigue", "tiredness"], "General fatigue / dehydration",
               Remedy("Hydration + glucose + rest", "500 ml ORS + 2 tbsp glucose",
                      "Rehydration", 30, "Have a light meal and rest.", 25.0)),
    RemedyRule(["stress", "insomnia"], "Mild stress / poor sleep",
               Remedy("Warm milk + deep breathing", "One glass before bed",
                      "Relaxation", 30, "Avoid screens 30 minutes before sleep.", 20.0)),
]

NONBIO_REMEDIES: List[str] = [
    "Talk to a close friend or family member about how you feel.",
    "Take a walk or do light exercise to clear your mind.",
    "Listen to music or watch something you enjoy.",
    "Write down your thoughts in a journal.",
    "Focus on a hobby like sports, drawing, or reading.",
    "If feelings do not improve, talk to a counselor.",
]

COST_BY_SEVERITY: Dict[str, float] = {
    "low": 150.0, "medium": 450.0, "high": 2800.0, "critical": 45000.0,
}


@dataclass
class Contact:
    name: str
    phone: str
    relation: str
    email: str = ""


@dataclass
class Patient:
    id: str
    email: str
    password: str
    salt: str
    name: str = ""
    age: int = 0
    gender: str = ""
    height: float = 0.0
    weight_kg: float = 0.0
    blood_group: str = "Unknown"
    phone: str = ""
    location: str = ""
    allergies: List[str] = field(default_factory=list)
    contacts: List[Contact] = field(default_factory=list)
    illness_actual: str = ""
    illness_chronic: str = ""
    medications: str = ""
    insurance: str = ""
    not_covered: str = ""
    uncovered_list: str = ""
    created_at: str = ""
    episodes: List[str] = field(default_factory=list)
    profile_complete: bool = False


@dataclass
class Episode:
    id: str
    patient_id: str
    symptoms: List[str]
    severity: str
    diagnosis: str
    remedy: Optional[Dict[str, Any]]
    est_cost: float
    status: str
    created_at: str
    deadline_ts: Optional[float]
    insurance_status: str = "not_applicable"
    actions: List[Dict[str, str]] = field(default_factory=list)


class Store:
    def __init__(self) -> None:
        self._lock: threading.Lock = threading.Lock()
        self.patients: Dict[str, Patient] = {}
        self.episodes: Dict[str, Episode] = {}
        self.email_index: Dict[str, str] = {}

    def add_patient(self, patient: Patient) -> None:
        with self._lock:
            self.patients[patient.id] = patient
            self.email_index[patient.email.lower()] = patient.id

    def add_episode(self, episode: Episode) -> None:
        with self._lock:
            self.episodes[episode.id] = episode
            self.patients[episode.patient_id].episodes.append(episode.id)

    def get_patient(self, pid: str) -> Optional[Patient]:
        with self._lock:
            return self.patients.get(pid)

    def get_episode(self, eid: str) -> Optional[Episode]:
        with self._lock:
            return self.episodes.get(eid)

    def find_by_email(self, email: str) -> Optional[Patient]:
        with self._lock:
            pid = self.email_index.get(email.lower())
            return self.patients.get(pid) if pid else None

    def patient_history(self, pid: str) -> List[Episode]:
        with self._lock:
            patient = self.patients.get(pid)
            if patient is None:
                return []
            return [self.episodes[e] for e in patient.episodes if e in self.episodes]


STORE: Store = Store()


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _timestamp() -> float:
    return time.time()


def _clean_symptoms(raw: str) -> List[str]:
    parts = [p.strip().lower() for p in raw.replace("\n", ",").split(",")]
    return [p for p in parts if p]


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", email))


def make_salt() -> str:
    return secrets.token_hex(16)


def hash_password(pw: str, salt: str) -> str:
    return hashlib.sha256((salt + ":" + pw).encode()).hexdigest()


def verify_password(pw: str, salt: str, hashed: str) -> bool:
    return hash_password(pw, salt) == hashed


COMMON_WORDS: set = {
    "the", "and", "have", "with", "pain", "my", "am", "is", "of", "to", "for", "on",
    "in", "since", "from", "day", "days", "yesterday", "today", "feel", "feeling",
    "been", "not", "it", "this", "that", "you", "are", "was", "were", "very", "just",
    "has", "had", "me", "but", "so", "because", "some", "what", "when", "where",
    "stomach", "head", "leg", "arm", "hand", "foot", "body", "doctor", "medicine",
    "problem", "issue", "sick", "tired", "tiredness", "dizzy", "dizziness", "fatigue",
    "weak", "weakness", "faint", "nausea", "chills", "joint", "muscle", "rash", "burn",
    "injury", "sprain", "swelling", "swollen", "rest", "drink", "water", "food", "eat",
    "having", "getting", "got", "get", "again", "after", "before", "now", "much",
    "more", "need", "please", "help", "started", "took", "taking", "last", "past",
    "hour", "hours", "week", "month", "night", "morning", "while", "everything",
    "something", "anything",
}


def is_gibberish(text: str) -> bool:
    words = re.findall(r"[a-z]+", text.lower())
    if not words:
        return True
    matches = sum(1 for w in words if w in COMMON_WORDS)
    return matches == 0


def assess_severity(symptoms: List[str]) -> str:
    text = " ".join(symptoms)
    for level in ("critical", "high", "medium", "nonbio"):
        if any(kw in text for kw in SEVERITY_RULES[level]):
            return level
    return "low"


def find_remedy(symptoms: List[str]) -> Optional[Remedy]:
    text = " ".join(symptoms)
    for rule in REMEDY_RULES:
        if any(kw in text for kw in rule.keywords):
            return rule.remedy
    return None


def diagnosis_for(symptoms: List[str]) -> str:
    text = " ".join(symptoms)
    critical_map = [
        (["chest pain", "heart attack"], "Possible cardiac event - emergency medical help required"),
        (["unconscious", "not breathing", "no pulse", "gasping"], "Cardiac / respiratory arrest - emergency"),
        (["severe bleeding", "bleeding", "coughing blood", "vomiting blood", "blood in stool"],
         "Active bleeding - emergency attention required"),
        (["stroke", "paralysis", "weakness one side", "blurry vision"], "Possible stroke - emergency"),
        (["seizure"], "Seizure - emergency care required"),
        (["overdose", "poison", "poisoning"], "Poisoning / overdose - emergency"),
        (["suicidal"], "Mental health crisis - emergency support required"),
        (["drowning", "electrocution", "severe burns"], "Life-threatening injury - emergency"),
    ]
    for kws, diag in critical_map:
        if any(kw in text for kw in kws):
            return diag
    for rule in REMEDY_RULES:
        if any(kw in text for kw in rule.keywords):
            return rule.diagnosis
    return "General symptoms - advice given below"


def estimate_cost(severity: str, symptom_count: int) -> float:
    base = COST_BY_SEVERITY.get(severity, 150.0)
    return round(base * (1 + 0.03 * symptom_count), 2)


def reaction_delay_seconds(remedy: Optional[Remedy]) -> float:
    minutes = remedy.reaction_minutes if remedy else 30
    if TIMER_MODE == "fast":
        return float(minutes)
    return float(minutes) * 60.0


def patient_to_json(patient: Patient) -> Dict[str, Any]:
    return {
        "id": patient.id, "email": patient.email, "name": patient.name,
        "age": patient.age, "gender": patient.gender,
        "height": patient.height, "weight_kg": patient.weight_kg,
        "blood_group": patient.blood_group, "phone": patient.phone,
        "location": patient.location, "allergies": patient.allergies,
        "contacts": [{"name": c.name, "phone": c.phone, "relation": c.relation, "email": c.email}
                     for c in patient.contacts],
        "insurance": patient.insurance, "created_at": patient.created_at,
        "episodes": patient.episodes,
    }


def episode_to_json(episode: Episode) -> Dict[str, Any]:
    return {
        "id": episode.id, "patient_id": episode.patient_id,
        "symptoms": episode.symptoms, "severity": episode.severity,
        "diagnosis": episode.diagnosis, "remedy": episode.remedy,
        "estimated_cost": episode.est_cost,
        "insurance_status": episode.insurance_status,
        "status": episode.status, "created_at": episode.created_at,
        "deadline_ts": episode.deadline_ts, "actions": episode.actions,
    }


def notify_external(kind: str, payload: Dict[str, Any]) -> None:
    urls = {"hospital": HOSPITAL_API_URL, "contacts": CONTACT_SMS_API_URL,
            "ambulance": AMBULANCE_API_URL}
    url = urls.get(kind, "")
    if url:
        try:
            _post_json(url, payload)
            print(f"[integration] POST {kind} -> {url} OK")
        except Exception as exc:
            print(f"[integration] POST {kind} -> {url} FAILED: {exc}")
    else:
        print(f"[simulated] {kind.upper()} notification sent (plug INTEGRATION URLS): {payload}")


def _post_json(url: str, payload: Dict[str, Any]) -> None:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5):
        pass


def _base_payload(patient: Patient, episode: Episode) -> Dict[str, Any]:
    return {
        "event": "medical_assistance",
        "patient": patient_to_json(patient),
        "episode": episode_to_json(episode),
        "severity": episode.severity,
        "hospital": DEFAULT_HOSPITAL,
        "ambulance_phone": AMBULANCE_PHONE,
    }


app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.after_request
def _cors_headers(response: Any) -> Any:
    if request.path.startswith("/api"):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/<path:_>", methods=["OPTIONS"])
def _api_options(_: str) -> Any:
    return ("", 204, {"Access-Control-Allow-Origin": "*",
                      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                      "Access-Control-Allow-Headers": "Content-Type"})


def _current_patient() -> Optional[Patient]:
    return STORE.get_patient(session.get("patient_id", ""))


@app.route("/")
def home() -> Any:
    patient = _current_patient()
    if patient:
        return redirect(url_for("dashboard"))
    return render_template("index.html", flash=None)


@app.route("/signin", methods=["GET", "POST"])
def signin() -> Any:
    err = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        user = STORE.find_by_email(email)
        if user is None:
            err = "No account found with this email. Please create an account first."
        elif not verify_password(pw, user.salt, user.password):
            err = "Incorrect password."
        else:
            session["patient_id"] = user.id
            return redirect(url_for("profile" if user.profile_complete else "details"))
    return render_template("signin.html", flash=err)


@app.route("/register", methods=["GET", "POST"])
def register() -> Any:
    err = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pw = request.form.get("password", "")
        pw2 = request.form.get("password2", "")
        if not is_valid_email(email):
            err = "Enter a valid email address (e.g. name@example.com)."
        elif len(pw) < 6:
            err = "Password must be at least 6 characters."
        elif pw != pw2:
            err = "Passwords do not match."
        elif STORE.find_by_email(email):
            err = "An account with this email already exists. Please sign in."
        else:
            salt = make_salt()
            patient = Patient(id=uuid.uuid4().hex[:10], email=email,
                              password=hash_password(pw, salt), salt=salt,
                              created_at=_now())
            STORE.add_patient(patient)
            session["patient_id"] = patient.id
            return redirect(url_for("details"))
    return render_template("register.html", flash=err)


@app.route("/details", methods=["GET", "POST"])
def details() -> Any:
    patient = _current_patient()
    if patient is None:
        return redirect(url_for("home"))
    err = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "0").strip()
        gender = request.form.get("gender", "").strip()
        height = request.form.get("height", "0").strip()
        weight = request.form.get("weight", "0").strip()
        blood = request.form.get("blood", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()

        contacts: List[Contact] = []
        for i in range(1, 7):
            cname = request.form.get(f"c{i}_name", "").strip()
            crel = request.form.get(f"c{i}_rel", "").strip()
            cphone = request.form.get(f"c{i}_phone", "").strip()
            cemail = request.form.get(f"c{i}_email", "").strip()
            if cname and cphone:
                contacts.append(Contact(cname, cphone, crel or "Emergency", cemail))

        if not name:
            err = "Full name is required."
        elif not age.isdigit() or not (0 <= int(age) <= 150):
            err = "Enter a valid age."
        elif not gender:
            err = "Select a gender."
        elif not height.replace(".", "").isdigit() or float(height) <= 0:
            err = "Enter a valid height."
        elif not weight.replace(".", "").isdigit() or float(weight) <= 0:
            err = "Enter a valid weight."
        elif not re.fullmatch(r"\d{1,15}", phone):
            err = "Phone number must contain digits only (max 15)."
        elif not location:
            err = "Location is required."
        elif not contacts:
            err = "Please add at least one emergency contact."
        else:
            patient.name = name
            patient.age = int(age)
            patient.gender = gender
            patient.height = float(height)
            patient.weight_kg = float(weight)
            patient.blood_group = blood or "Unknown"
            patient.phone = phone
            patient.location = location
            patient.contacts = contacts
            patient.allergies = [a.strip() for a in request.form.get("allergies", "").split(",") if a.strip()]
            patient.illness_actual = request.form.get("illnessActual", "").strip()
            patient.illness_chronic = request.form.get("illnessChronic", "").strip()
            patient.medications = request.form.get("medications", "").strip()
            patient.profile_complete = True
            return redirect(url_for("insurance"))
    existing_contacts = [{"name": c.name, "rel": c.rel, "phone": c.phone, "email": c.email}
                         for c in patient.contacts]
    return render_template("details.html", patient=patient,
                           flash=err, existing_contacts=existing_contacts)


@app.route("/insurance", methods=["GET", "POST"])
def insurance() -> Any:
    patient = _current_patient()
    if patient is None:
        return redirect(url_for("home"))
    err = None
    if request.method == "POST":
        ins = request.form.get("insurance", "").strip()
        not_covered = request.form.get("notCovered", "")
        if not ins:
            err = "Insurance company name is required."
        elif not_covered not in ("Yes", "No"):
            err = "Please answer the coverage question."
        else:
            patient.insurance = ins
            patient.not_covered = not_covered
            patient.uncovered_list = request.form.get("notCoveredList", "").strip() if not_covered == "Yes" else ""
            return redirect(url_for("dashboard"))
    return render_template("insurance.html", patient=patient, flash=err)


@app.route("/logout")
def logout() -> Any:
    session.clear()
    return redirect(url_for("home"))


@app.route("/profile")
def profile() -> Any:
    patient = _current_patient()
    if patient is None:
        return redirect(url_for("home"))
    return render_template("profile.html", patient=patient)


@app.route("/dashboard")
def dashboard() -> Any:
    patient = _current_patient()
    if patient is None:
        return redirect(url_for("home"))
    return render_template("dashboard.html", patient=patient)


@app.route("/episode/new", methods=["POST"])
def new_episode() -> Any:
    patient = _current_patient()
    if patient is None:
        return redirect(url_for("home"))
    symptoms = _clean_symptoms(request.form.get("symptoms", ""))
    if not symptoms:
        return redirect(url_for("dashboard"))
    severity = assess_severity(symptoms)
    if severity == "nonbio" or (is_gibberish(" ".join(symptoms)) and severity == "low"):
        severity = "nonbio"
    remedy = find_remedy(symptoms) if severity != "nonbio" else None
    diagnosis = diagnosis_for(symptoms) if severity != "nonbio" else "Not a biological / medical issue"
    cost = estimate_cost(severity, len(symptoms))

    if severity == "nonbio":
        episode = Episode(
            id=uuid.uuid4().hex[:10], patient_id=patient.id, symptoms=symptoms,
            severity="nonbio", diagnosis=diagnosis, remedy=None, est_cost=0.0,
            status="advice_given", created_at=_now(), deadline_ts=None,
        )
        episode.actions.append({"ts": _now(), "type": "assess",
                                "message": f"Symptoms: {', '.join(symptoms)} | Not a medical issue"})
        episode.actions.append({"ts": _now(), "type": "advice",
                                "message": "Emotional / non-medical advice given."})
        STORE.add_episode(episode)
        return redirect(url_for("episode_page", eid=episode.id))

    remedy_dict = {"medicine": remedy.medicine, "dosage": remedy.dosage,
                   "reaction_minutes": remedy.reaction_minutes, "note": remedy.note,
                   "price": remedy.price} if remedy else None

    episode = Episode(
        id=uuid.uuid4().hex[:10], patient_id=patient.id, symptoms=symptoms,
        severity=severity, diagnosis=diagnosis, remedy=remedy_dict,
        est_cost=cost,
        status="remedy_active" if severity in ("low", "medium") else "hospital_notified",
        created_at=_now(),
        deadline_ts=_timestamp() + reaction_delay_seconds(remedy)
        if remedy and severity in ("low", "medium") else None,
    )

    episode.actions.append({"ts": _now(), "type": "assess",
                            "message": f"Symptoms: {', '.join(symptoms)} | Severity: {severity.upper()}"})
    if severity in ("low", "medium") and remedy:
        episode.actions.append({"ts": _now(), "type": "remedy",
                                "message": f"Prescribed {remedy.medicine} ({remedy.dosage}). "
                                           f"Reaction window: ~{remedy.reaction_minutes} min."})
    if severity in ("high", "critical"):
        episode.actions.append({"ts": _now(), "type": "hospital",
                                "message": f"CRITICAL ALERT sent to {DEFAULT_HOSPITAL}. "
                                           f"Ambulance: {AMBULANCE_PHONE}."})
        episode.actions.append({"ts": _now(), "type": "contacts",
                                "message": "Emergency contacts notified (simulated)."})
        notify_external("hospital", _base_payload(patient, episode))
        notify_external("contacts", _base_payload(patient, episode))
    if severity == "critical":
        episode.actions.append({"ts": _now(), "type": "ambulance",
                                "message": f"Ambulance dispatched via {AMBULANCE_PHONE}."})
        episode.status = "ambulance_dispatched"
        notify_external("ambulance", _base_payload(patient, episode))
    if cost > INSURANCE_COVER_LIMIT and severity in ("high", "critical"):
        episode.insurance_status = "offered"
        episode.actions.append({"ts": _now(), "type": "insurance",
                                "message": f"Estimated cost {cost:.2f} exceeds cover "
                                           f"{INSURANCE_COVER_LIMIT:.2f} - insurance offered."})

    STORE.add_episode(episode)
    return redirect(url_for("episode_page", eid=episode.id))


@app.route("/episode/<eid>")
def episode_page(eid: str) -> Any:
    patient = _current_patient()
    episode = STORE.get_episode(eid)
    if patient is None or episode is None or episode.patient_id != patient.id:
        return redirect(url_for("home"))
    _auto_ambulance_sweep(episode)
    return render_template("episode.html", patient=patient,
                           episode=episode, cover=INSURANCE_COVER_LIMIT)


@app.route("/episode/<eid>/resolve", methods=["POST"])
def resolve_episode(eid: str) -> Any:
    episode = _owned_episode(eid)
    if episode and episode.status == "remedy_active":
        episode.status = "resolved"
        episode.deadline_ts = None
        episode.actions.append({"ts": _now(), "type": "resolve",
                                "message": "Patient confirmed the remedy worked. Problem resolved."})
    return redirect(url_for("episode_page", eid=eid))


@app.route("/episode/<eid>/ambulance", methods=["POST"])
def ambulance_episode(eid: str) -> Any:
    episode = _owned_episode(eid)
    if episode and episode.status != "resolved":
        patient = STORE.get_patient(episode.patient_id)
        episode.status = "ambulance_dispatched"
        episode.deadline_ts = None
        episode.actions.append({"ts": _now(), "type": "ambulance",
                                "message": f"AMBULANCE dispatched via {AMBULANCE_PHONE}."})
        if patient:
            notify_external("ambulance", _base_payload(patient, episode))
    return redirect(url_for("episode_page", eid=eid))


@app.route("/episode/<eid>/hospital", methods=["POST"])
def hospital_episode(eid: str) -> Any:
    episode = _owned_episode(eid)
    if episode:
        patient = STORE.get_patient(episode.patient_id)
        episode.actions.append({"ts": _now(), "type": "hospital",
                                "message": f"Hospital re-notified ({DEFAULT_HOSPITAL})."})
        if patient:
            notify_external("hospital", _base_payload(patient, episode))
    return redirect(url_for("episode_page", eid=eid))


@app.route("/episode/<eid>/contacts", methods=["POST"])
def contacts_episode(eid: str) -> Any:
    episode = _owned_episode(eid)
    if episode:
        patient = STORE.get_patient(episode.patient_id)
        episode.actions.append({"ts": _now(), "type": "contacts",
                                "message": "Emergency contacts re-called (simulated)."})
        if patient:
            notify_external("contacts", _base_payload(patient, episode))
    return redirect(url_for("episode_page", eid=eid))


@app.route("/episode/<eid>/insurance", methods=["POST"])
def insurance_episode(eid: str) -> Any:
    episode = _owned_episode(eid)
    if episode:
        choice = request.form.get("choice", "no")
        episode.insurance_status = "applied" if choice == "yes" else "declined"
        episode.actions.append({"ts": _now(), "type": "insurance",
                                "message": "Insurance application submitted." if choice == "yes"
                                else "Patient declined insurance."})
    return redirect(url_for("episode_page", eid=eid))


@app.route("/episode/<eid>/advance", methods=["POST"])
def advance_timer(eid: str) -> Any:
    episode = _owned_episode(eid)
    if episode:
        episode.deadline_ts = _timestamp() - 1
    return redirect(url_for("episode_page", eid=eid))


@app.route("/history")
def history() -> Any:
    patient = _current_patient()
    if patient is None:
        return redirect(url_for("home"))
    episodes = sorted(STORE.patient_history(patient.id),
                      key=lambda e: e.created_at, reverse=True)
    return render_template("history.html", patient=patient, episodes=episodes)


def _owned_episode(eid: str) -> Optional[Episode]:
    patient = _current_patient()
    episode = STORE.get_episode(eid)
    if patient is None or episode is None or episode.patient_id != patient.id:
        return None
    return episode


def _auto_ambulance_sweep(episode: Episode) -> None:
    if (episode.status == "remedy_active" and episode.deadline_ts
            and _timestamp() >= episode.deadline_ts):
        patient = STORE.get_patient(episode.patient_id)
        episode.status = "ambulance_dispatched"
        episode.deadline_ts = None
        episode.actions.append({"ts": _now(), "type": "ambulance",
                                "message": "Remedy did NOT work within the reaction window - "
                                           f"AMBULANCE auto-dispatched ({AMBULANCE_PHONE})."})
        if patient:
            notify_external("ambulance", _base_payload(patient, episode))


def background_sweeper() -> None:
    while True:
        time.sleep(SWEEP_INTERVAL)
        for eid in list(STORE.episodes):
            episode = STORE.get_episode(eid)
            if episode:
                _auto_ambulance_sweep(episode)


@app.route("/api/health")
def api_health() -> Any:
    return jsonify({"service": APP_NAME, "status": "ok", "time": _now(),
                    "insurance_cover_limit": INSURANCE_COVER_LIMIT})


@app.route("/api/contract")
def api_contract() -> Any:
    return jsonify({
        "app": APP_NAME, "version": "1.0",
        "severity_values": ["low", "medium", "high", "critical", "nonbio"],
        "endpoints": {
            "assess_symptoms": {"method": "POST", "path": "/api/severity",
                                "body": {"symptoms": ["chest pain"], "patient_id": "optional"}},
            "create_patient": {"method": "POST", "path": "/api/patients",
                               "body": {"name": "...", "age": 30, "contacts": []}},
            "get_patient": {"method": "GET", "path": "/api/patients/<id>"},
            "get_history": {"method": "GET", "path": "/api/patients/<id>/history"},
            "get_episode": {"method": "GET", "path": "/api/episodes/<id>"},
            "trigger_action": {"method": "POST", "path": "/api/episodes/<id>/actions",
                               "body": {"action": "ambulance|hospital|contacts|resolve|insurance",
                                        "choice": "yes|no"}},
        },
        "webhooks_we_call": {
            "HOSPITAL_API_URL": "POST patient + severity when severity is high/critical",
            "CONTACT_SMS_API_URL": "POST emergency contacts when severity is high/critical",
            "AMBULANCE_API_URL": "POST when user hits emergency, timer expires, or severity critical",
        },
    })


@app.route("/api/patients", methods=["POST"])
def api_create_patient() -> Any:
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip()
    if not email:
        return jsonify({"error": "email is required"}), 400
    if STORE.find_by_email(email):
        return jsonify({"error": "email already exists"}), 400
    salt = make_salt()
    contacts = [Contact(str(c.get("name", "")), str(c.get("phone", "")),
                        str(c.get("relation", "")), str(c.get("email", "")))
                for c in data.get("contacts", [])]
    patient = Patient(
        id=uuid.uuid4().hex[:10], email=email,
        password=hash_password(str(data.get("password", "")), salt), salt=salt,
        name=str(data.get("name", "")), age=int(data.get("age", 0) or 0),
        weight_kg=float(data.get("weight_kg", 0) or 0),
        blood_group=str(data.get("blood_group", "Unknown")),
        allergies=[str(a) for a in data.get("allergies", [])],
        contacts=contacts, created_at=_now())
    STORE.add_patient(patient)
    return jsonify(patient_to_json(patient)), 201


@app.route("/api/severity", methods=["POST"])
def api_severity() -> Any:
    data = request.get_json(silent=True) or {}
    symptoms = [str(s).lower() for s in data.get("symptoms", [])]
    if not symptoms:
        return jsonify({"error": "symptoms are required"}), 400
    severity = assess_severity(symptoms)
    if severity == "nonbio" or (is_gibberish(" ".join(symptoms)) and severity == "low"):
        severity = "nonbio"
    remedy = find_remedy(symptoms) if severity != "nonbio" else None
    diagnosis = diagnosis_for(symptoms) if severity != "nonbio" else "Not a biological / medical issue"
    cost = estimate_cost(severity, len(symptoms))
    payload = {
        "severity": severity, "diagnosis": diagnosis,
        "estimated_cost": cost,
        "insurance_needed": cost > INSURANCE_COVER_LIMIT,
        "recommendation": ("IMMEDIATE HOSPITAL" if severity in ("high", "critical")
                           else "home remedy"),
        "remedy": {"medicine": remedy.medicine, "dosage": remedy.dosage,
                   "reaction_minutes": remedy.reaction_minutes,
                   "note": remedy.note} if remedy else None,
        "action": ("hospital" if severity in ("high", "critical") else "remedy"),
    }
    if data.get("patient_id"):
        p = STORE.get_patient(data["patient_id"])
        payload["patient"] = patient_to_json(p) if p else None
    return jsonify(payload)


@app.route("/api/patients/<pid>")
def api_patient(pid: str) -> Any:
    patient = STORE.get_patient(pid)
    if patient is None:
        return jsonify({"error": "patient not found"}), 404
    return jsonify(patient_to_json(patient))


@app.route("/api/patients/<pid>/history")
def api_history(pid: str) -> Any:
    patient = STORE.get_patient(pid)
    if patient is None:
        return jsonify({"error": "patient not found"}), 404
    episodes = sorted(STORE.patient_history(pid), key=lambda e: e.created_at, reverse=True)
    return jsonify([episode_to_json(e) for e in episodes])


@app.route("/api/episodes/<eid>")
def api_episode(eid: str) -> Any:
    episode = STORE.get_episode(eid)
    if episode is None:
        return jsonify({"error": "episode not found"}), 404
    return jsonify(episode_to_json(episode))


@app.route("/api/episodes/<eid>/actions", methods=["POST"])
def api_episode_action(eid: str) -> Any:
    episode = STORE.get_episode(eid)
    if episode is None:
        return jsonify({"error": "episode not found"}), 404
    data = request.get_json(silent=True) or {}
    if isinstance(data, str):
        action = data.strip().lower()
        data = {}
    else:
        action = str(data.get("action", "")).strip().lower()
    patient = STORE.get_patient(episode.patient_id)
    if action == "ambulance":
        episode.status = "ambulance_dispatched"
        episode.deadline_ts = None
        episode.actions.append({"ts": _now(), "type": "ambulance",
                                "message": "Ambulance dispatched via API."})
        notify_external("ambulance", _base_payload(patient, episode) if patient else {})
    elif action == "hospital":
        episode.actions.append({"ts": _now(), "type": "hospital",
                                "message": "Hospital notified via API."})
        notify_external("hospital", _base_payload(patient, episode) if patient else {})
    elif action == "contacts":
        episode.actions.append({"ts": _now(), "type": "contacts",
                                "message": "Emergency contacts called via API."})
        notify_external("contacts", _base_payload(patient, episode) if patient else {})
    elif action == "resolve":
        episode.status = "resolved"
        episode.deadline_ts = None
        episode.actions.append({"ts": _now(), "type": "resolve",
                                "message": "Resolved via API."})
    elif action == "insurance":
        choice = data.get("choice", "no") if isinstance(data, dict) else "no"
        episode.insurance_status = "applied" if choice == "yes" else "declined"
        episode.actions.append({"ts": _now(), "type": "insurance",
                                "message": "Insurance handled via API."})
    else:
        return jsonify({"error": f"unknown action '{action}'"}), 400
    return jsonify(episode_to_json(episode))


def _http_get_json(url: str, timeout: int = 25) -> Optional[Dict[str, Any]]:
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Health360App/1.0 (local demo)",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _geocode(location: str) -> Optional[List[float]]:
    data = _http_get_json(
        "https://nominatim.openstreetmap.org/search?format=json&limit=1&q="
        + urllib.parse.quote(location))
    if data and len(data) > 0:
        return [float(data[0]["lat"]), float(data[0]["lon"])]
    data = _http_get_json(
        "https://photon.komoot.io/api/?q=" + urllib.parse.quote(location) + "&limit=1")
    if data and data.get("features"):
        c = data["features"][0]["geometry"]["coordinates"]
        return [float(c[1]), float(c[0])]
    return None


def _find_hospitals_near(lat: float, lon: float) -> List[Dict[str, Any]]:
    seen: Dict[str, Dict[str, Any]] = {}

    def add(h: Dict[str, Any]) -> None:
        if not h.get("name"):
            return
        key = h["name"].strip().lower()
        if key in seen:
            return
        seen[key] = h

    for osm_tag in ("amenity:hospital", "healthcare"):
        url = ("https://photon.komoot.io/api/?q=hospital&lat={}&lon={}"
               "&limit=25&osm_tag={}").format(lat, lon, osm_tag)
        data = _http_get_json(url)
        if not data:
            continue
        for f in data.get("features", []):
            p = f.get("properties", {}) or {}
            g = f.get("geometry", {}) or {}
            coords = g.get("coordinates") or []
            add({
                "name": p.get("name", ""),
                "street": p.get("street", ""),
                "city": p.get("city", "") or p.get("locality", "") or p.get("county", ""),
                "postcode": p.get("postcode", ""),
                "lat": coords[1] if len(coords) > 1 else None,
                "lon": coords[0] if len(coords) > 0 else None,
            })
    return list(seen.values())[:25]


@app.route("/api/hospitals")
def api_hospitals() -> Any:
    location = request.args.get("location", "").strip()
    if not location:
        return jsonify({"error": "Location is required", "hospitals": []}), 400
    coords = _geocode(location)
    if not coords:
        return jsonify({"error": f"Could not locate '{location}'. "
                                 "Try a more specific location (e.g. 'Mumbai, Maharashtra').",
                        "hospitals": []}), 404
    hospitals = _find_hospitals_near(coords[0], coords[1])
    return jsonify({
        "location": location, "lat": coords[0], "lon": coords[1],
        "count": len(hospitals), "hospitals": hospitals,
    })


def main() -> None:
    print(f"[{APP_NAME}] starting on http://{HOST}:{PORT}")
    print(f"[{APP_NAME}] Timer mode: {'fast (seconds, demo)' if TIMER_MODE == 'fast' else 'real (minutes, production)'}")
    threading.Thread(target=background_sweeper, daemon=True, name="ambulance-sweeper").start()
    threading.Timer(1.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
