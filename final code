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

from __future__ import annotations  # lets newer-style type hints work on older Python

# ---------------------------------------------------------------------------
# IMPORTING THE TOOLS WE NEED
# ---------------------------------------------------------------------------
# These lines load extra code that other people wrote, so we do not have to
# build everything ourselves. "hashlib" scrambles passwords, "json" saves and
# loads data, "threading" lets several things run at once, "urllib" talks to
# the internet, and "flask" is the tool that makes the website.

import hashlib  # a tool for scrambling (hashing) passwords safely
import json  # a tool for saving/loading data and sending data as JSON
import re  # a tool for finding patterns in text (like email checking)
import secrets  # a tool for making random secret text (used for password salt)
import threading  # a tool that lets several things run at the same time
import time  # a tool for reading the clock and pausing the app
import urllib.parse  # a tool for making safe web addresses (URLs)
import urllib.request  # a tool for downloading data from the internet
import uuid  # a tool for making random unique ID numbers
import webbrowser  # a tool that opens a web browser
from dataclasses import dataclass, field  # tools that let us create simple data containers
from datetime import datetime  # a tool for working with dates and times
from typing import Any, Dict, List, Optional  # type names so the code explains its own data

from flask import (Flask, jsonify, redirect, render_template,  # the website tool (Flask) parts we use
                   request, session, url_for)  # more Flask parts: reading forms, logins, page links

# ---------------------------------------------------------------------------
# 1. CONFIGURATION  (the app's basic settings - change these to change the app)
# ---------------------------------------------------------------------------

# The name of the app, shown on the website and in the terminal.
APP_NAME: str = "Health 360"  # the app's display name
# Which address and port number the website runs on (your own computer).
HOST: str = "127.0.0.1"  # the address of your own computer
PORT: int = 5000  # the "door" (port) the website is served on
# A secret key the app uses to keep logins and sessions safe.
SECRET_KEY: str = "health360-merged-secret-change-me"  # the key that protects login sessions

# "fast" = the remedy timer runs in SECONDS (great for showing off the demo).
# "real" = the timer runs in MINUTES (what you would use in real life).
TIMER_MODE: str = "fast"  # which timer speed to use ("fast" or "real")
# The most money insurance will pay for one illness episode (in rupees).
INSURANCE_COVER_LIMIT: float = 2000.0  # insurance max payout per episode (rupees)
# How often (in seconds) the app checks whether a remedy timer has run out.
SWEEP_INTERVAL: float = 2.0  # seconds between background timer checks

# ---------------------------------------------------------------------------
# 2. INTEGRATION HOOKS (friends replace these with their endpoints)
# ---------------------------------------------------------------------------

# If your friend gives you a real website address (URL) to put here, the app
# will actually SEND the alert to that address. If left empty, the app just
# prints a pretend message in the terminal instead.
HOSPITAL_API_URL: str = ""  # URL for alerting a hospital (leave empty for demo)
AMBULANCE_API_URL: str = ""  # URL for calling an ambulance service (leave empty for demo)
CONTACT_SMS_API_URL: str = ""  # URL for sending SMS to emergency contacts (empty for demo)

# The phone number to call for an ambulance, and the hospital mentioned in
# the alerts. (Your friend can change these to the real ones.)
AMBULANCE_PHONE: str = "108"  # the ambulance phone number used in alerts
DEFAULT_HOSPITAL: str = "City General Hospital"  # the hospital name used in alerts

# ---------------------------------------------------------------------------
# 3. KNOWLEDGE BASE  (severity + remedies merged from all parts)
# ---------------------------------------------------------------------------

# The word lists below are how the app decides how serious a problem is.
#   "critical" = call emergency / ambulance right now.
#   "high"     = go to hospital now.
#   "medium"   = use a home remedy and keep an eye on it.
#   "nonbio"   = NOT a medical issue (love problems, sadness, etc.).
SEVERITY_RULES: Dict[str, List[str]] = {  # the master word lists, one list per severity level
    "critical": [  # words that mean: life-threatening emergency
        "unconscious", "not breathing", "no pulse", "severe bleeding", "heart attack",  # emergency words
        "chest pain", "stroke", "seizure", "overdose", "paralysis", "blue lips",  # more emergency words
        "gasping", "suicidal", "drowning", "electrocution", "poison", "poisoning",  # more emergency words
        "coughing blood", "severe burns",  # more emergency words
    ],
    "high": [  # words that mean: must go to hospital soon
        "high fever", "vomiting blood", "severe pain", "difficulty breathing",  # serious words
        "swollen", "broken bone", "fracture", "blood in stool", "fainting",  # serious words
        "blood in vomit", "fever 104", "blurry vision", "weakness one side",  # serious words
        "heavy bleeding", "bleeding",  # serious words
    ],
    "medium": [  # words that mean: mild problem, use a home remedy
        "fever", "headache", "stomach", "belly", "tummy", "nausea", "vomiting",  # mild words
        "diarrhea", "cough", "throat", "pain", "rash", "allergy", "sneezing",  # mild words
        "runny nose", "dizziness", "cold", "insect bite", "gastric", "gas",  # mild words
        "acidity", "indigestion", "heartburn", "back", "balls", "testicl",  # mild words
        "private", "genital",  # mild words
    ],
    "nonbio": [  # words that mean: NOT a medical problem (feelings, love, stress)
        "love attack", "broken heart", "heartbreak", "breakup", "love", "crush",  # feeling words
        "sad", "depress", "emotional", "stress",  # feeling words
    ],
}


# A "Remedy" is ONE home treatment. It holds the medicine name, how to take
# it, what type of medicine it is, how many minutes to wait for it to work,
# extra advice, and the price in rupees.
@dataclass(frozen=True)  # this makes Remedy a simple, fixed data container
class Remedy:  # the shape of one home remedy
    medicine: str  # the medicine's name
    dosage: str  # how to take it (how much and how often)
    category: str  # what type of medicine it is (painkiller, antacid...)
    reaction_minutes: int  # how many minutes to wait before it should work
    note: str  # extra advice for the user
    price: float  # the price in rupees


# A "RemedyRule" links certain trigger words (keywords) to a short diagnosis
# and a Remedy. Example: if the user types "headache", we show the headache
# diagnosis and the headache remedy.
@dataclass(frozen=True)  # this makes RemedyRule a simple, fixed data container
class RemedyRule:  # the shape of one rule linking words to a remedy
    keywords: List[str]  # the trigger words that match this rule
    diagnosis: str  # the short explanation to show the user
    remedy: Remedy  # the remedy to give for these words


# This is the big list of all the home remedies the app knows. Each entry has
# trigger words, a short explanation, and the full remedy to show the user.
REMEDY_RULES: List[RemedyRule] = [  # the full list of remedy rules
    RemedyRule(["headache", "head ache"], "Likely tension / mild headache",  # rule for headaches
               Remedy("Paracetamol (Acetaminophen)", "500 mg every 6 hours, max 3/day",  # the medicine
                      "Painkiller", 30, "Take with food and stay hydrated.", 45.0)),  # type, minutes, note, price
    RemedyRule(["fever", "temperature", "body heat"], "Mild to moderate fever",  # rule for fever
               Remedy("Ibuprofen (or Paracetamol)", "200 mg every 6-8 hours with food",  # the medicine
                      "Antipyretic", 30, "Drink plenty of fluids; monitor temperature.", 60.0)),  # details
    RemedyRule(["cough", "throat"], "Cough / throat irritation",  # rule for cough
               Remedy("Warm salt-water gargle + cough syrup", "Gargle every 4 hours; 1 tsp at bedtime",  # the medicine
                      "Soothing", 30, "Do not take with other cold medicines.", 95.0)),  # details
    RemedyRule(["cold", "runny nose", "sneezing"], "Common cold / mild allergy",  # rule for cold
               Remedy("Cetirizine (antihistamine)", "10 mg once daily",  # the medicine
                      "Antihistamine", 20, "May cause drowsiness - avoid driving.", 55.0)),  # details
    RemedyRule(["stomach", "belly", "tummy", "indigestion"], "Indigestion / mild gastritis",  # rule for stomach
               Remedy("Antacid (Omeprazole)", "20 mg before breakfast",  # the medicine
                      "Antacid", 20, "Avoid spicy and oily food today. Eat khichdi or curd rice.", 70.0)),  # details
    RemedyRule(["vomit", "nausea"], "Mild nausea / vomiting",  # rule for vomiting
               Remedy("ORS + ginger tea", "Sip ORS slowly every 15 minutes",  # the medicine
                      "Rehydration", 25, "No solid food for a few hours. See a doctor if it lasts over 12 hours.", 40.0)),  # details
    RemedyRule(["diarrhea"], "Mild gastroenteritis",  # rule for diarrhea
               Remedy("ORS + Loperamide", "ORS after each loose stool; 2 mg after first",  # the medicine
                      "Anti-diarrheal", 30, "Hydration is the priority.", 85.0)),  # details
    RemedyRule(["gastric", "gas", "acidity", "heartburn"], "Gas / acidity",  # rule for gas
               Remedy("Antacid + jeera water", "1 glass warm water + antacid as directed",  # the medicine
                      "Antacid", 20, "Walk slowly and rest on your left side.", 40.0)),  # details
    RemedyRule(["dizz"], "Possible low blood pressure",  # rule for dizziness
               Remedy("ORS + salty snack + rest", "Drink ORS and lie down",  # the medicine
                      "Rehydration", 20, "Rise slowly from sitting.", 30.0)),  # details
    RemedyRule(["back", "backache"], "Back pain",  # rule for back pain
               Remedy("Warm compress + Paracetamol", "500 mg every 6 hours; warm pack 15 min",  # the medicine
                      "Painkiller", 30, "Rest on a hard surface; avoid bending and heavy lifting.", 60.0)),  # details
    RemedyRule(["balls", "testicl", "private", "genital"], "Private area pain",  # rule for private-area pain
               Remedy("Cold pack + rest", "Cold pack 15 minutes at a time",  # the medicine
                      "Soothing", 30, "Wear loose underwear. If sharp or over a day, see a doctor now.", 50.0)),  # details
    RemedyRule(["allergy", "rash", "insect bite"], "Mild allergic reaction",  # rule for allergies
               Remedy("Cetirizine + calamine lotion", "10 mg once; apply lotion on rash",  # the medicine
                      "Antihistamine", 20, "If hives spread or lips swell, call emergency.", 90.0)),  # details
    RemedyRule(["tired", "fatigue", "tiredness"], "General fatigue / dehydration",  # rule for tiredness
               Remedy("Hydration + glucose + rest", "500 ml ORS + 2 tbsp glucose",  # the medicine
                      "Rehydration", 30, "Have a light meal and rest.", 25.0)),  # details
    RemedyRule(["stress", "insomnia"], "Mild stress / poor sleep",  # rule for stress
               Remedy("Warm milk + deep breathing", "One glass before bed",  # the medicine
                      "Relaxation", 20, "Avoid screens 30 minutes before sleep.", 20.0)),  # details
]

# Advice shown when the app decides the problem is NOT a medical issue
# (for example a broken heart or a bad day).
NONBIO_REMEDIES: List[str] = [  # advice tips for non-medical problems
    "Talk to a close friend or family member about how you feel.",  # tip one
    "Take a walk or do light exercise to clear your mind.",  # tip two
    "Listen to music or watch something you enjoy.",  # tip three
    "Write down your thoughts in a journal.",  # tip four
    "Focus on a hobby like sports, drawing, or reading.",  # tip five
    "If feelings do not improve, talk to a counselor.",  # tip six
]

# Rough hospital bill amount (in rupees) for each severity level. The app uses
# this to decide whether the bill is bigger than the insurance cover.
COST_BY_SEVERITY: Dict[str, float] = {  # average treatment cost per severity
    "low": 150.0, "medium": 450.0, "high": 2800.0, "critical": 45000.0,  # costs per level
}

# ---------------------------------------------------------------------------
# 4. DATA MODEL  (the shapes of the data the app stores)
# ---------------------------------------------------------------------------

# A "Contact" is one emergency contact: their name, phone number, relation to
# the patient (like "mother"), and email.
@dataclass  # this makes Contact a simple data container
class Contact:  # the shape of one emergency contact
    name: str  # the contact's name
    phone: str  # the contact's phone number
    relation: str  # how they are related to the patient (mother, friend...)
    email: str = ""  # the contact's email (optional, empty by default)


# A "Patient" is one user's whole profile: login details, personal info
# (age, height, weight, blood group...), emergency contacts, insurance info,
# and a list of the IDs of all their past episodes.
@dataclass  # this makes Patient a simple data container
class Patient:  # the shape of one user's whole profile
    id: str  # the patient's unique ID
    email: str  # the patient's login email
    password: str  # the scrambled (hashed) password
    salt: str  # the random text added to the password before hashing
    name: str = ""  # the patient's full name (empty until filled in)
    age: int = 0  # the patient's age
    gender: str = ""  # the patient's gender
    height: float = 0.0  # the patient's height
    weight_kg: float = 0.0  # the patient's weight in kilograms
    blood_group: str = "Unknown"  # the patient's blood group
    phone: str = ""  # the patient's phone number
    location: str = ""  # the patient's city/area
    allergies: List[str] = field(default_factory=list)  # a list of known allergies
    contacts: List[Contact] = field(default_factory=list)  # the list of emergency contacts
    illness_actual: str = ""  # current/recent illness description
    illness_chronic: str = ""  # any long-term (chronic) illness description
    medications: str = ""  # medicines the patient already takes
    insurance: str = ""  # the insurance company name
    not_covered: str = ""  # whether some treatments are not covered (Yes/No)
    uncovered_list: str = ""  # which treatments are not covered
    created_at: str = ""  # when the account was created
    episodes: List[str] = field(default_factory=list)  # IDs of all this patient's episodes
    profile_complete: bool = False  # True once personal details are filled in


# An "Episode" is one illness/incident report: which symptoms the user had,
# how serious it was, the remedy that was given, the estimated cost, what
# happened after (actions log), and whether insurance was used.
@dataclass  # this makes Episode a simple data container
class Episode:  # the shape of one illness report
    id: str  # the episode's unique ID
    patient_id: str  # which patient this episode belongs to
    symptoms: List[str]  # the list of symptoms the user typed
    severity: str  # the severity level (low/medium/high/critical/nonbio)
    diagnosis: str  # the short explanation of the problem
    remedy: Optional[Dict[str, Any]]  # the remedy details (or None if none)
    est_cost: float  # the estimated treatment cost
    status: str  # what stage this episode is at (remedy_active, resolved...)
    created_at: str  # when the episode was created
    deadline_ts: Optional[float]  # the timer deadline (time number) or None
    insurance_status: str = "not_applicable"  # offered/applied/declined/not_applicable
    actions: List[Dict[str, str]] = field(default_factory=list)  # the timeline of what happened


# The "Store" is the app's memory. It keeps every patient and every episode in
# dictionaries (like address books) so the app can look them up quickly.
# The "lock" makes sure only one thing changes the memory at a time, so the
# app does not crash even if several people use it at once.
class Store:  # the app's in-memory storage box
    def __init__(self) -> None:  # sets up a new empty Store
        self._lock: threading.Lock = threading.Lock()  # a lock so only one change at a time
        self.patients: Dict[str, Patient] = {}  # address book of patients by ID
        self.episodes: Dict[str, Episode] = {}  # address book of episodes by ID
        self.email_index: Dict[str, str] = {}  # quick lookup from email to patient ID

    # Add a new patient to the address book (and remember their email too).
    def add_patient(self, patient: Patient) -> None:  # saves a new patient
        with self._lock:  # lock the memory while saving
            self.patients[patient.id] = patient  # store the patient under their ID
            self.email_index[patient.email.lower()] = patient.id  # remember their email too

    # Save a new episode and attach it to the patient's list of episodes.
    def add_episode(self, episode: Episode) -> None:  # saves a new episode
        with self._lock:  # lock the memory while saving
            self.episodes[episode.id] = episode  # store the episode under its ID
            self.patients[episode.patient_id].episodes.append(episode.id)  # add ID to that patient's list

    # Look up one patient by their id.
    def get_patient(self, pid: str) -> Optional[Patient]:  # finds a patient by ID
        with self._lock:  # lock the memory while reading
            return self.patients.get(pid)  # return the patient, or None if not found

    # Look up one episode by its id.
    def get_episode(self, eid: str) -> Optional[Episode]:  # finds an episode by ID
        with self._lock:  # lock the memory while reading
            return self.episodes.get(eid)  # return the episode, or None if not found

    # Look up a patient by their email address (used when signing in).
    def find_by_email(self, email: str) -> Optional[Patient]:  # finds a patient by email
        with self._lock:  # lock the memory while reading
            pid = self.email_index.get(email.lower())  # look up the ID for this email
            return self.patients.get(pid) if pid else None  # return the patient, or None

    # Return all episodes that belong to one patient.
    def patient_history(self, pid: str) -> List[Episode]:  # returns a patient's episode list
        with self._lock:  # lock the memory while reading
            patient = self.patients.get(pid)  # find the patient
            if patient is None:  # if no such patient
                return []  # return an empty list
            return [self.episodes[e] for e in patient.episodes if e in self.episodes]  # gather their episodes


# This creates the one shared memory box that the whole app uses.
STORE: Store = Store()  # the app's one shared storage box

# ---------------------------------------------------------------------------
# 5. HELPERS  (small reusable functions used everywhere in the app)
# ---------------------------------------------------------------------------

# Returns the current date and time as text (e.g. "2026-08-07 14:30:00").
def _now() -> str:  # helper: gives the current date and time as text
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # format the current moment nicely


# Returns the current time as a number (used for counting seconds).
def _timestamp() -> float:  # helper: gives the current time as a big number
    return time.time()  # seconds since 1970 (used for the timer)


# Turns what the user typed into a clean list of symptoms.
# Example: "Chest Pain, fever" becomes ["chest pain", "fever"].
def _clean_symptoms(raw: str) -> List[str]:  # helper: cleans the typed symptoms
    parts = [p.strip().lower() for p in raw.replace("\n", ",").split(",")]  # split on commas, tidy each part
    return [p for p in parts if p]  # drop any empty parts and return the list


# Checks if an email address looks like a real email (like name@example.com).
def is_valid_email(email: str) -> bool:  # helper: checks an email looks real
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$", email))  # match the email pattern, return True/False


# --- Password safety ---
# A "salt" is a random extra text added to the password before saving it.
def make_salt() -> str:  # helper: makes a random salt string
    return secrets.token_hex(16)  # a random 16-byte text for extra password safety


# Scrambles the password + salt into a hash. The real password is NEVER stored.
def hash_password(pw: str, salt: str) -> str:  # helper: scrambles a password
    return hashlib.sha256((salt + ":" + pw).encode()).hexdigest()  # hash the salt+password into a code


# Checks a typed password against the stored hash (True if it matches).
def verify_password(pw: str, salt: str, hashed: str) -> bool:  # helper: checks a typed password
    return hash_password(pw, salt) == hashed  # scramble it again and compare to the stored one


# These are everyday English words. If the user's message contains NONE of
# them, the app thinks the message is nonsense (gibberish), not real symptoms.
COMMON_WORDS: set = {  # normal everyday words used to spot nonsense
    "the", "and", "have", "with", "pain", "my", "am", "is", "of", "to", "for", "on",  # common words
    "in", "since", "from", "day", "days", "yesterday", "today", "feel", "feeling",  # common words
    "been", "not", "it", "this", "that", "you", "are", "was", "were", "very", "just",  # common words
    "has", "had", "me", "but", "so", "because", "some", "what", "when", "where",  # common words
    "stomach", "head", "leg", "arm", "hand", "foot", "body", "doctor", "medicine",  # common words
    "problem", "issue", "sick", "tired", "tiredness", "dizzy", "dizziness", "fatigue",  # common words
    "weak", "weakness", "faint", "nausea", "chills", "joint", "muscle", "rash", "burn",  # common words
    "injury", "sprain", "swelling", "swollen", "rest", "drink", "water", "food", "eat",  # common words
    "having", "getting", "got", "get", "again", "after", "before", "now", "much",  # common words
    "more", "need", "please", "help", "started", "took", "taking", "last", "past",  # common words
    "hour", "hours", "week", "month", "night", "morning", "while", "everything",  # common words
    "something", "anything",  # common words
}


# Returns True if the text looks like random nonsense, not real English.
def is_gibberish(text: str) -> bool:  # helper: checks if text is nonsense
    words = re.findall(r"[a-z]+", text.lower())  # find all real words in the text
    if not words:  # if there are no words at all
        return True  # treat it as nonsense
    matches = sum(1 for w in words if w in COMMON_WORDS)  # count how many words are everyday words
    return matches == 0  # if NONE are everyday words, it is nonsense


# THE HEART OF THE APP: reads the symptoms and picks a severity level
# (critical / high / medium / nonbio / low) using the word lists above.
def assess_severity(symptoms: List[str]) -> str:  # the main "how serious?" function
    text = " ".join(symptoms)  # join all symptoms into one sentence
    for level in ("critical", "high", "medium", "nonbio"):  # check the levels in order
        if any(kw in text for kw in SEVERITY_RULES[level]):  # if any keyword of this level appears
            return level  # return that severity level
    return "low"  # if nothing matches, it's a mild/low problem


# Looks through the remedy list and returns a remedy if the symptoms match
# one of the keyword groups (e.g. "headache" -> the paracetamol remedy).
def find_remedy(symptoms: List[str]) -> Optional[Remedy]:  # helper: finds a matching remedy
    text = " ".join(symptoms)  # join all symptoms into one sentence
    for rule in REMEDY_RULES:  # go through every remedy rule
        if any(kw in text for kw in rule.keywords):  # if a rule's keyword appears
            return rule.remedy  # return that rule's remedy
    return None  # no match: return nothing


# Picks a short sentence explaining what the symptoms might be.
def diagnosis_for(symptoms: List[str]) -> str:  # helper: makes a diagnosis sentence
    text = " ".join(symptoms)  # join all symptoms into one sentence
    # Special serious-diagnosis messages for emergency conditions.
    critical_map = [  # a list of serious conditions and their messages
        (["chest pain", "heart attack"], "Possible cardiac event - emergency medical help required"),  # heart problem message
        (["unconscious", "not breathing", "no pulse", "gasping"], "Cardiac / respiratory arrest - emergency"),  # arrest message
        (["severe bleeding", "bleeding", "coughing blood", "vomiting blood", "blood in stool"],  # bleeding keywords
         "Active bleeding - emergency attention required"),  # bleeding message
        (["stroke", "paralysis", "weakness one side", "blurry vision"], "Possible stroke - emergency"),  # stroke message
        (["seizure"], "Seizure - emergency care required"),  # seizure message
        (["overdose", "poison", "poisoning"], "Poisoning / overdose - emergency"),  # poisoning message
        (["suicidal"], "Mental health crisis - emergency support required"),  # crisis message
        (["drowning", "electrocution", "severe burns"], "Life-threatening injury - emergency"),  # injury message
    ]
    for kws, diag in critical_map:  # check each serious condition
        if any(kw in text for kw in kws):  # if one of its keywords appears
            return diag  # return its message
    # Otherwise use the diagnosis that came with the matching remedy rule.
    for rule in REMEDY_RULES:  # go through every remedy rule
        if any(kw in text for kw in rule.keywords):  # if a rule's keyword appears
            return rule.diagnosis  # return that rule's diagnosis
    return "General symptoms - advice given below"  # nothing matched: general message


# Guesses how much hospital treatment might cost, based on severity and how
# many symptoms the user typed (more symptoms = slightly more expensive).
def estimate_cost(severity: str, symptom_count: int) -> float:  # helper: guesses the bill
    base = COST_BY_SEVERITY.get(severity, 150.0)  # get the base cost for this severity
    return round(base * (1 + 0.03 * symptom_count), 2)  # add a little for each symptom and round


# How long the app waits for the remedy to work before calling an ambulance.
# In "fast" mode this is just the number of minutes as seconds (so 30 = 30
# seconds, great for the demo). In "real" mode 30 = 30 minutes.
def reaction_delay_seconds(remedy: Optional[Remedy]) -> float:  # helper: how long to wait for a remedy
    minutes = remedy.reaction_minutes if remedy else 30  # get the wait minutes (30 if no remedy)
    if TIMER_MODE == "fast":  # if we are in demo (fast) mode
        return float(minutes)  # return seconds = number of minutes (demo speed)
    return float(minutes) * 60.0  # otherwise real mode: minutes turned into seconds


# Turns a Patient into a plain dictionary so it can be sent as JSON (the text
# format other apps/websites use to talk to each other).
def patient_to_json(patient: Patient) -> Dict[str, Any]:  # helper: turns a patient into JSON-friendly data
    return {  # build the plain dictionary of the patient
        "id": patient.id, "email": patient.email, "name": patient.name,  # basic info
        "age": patient.age, "gender": patient.gender,  # basic info
        "height": patient.height, "weight_kg": patient.weight_kg,  # body info
        "blood_group": patient.blood_group, "phone": patient.phone,  # body info
        "location": patient.location, "allergies": patient.allergies,  # address and allergies
        "contacts": [{"name": c.name, "phone": c.phone, "relation": c.relation, "email": c.email}  # each contact as data
                     for c in patient.contacts],  # for every contact in the list
        "insurance": patient.insurance, "created_at": patient.created_at,  # insurance and date
        "episodes": patient.episodes,  # the episode ID list
    }


# Turns an Episode into a plain dictionary (same idea as above, for episodes).
def episode_to_json(episode: Episode) -> Dict[str, Any]:  # helper: turns an episode into JSON-friendly data
    return {  # build the plain dictionary of the episode
        "id": episode.id, "patient_id": episode.patient_id,  # IDs
        "symptoms": episode.symptoms, "severity": episode.severity,  # symptoms and severity
        "diagnosis": episode.diagnosis, "remedy": episode.remedy,  # diagnosis and remedy
        "estimated_cost": episode.est_cost,  # the cost estimate
        "insurance_status": episode.insurance_status,  # insurance state
        "status": episode.status, "created_at": episode.created_at,  # status and date
        "deadline_ts": episode.deadline_ts, "actions": episode.actions,  # timer deadline and log
    }


# Sends an alert to an outside system (hospital / ambulance / SMS app). If no
# real URL is set, it just prints a pretend message in the terminal so you can
# see what WOULD have been sent.
def notify_external(kind: str, payload: Dict[str, Any]) -> None:  # helper: sends an outside alert
    urls = {"hospital": HOSPITAL_API_URL, "contacts": CONTACT_SMS_API_URL,  # which URL goes to which kind
            "ambulance": AMBULANCE_API_URL}  # more kinds to URLs
    url = urls.get(kind, "")  # pick the URL for this kind of alert
    if url:  # if a real URL was set
        try:  # try to send it
            _post_json(url, payload)  # actually send the data
            print(f"[integration] POST {kind} -> {url} OK")  # tell the terminal it worked
        except Exception as exc:  # if sending failed
            print(f"[integration] POST {kind} -> {url} FAILED: {exc}")  # tell the terminal it failed
    else:  # no URL set (demo mode)
        print(f"[simulated] {kind.upper()} notification sent (plug INTEGRATION URLS): {payload}")  # print a pretend message


# The actual code that sends the data to a URL as JSON.
def _post_json(url: str, payload: Dict[str, Any]) -> None:  # helper: posts JSON to a URL
    req = urllib.request.Request(  # build the request
        url,  # where to send it
        data=json.dumps(payload).encode("utf-8"),  # turn the payload into JSON bytes
        headers={"Content-Type": "application/json"},  # tell the server it is JSON
        method="POST",  # use the POST sending method
    )
    with urllib.request.urlopen(req, timeout=5):  # send it and wait up to 5 seconds
        pass  # we don't need the reply


# Builds the standard bundle of info (patient + episode + hospital details)
# that gets sent to outside systems when an alert fires.
def _base_payload(patient: Patient, episode: Episode) -> Dict[str, Any]:  # helper: the standard alert bundle
    return {  # build the bundle
        "event": "medical_assistance",  # what type of event this is
        "patient": patient_to_json(patient),  # the patient info
        "episode": episode_to_json(episode),  # the episode info
        "severity": episode.severity,  # how serious
        "hospital": DEFAULT_HOSPITAL,  # which hospital
        "ambulance_phone": AMBULANCE_PHONE,  # ambulance number
    }


# ---------------------------------------------------------------------------
# 6. FLASK APP  (the web server that runs the whole website)
# ---------------------------------------------------------------------------

# Create the Flask app (the engine of the website) and give it its secret key.
app = Flask(__name__)  # create the website engine
app.secret_key = SECRET_KEY  # give it the secret key for safe sessions


# Lets other websites call our API. (CORS = the browser rule that decides
# which websites are allowed to talk to each other.)
@app.after_request  # run this after every request leaves the server
def _cors_headers(response: Any) -> Any:  # adds the CORS permission headers
    if request.path.startswith("/api"):  # only for API addresses
        response.headers["Access-Control-Allow-Origin"] = "*"  # allow any website to call us
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"  # allowed request types
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"  # allowed headers
    return response  # send the response on its way


# Answers the browser's quick "can I call you?" check that comes before a real
# API call.
@app.route("/api/<path:_>", methods=["OPTIONS"])  # a route that catches the pre-check calls
def _api_options(_: str) -> Any:  # replies to that pre-check
    return ("", 204, {"Access-Control-Allow-Origin": "*",  # empty reply with permission headers
                      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",  # allowed methods
                      "Access-Control-Allow-Headers": "Content-Type"})  # allowed headers


# Returns the user who is logged in right now (from the browser's session).
def _current_patient() -> Optional[Patient]:  # helper: who is logged in now
    return STORE.get_patient(session.get("patient_id", ""))  # look up the session's patient ID


# --------------------------- Auth / sign-in (part 1) ------------------------
# These are the pages for signing up, logging in, entering personal details,
# and the insurance info. (This was the friend's part of the app.)

# The front page. If the user is already logged in, skip straight to the
# dashboard instead.
@app.route("/")  # the address of the front page
def home() -> Any:  # the front page function
    patient = _current_patient()  # check who is logged in
    if patient:  # if someone is logged in
        return redirect(url_for("dashboard"))  # jump straight to the dashboard
    return render_template("index.html", flash=None)  # otherwise show the landing page


# The login page. On a POST it checks the email + password. If correct, it
# starts a session and sends the user to their profile (or details if their
# profile is not finished yet).
@app.route("/signin", methods=["GET", "POST"])  # the login page address
def signin() -> Any:  # the login page function
    err = None  # no error yet
    if request.method == "POST":  # if the form was submitted
        email = request.form.get("email", "").strip()  # read the typed email
        pw = request.form.get("password", "")  # read the typed password
        user = STORE.find_by_email(email)  # look up the account by email
        if user is None:  # no account with this email
            err = "No account found with this email. Please create an account first."  # show this error
        elif not verify_password(pw, user.salt, user.password):  # password does not match
            err = "Incorrect password."  # show this error
        else:  # email and password are correct
            session["patient_id"] = user.id  # log the user in (remember their ID)
            return redirect(url_for("profile" if user.profile_complete else "details"))  # go to profile or details
    return render_template("signin.html", flash=err)  # show the login page (with error if any)


# The sign-up page. On a POST it checks the email and password, creates a new
# account, logs the user in, and sends them to the details page.
@app.route("/register", methods=["GET", "POST"])  # the sign-up page address
def register() -> Any:  # the sign-up page function
    err = None  # no error yet
    if request.method == "POST":  # if the form was submitted
        email = request.form.get("email", "").strip()  # read the typed email
        pw = request.form.get("password", "")  # read the typed password
        pw2 = request.form.get("password2", "")  # read the typed "confirm password"
        if not is_valid_email(email):  # email does not look real
            err = "Enter a valid email address (e.g. name@example.com)."  # show this error
        elif len(pw) < 6:  # password too short
            err = "Password must be at least 6 characters."  # show this error
        elif pw != pw2:  # the two passwords do not match
            err = "Passwords do not match."  # show this error
        elif STORE.find_by_email(email):  # this email already has an account
            err = "An account with this email already exists. Please sign in."  # show this error
        else:  # all checks passed
            # Everything looks good: make a random salt, scramble the password,
            # save the new patient, and log them in.
            salt = make_salt()  # make a random salt
            patient = Patient(id=uuid.uuid4().hex[:10], email=email,  # make the new patient with a random ID
                              password=hash_password(pw, salt), salt=salt,  # store the scrambled password + salt
                              created_at=_now())  # note the creation time
            STORE.add_patient(patient)  # save the new patient
            session["patient_id"] = patient.id  # log them in
            return redirect(url_for("details"))  # send them to the details page
    return render_template("register.html", flash=err)  # show the sign-up page (with error if any)


# The personal details page - name, age, gender, height, weight, blood group,
# phone, location, allergies, and up to 6 emergency contacts. On a POST it
# saves all of it to the patient profile.
@app.route("/details", methods=["GET", "POST"])  # the details page address
def details() -> Any:  # the details page function
    patient = _current_patient()  # who is logged in
    if patient is None:  # nobody logged in
        return redirect(url_for("home"))  # send them to the front page
    err = None  # no error yet
    if request.method == "POST":  # if the form was submitted
        name = request.form.get("name", "").strip()  # read the name
        age = request.form.get("age", "0").strip()  # read the age
        gender = request.form.get("gender", "").strip()  # read the gender
        height = request.form.get("height", "0").strip()  # read the height
        weight = request.form.get("weight", "0").strip()  # read the weight
        blood = request.form.get("blood", "").strip()  # read the blood group
        phone = request.form.get("phone", "").strip()  # read the phone number
        location = request.form.get("location", "").strip()  # read the location

        # Loop 6 times to read up to 6 emergency contacts from the form
        # (c1_..., c2_..., c3_... and so on). Only contacts with both a name
        # and a phone number are kept.
        contacts: List[Contact] = []  # empty list to collect the contacts
        for i in range(1, 7):  # repeat for contact slots 1 to 6
            cname = request.form.get(f"c{i}_name", "").strip()  # read this contact's name
            crel = request.form.get(f"c{i}_rel", "").strip()  # read this contact's relation
            cphone = request.form.get(f"c{i}_phone", "").strip()  # read this contact's phone
            cemail = request.form.get(f"c{i}_email", "").strip()  # read this contact's email
            if cname and cphone:  # only keep it if it has a name and phone
                contacts.append(Contact(cname, cphone, crel or "Emergency", cemail))  # add it to the list

        # A long list of "if" checks that make sure the answers are sensible
        # before saving. If anything is wrong, show an error instead.
        if not name:  # name is empty
            err = "Full name is required."  # show this error
        elif not age.isdigit() or not (0 <= int(age) <= 150):  # age is not a proper number
            err = "Enter a valid age."  # show this error
        elif not gender:  # gender not chosen
            err = "Select a gender."  # show this error
        elif not height.replace(".", "").isdigit() or float(height) <= 0:  # height is not a valid number
            err = "Enter a valid height."  # show this error
        elif not weight.replace(".", "").isdigit() or float(weight) <= 0:  # weight is not a valid number
            err = "Enter a valid weight."  # show this error
        elif not re.fullmatch(r"\d{1,15}", phone):  # phone has non-digit characters
            err = "Phone number must contain digits only (max 15)."  # show this error
        elif not location:  # location is empty
            err = "Location is required."  # show this error
        elif not contacts:  # no emergency contacts added
            err = "Please add at least one emergency contact."  # show this error
        else:  # all checks passed
            # All checks passed: save everything onto the patient profile.
            patient.name = name  # save the name
            patient.age = int(age)  # save the age (as a number)
            patient.gender = gender  # save the gender
            patient.height = float(height)  # save the height (as a number)
            patient.weight_kg = float(weight)  # save the weight (as a number)
            patient.blood_group = blood or "Unknown"  # save the blood group
            patient.phone = phone  # save the phone
            patient.location = location  # save the location
            patient.contacts = contacts  # save the emergency contacts list
            patient.allergies = [a.strip() for a in request.form.get("allergies", "").split(",") if a.strip()]  # save allergies
            patient.illness_actual = request.form.get("illnessActual", "").strip()  # save current illness
            patient.illness_chronic = request.form.get("illnessChronic", "").strip()  # save chronic illness
            patient.medications = request.form.get("medications", "").strip()  # save medications
            patient.profile_complete = True  # mark the profile as complete
            return redirect(url_for("insurance"))  # go to the insurance page
    # When just showing the page (GET), pass the contacts that were already
    # saved so the form can be filled in again if the user edits it.
    existing_contacts = [{"name": c.name, "rel": c.rel, "phone": c.phone, "email": c.email}  # get saved contacts
                         for c in patient.contacts]  # for every saved contact
    return render_template("details.html", patient=patient,  # show the details page
                           flash=err, existing_contacts=existing_contacts)  # with error and saved contacts


# The insurance page - which insurance company the user has and whether every
# treatment is covered. On a POST it saves the answers.
@app.route("/insurance", methods=["GET", "POST"])  # the insurance page address
def insurance() -> Any:  # the insurance page function
    patient = _current_patient()  # who is logged in
    if patient is None:  # nobody logged in
        return redirect(url_for("home"))  # send them to the front page
    err = None  # no error yet
    if request.method == "POST":  # if the form was submitted
        ins = request.form.get("insurance", "").strip()  # read the insurance company
        not_covered = request.form.get("notCovered", "")  # read the coverage answer
        if not ins:  # company name empty
            err = "Insurance company name is required."  # show this error
        elif not_covered not in ("Yes", "No"):  # coverage answer missing
            err = "Please answer the coverage question."  # show this error
        else:  # all checks passed
            patient.insurance = ins  # save the insurance company
            patient.not_covered = not_covered  # save the coverage answer
            patient.uncovered_list = request.form.get("notCoveredList", "").strip() if not_covered == "Yes" else ""  # save uncovered list
            return redirect(url_for("dashboard"))  # go to the dashboard
    return render_template("insurance.html", patient=patient, flash=err)  # show the insurance page


# Log out - clears the session so the browser no longer knows who is logged in.
@app.route("/logout")  # the logout address
def logout() -> Any:  # the logout function
    session.clear()  # forget who is logged in
    return redirect(url_for("home"))  # go back to the front page


# The profile page - shows all the saved details of the logged-in user.
@app.route("/profile")  # the profile page address
def profile() -> Any:  # the profile page function
    patient = _current_patient()  # who is logged in
    if patient is None:  # nobody logged in
        return redirect(url_for("home"))  # send them to the front page
    return render_template("profile.html", patient=patient)  # show the profile page


# --------------------------- Problem report (part 2 + 3) --------------------
# These pages handle reporting symptoms and everything that happens next
# (remedies, timers, ambulance, hospital, insurance, history).

# The main page where the user types their symptoms. It has quick-pick chips
# that fill the text box when clicked.
@app.route("/dashboard")  # the dashboard address
def dashboard() -> Any:  # the dashboard page function
    patient = _current_patient()  # who is logged in
    if patient is None:  # nobody logged in
        return redirect(url_for("home"))  # send them to the front page
    return render_template("dashboard.html", patient=patient)  # show the dashboard page


# THE most important part: called when the user submits their symptoms.
# It decides the severity, picks a remedy, may alert the hospital/ambulance,
# and saves the whole thing as an "episode" (one illness report).
@app.route("/episode/new", methods=["POST"])  # the address that receives the symptom form
def new_episode() -> Any:  # the function that handles a new symptom report
    patient = _current_patient()  # who is logged in
    if patient is None:  # nobody logged in
        return redirect(url_for("home"))  # send them to the front page
    symptoms = _clean_symptoms(request.form.get("symptoms", ""))  # clean the typed symptoms
    if not symptoms:  # nothing was typed
        return redirect(url_for("dashboard"))  # send them back to the dashboard
    # Decide how serious it is. Nonsense text or love/stress words become
    # "nonbio" (not a medical issue).
    severity = assess_severity(symptoms)  # pick a severity level
    if severity == "nonbio" or (is_gibberish(" ".join(symptoms)) and severity == "low"):  # nonsense or feelings
        severity = "nonbio"  # treat it as not a medical issue
    remedy = find_remedy(symptoms) if severity != "nonbio" else None  # find a remedy (if medical)
    diagnosis = diagnosis_for(symptoms) if severity != "nonbio" else "Not a biological / medical issue"  # get diagnosis
    cost = estimate_cost(severity, len(symptoms))  # estimate the cost

    # If it is NOT a medical issue, save a simple "advice" episode and show it.
    if severity == "nonbio":  # not a medical problem
        episode = Episode(  # make the episode
            id=uuid.uuid4().hex[:10], patient_id=patient.id, symptoms=symptoms,  # IDs and symptoms
            severity="nonbio", diagnosis=diagnosis, remedy=None, est_cost=0.0,  # details for nonbio
            status="advice_given", created_at=_now(), deadline_ts=None,  # no timer needed
        )
        episode.actions.append({"ts": _now(), "type": "assess",  # log the assessment step
                                "message": f"Symptoms: {', '.join(symptoms)} | Not a medical issue"})  # log message
        episode.actions.append({"ts": _now(), "type": "advice",  # log the advice step
                                "message": "Emotional / non-medical advice given."})  # log message
        STORE.add_episode(episode)  # save the episode
        return redirect(url_for("episode_page", eid=episode.id))  # show the episode page

    # Turn the remedy object into a plain dictionary so it can be saved.
    remedy_dict = {"medicine": remedy.medicine, "dosage": remedy.dosage,  # save remedy basics
                   "reaction_minutes": remedy.reaction_minutes, "note": remedy.note,  # save wait time and note
                   "price": remedy.price} if remedy else None  # save price (or None if no remedy)

    # Create the episode. For low/medium it starts a remedy timer. For
    # high/critical it goes straight to "hospital notified".
    episode = Episode(  # make the episode
        id=uuid.uuid4().hex[:10], patient_id=patient.id, symptoms=symptoms,  # IDs and symptoms
        severity=severity, diagnosis=diagnosis, remedy=remedy_dict,  # severity, diagnosis, remedy
        est_cost=cost,  # the cost estimate
        status="remedy_active" if severity in ("low", "medium") else "hospital_notified",  # starting status
        created_at=_now(),  # creation time
        deadline_ts=_timestamp() + reaction_delay_seconds(remedy)  # timer = now + wait time
        if remedy and severity in ("low", "medium") else None,  # only if there is a remedy timer
    )

    # The lines below build a timeline ("actions log") of everything done.
    episode.actions.append({"ts": _now(), "type": "assess",  # log the assessment step
                            "message": f"Symptoms: {', '.join(symptoms)} | Severity: {severity.upper()}"})  # log message
    if severity in ("low", "medium") and remedy:  # if it's a mild case with a remedy
        episode.actions.append({"ts": _now(), "type": "remedy",  # log the remedy step
                                "message": f"Prescribed {remedy.medicine} ({remedy.dosage}). "  # log the medicine
                                           f"Reaction window: ~{remedy.reaction_minutes} min."})  # log the wait time
    if severity in ("high", "critical"):  # if it's a serious case
        # Serious case: tell the hospital and the emergency contacts.
        episode.actions.append({"ts": _now(), "type": "hospital",  # log the hospital step
                                "message": f"CRITICAL ALERT sent to {DEFAULT_HOSPITAL}. "  # log the alert
                                           f"Ambulance: {AMBULANCE_PHONE}."})  # log the ambulance number
        episode.actions.append({"ts": _now(), "type": "contacts",  # log the contacts step
                                "message": "Emergency contacts notified (simulated)."})  # log message
        notify_external("hospital", _base_payload(patient, episode))  # send the hospital alert
        notify_external("contacts", _base_payload(patient, episode))  # send the contacts alert
    if severity == "critical":  # if it's critical
        # Critical case: also dispatch an ambulance right away.
        episode.actions.append({"ts": _now(), "type": "ambulance",  # log the ambulance step
                                "message": f"Ambulance dispatched via {AMBULANCE_PHONE}."})  # log message
        episode.status = "ambulance_dispatched"  # change status to ambulance sent
        notify_external("ambulance", _base_payload(patient, episode))  # send the ambulance alert
    if cost > INSURANCE_COVER_LIMIT and severity in ("high", "critical"):  # bill bigger than cover
        # If the bill would be bigger than the insurance cover, offer insurance.
        episode.insurance_status = "offered"  # mark insurance as offered
        episode.actions.append({"ts": _now(), "type": "insurance",  # log the insurance step
                                "message": f"Estimated cost {cost:.2f} exceeds cover "  # log the cost
                                           f"{INSURANCE_COVER_LIMIT:.2f} - insurance offered."})  # log the cover

    STORE.add_episode(episode)  # save the episode
    return redirect(url_for("episode_page", eid=episode.id))  # show the episode page


# Shows the result page for one episode: severity, remedy, the reaction
# timer, and the emergency buttons (ambulance / hospital / contacts).
@app.route("/episode/<eid>")  # the episode result page address (eid = episode ID)
def episode_page(eid: str) -> Any:  # the episode page function
    patient = _current_patient()  # who is logged in
    episode = STORE.get_episode(eid)  # find this episode
    if patient is None or episode is None or episode.patient_id != patient.id:  # not allowed to see it
        return redirect(url_for("home"))  # send them to the front page
    _auto_ambulance_sweep(episode)  # check if the remedy timer ran out
    return render_template("episode.html", patient=patient,  # show the episode page
                           episode=episode, cover=INSURANCE_COVER_LIMIT)  # with episode and insurance cover


# Button: "My remedy worked" - marks the episode as resolved and stops the
# timer so no ambulance is called.
@app.route("/episode/<eid>/resolve", methods=["POST"])  # the "remedy worked" button address
def resolve_episode(eid: str) -> Any:  # the resolve function
    episode = _owned_episode(eid)  # find the episode (only if owned)
    if episode and episode.status == "remedy_active":  # if it exists and timer is running
        episode.status = "resolved"  # mark as resolved
        episode.deadline_ts = None  # stop the timer
        episode.actions.append({"ts": _now(), "type": "resolve",  # log the resolve step
                                "message": "Patient confirmed the remedy worked. Problem resolved."})  # log message
    return redirect(url_for("episode_page", eid=eid))  # show the episode page again


# Button: call the ambulance right now (no waiting for the timer).
@app.route("/episode/<eid>/ambulance", methods=["POST"])  # the ambulance button address
def ambulance_episode(eid: str) -> Any:  # the call-ambulance function
    episode = _owned_episode(eid)  # find the episode (only if owned)
    if episode and episode.status != "resolved":  # if it exists and not already resolved
        patient = STORE.get_patient(episode.patient_id)  # find the patient
        episode.status = "ambulance_dispatched"  # mark ambulance as sent
        episode.deadline_ts = None  # stop the timer
        episode.actions.append({"ts": _now(), "type": "ambulance",  # log the ambulance step
                                "message": f"AMBULANCE dispatched via {AMBULANCE_PHONE}."})  # log message
        if patient:  # if we found the patient
            notify_external("ambulance", _base_payload(patient, episode))  # send the ambulance alert
    return redirect(url_for("episode_page", eid=eid))  # show the episode page again


# Button: tell the hospital again (re-sends the alert).
@app.route("/episode/<eid>/hospital", methods=["POST"])  # the re-notify-hospital button address
def hospital_episode(eid: str) -> Any:  # the notify-hospital function
    episode = _owned_episode(eid)  # find the episode (only if owned)
    if episode:  # if it exists
        patient = STORE.get_patient(episode.patient_id)  # find the patient
        episode.actions.append({"ts": _now(), "type": "hospital",  # log the hospital step
                                "message": f"Hospital re-notified ({DEFAULT_HOSPITAL})."})  # log message
        if patient:  # if we found the patient
            notify_external("hospital", _base_payload(patient, episode))  # send the hospital alert
    return redirect(url_for("episode_page", eid=eid))  # show the episode page again


# Button: call the emergency contacts again (re-sends the alert).
@app.route("/episode/<eid>/contacts", methods=["POST"])  # the re-call-contacts button address
def contacts_episode(eid: str) -> Any:  # the call-contacts function
    episode = _owned_episode(eid)  # find the episode (only if owned)
    if episode:  # if it exists
        patient = STORE.get_patient(episode.patient_id)  # find the patient
        episode.actions.append({"ts": _now(), "type": "contacts",  # log the contacts step
                                "message": "Emergency contacts re-called (simulated)."})  # log message
        if patient:  # if we found the patient
            notify_external("contacts", _base_payload(patient, episode))  # send the contacts alert
    return redirect(url_for("episode_page", eid=eid))  # show the episode page again


# Button: accept or decline the insurance offer for this episode.
@app.route("/episode/<eid>/insurance", methods=["POST"])  # the insurance choice button address
def insurance_episode(eid: str) -> Any:  # the insurance choice function
    episode = _owned_episode(eid)  # find the episode (only if owned)
    if episode:  # if it exists
        choice = request.form.get("choice", "no")  # read yes/no choice (default no)
        episode.insurance_status = "applied" if choice == "yes" else "declined"  # save the choice
        episode.actions.append({"ts": _now(), "type": "insurance",  # log the insurance step
                                "message": "Insurance application submitted." if choice == "yes"  # log accepted
                                else "Patient declined insurance."})  # log declined
    return redirect(url_for("episode_page", eid=eid))  # show the episode page again


# DEMO ONLY: instantly makes the remedy timer run out so you can watch the
# ambulance get called automatically. (Not linked from any button on the site.)
@app.route("/episode/<eid>/advance", methods=["POST"])  # demo-only timer-skip address
def advance_timer(eid: str) -> Any:  # the timer-skip function
    episode = _owned_episode(eid)  # find the episode (only if owned)
    if episode:  # if it exists
        episode.deadline_ts = _timestamp() - 1  # set the deadline to 1 second in the past
    return redirect(url_for("episode_page", eid=eid))  # show the episode page again


# The history page - shows all past episodes for the logged-in user, newest
# first.
@app.route("/history")  # the history page address
def history() -> Any:  # the history page function
    patient = _current_patient()  # who is logged in
    if patient is None:  # nobody logged in
        return redirect(url_for("home"))  # send them to the front page
    episodes = sorted(STORE.patient_history(patient.id),  # get the patient's episodes and sort them
                      key=lambda e: e.created_at, reverse=True)  # newest first
    return render_template("history.html", patient=patient, episodes=episodes)  # show the history page


# Small helper: returns the episode only if it exists AND belongs to the
# logged-in user. Returns None otherwise.
def _owned_episode(eid: str) -> Optional[Episode]:  # helper: get an episode only if the user owns it
    patient = _current_patient()  # who is logged in
    episode = STORE.get_episode(eid)  # find the episode
    if patient is None or episode is None or episode.patient_id != patient.id:  # not allowed
        return None  # return nothing
    return episode  # otherwise return the episode


# If the remedy timer has run out, automatically call the ambulance.
def _auto_ambulance_sweep(episode: Episode) -> None:  # helper: auto-call ambulance when timer ends
    if (episode.status == "remedy_active" and episode.deadline_ts  # timer is running
            and _timestamp() >= episode.deadline_ts):  # and time is up
        patient = STORE.get_patient(episode.patient_id)  # find the patient
        episode.status = "ambulance_dispatched"  # mark ambulance as sent
        episode.deadline_ts = None  # stop the timer
        episode.actions.append({"ts": _now(), "type": "ambulance",  # log the ambulance step
                                "message": "Remedy did NOT work within the reaction window - "  # log reason
                                           f"AMBULANCE auto-dispatched ({AMBULANCE_PHONE})."})  # log the ambulance
        if patient:  # if we found the patient
            notify_external("ambulance", _base_payload(patient, episode))  # send the ambulance alert


# Runs in the background ALL the time. Every couple of seconds it checks every
# episode to see whether any remedy timer has run out.
def background_sweeper() -> None:  # the always-on background checker
    while True:  # loop forever
        time.sleep(SWEEP_INTERVAL)  # pause for the set seconds
        for eid in list(STORE.episodes):  # go through every episode
            episode = STORE.get_episode(eid)  # get the episode
            if episode:  # if it exists
                _auto_ambulance_sweep(episode)  # check its timer


# --------------------------- JSON API (for friends) -------------------------
# These are the "robot-friendly" endpoints. Other apps (or your friend's apps)
# can call these to check the server, create patients, or trigger actions.

# Simple "is the server alive?" check - good for testing.
@app.route("/api/health")  # the health-check address
def api_health() -> Any:  # the health-check function
    return jsonify({"service": APP_NAME, "status": "ok", "time": _now(),  # reply with app name, status, time
                    "insurance_cover_limit": INSURANCE_COVER_LIMIT})  # and the insurance limit


# A guide to the API - lists every endpoint and what it expects, so anyone
# reading it knows how to use the robot-friendly part.
@app.route("/api/contract")  # the API guide address
def api_contract() -> Any:  # the API guide function
    return jsonify({  # reply with the API guide
        "app": APP_NAME, "version": "1.0",  # app name and version
        "severity_values": ["low", "medium", "high", "critical", "nonbio"],  # all severity levels
        "endpoints": {  # list of endpoints
            "assess_symptoms": {"method": "POST", "path": "/api/severity",  # how to assess symptoms
                                "body": {"symptoms": ["chest pain"], "patient_id": "optional"}},  # example body
            "create_patient": {"method": "POST", "path": "/api/patients",  # how to create a patient
                               "body": {"name": "...", "age": 30, "contacts": []}},  # example body
            "get_patient": {"method": "GET", "path": "/api/patients/<id>"},  # how to get a patient
            "get_history": {"method": "GET", "path": "/api/patients/<id>/history"},  # how to get history
            "get_episode": {"method": "GET", "path": "/api/episodes/<id>"},  # how to get an episode
            "trigger_action": {"method": "POST", "path": "/api/episodes/<id>/actions",  # how to trigger actions
                               "body": {"action": "ambulance|hospital|contacts|resolve|insurance",  # possible actions
                                        "choice": "yes|no"}},  # possible choices
        },
        "webhooks_we_call": {  # what we send to the friend's URLs
            "HOSPITAL_API_URL": "POST patient + severity when severity is high/critical",  # hospital hook
            "CONTACT_SMS_API_URL": "POST emergency contacts when severity is high/critical",  # SMS hook
            "AMBULANCE_API_URL": "POST when user hits emergency, timer expires, or severity critical",  # ambulance hook
        },
    })


# Lets another app create a patient account by sending JSON data.
@app.route("/api/patients", methods=["POST"])  # the create-patient API address
def api_create_patient() -> Any:  # the create-patient API function
    data = request.get_json(silent=True) or {}  # read the incoming JSON (empty if none)
    email = str(data.get("email", "")).strip()  # read the email
    if not email:  # email missing
        return jsonify({"error": "email is required"}), 400  # error: bad request
    if STORE.find_by_email(email):  # email already exists
        return jsonify({"error": "email already exists"}), 400  # error: bad request
    salt = make_salt()  # make a random salt
    contacts = [Contact(str(c.get("name", "")), str(c.get("phone", "")),  # build contact list from JSON
                        str(c.get("relation", "")), str(c.get("email", "")))  # each contact's fields
                for c in data.get("contacts", [])]  # for every contact in the JSON
    patient = Patient(  # build the new patient
        id=uuid.uuid4().hex[:10], email=email,  # random ID and the email
        password=hash_password(str(data.get("password", "")), salt), salt=salt,  # scrambled password + salt
        name=str(data.get("name", "")), age=int(data.get("age", 0) or 0),  # name and age
        weight_kg=float(data.get("weight_kg", 0) or 0),  # weight
        blood_group=str(data.get("blood_group", "Unknown")),  # blood group
        allergies=[str(a) for a in data.get("allergies", [])],  # allergies
        contacts=contacts, created_at=_now())  # contacts and creation time
    STORE.add_patient(patient)  # save the new patient
    return jsonify(patient_to_json(patient)), 201  # reply with the patient data (201 = created)


# Lets another app send symptoms and get back the severity + remedy + cost as
# JSON (the same brain as the website uses).
@app.route("/api/severity", methods=["POST"])  # the assess-symptoms API address
def api_severity() -> Any:  # the assess-symptoms API function
    data = request.get_json(silent=True) or {}  # read the incoming JSON
    symptoms = [str(s).lower() for s in data.get("symptoms", [])]  # clean the symptom list
    if not symptoms:  # no symptoms given
        return jsonify({"error": "symptoms are required"}), 400  # error: bad request
    severity = assess_severity(symptoms)  # pick a severity level
    if severity == "nonbio" or (is_gibberish(" ".join(symptoms)) and severity == "low"):  # nonsense or feelings
        severity = "nonbio"  # treat as not a medical issue
    remedy = find_remedy(symptoms) if severity != "nonbio" else None  # find a remedy (if medical)
    diagnosis = diagnosis_for(symptoms) if severity != "nonbio" else "Not a biological / medical issue"  # get diagnosis
    cost = estimate_cost(severity, len(symptoms))  # estimate the cost
    payload = {  # build the reply
        "severity": severity, "diagnosis": diagnosis,  # severity and diagnosis
        "estimated_cost": cost,  # the cost
        "insurance_needed": cost > INSURANCE_COVER_LIMIT,  # whether insurance is needed
        "recommendation": ("IMMEDIATE HOSPITAL" if severity in ("high", "critical")  # serious? hospital
                           else "home remedy"),  # mild? home remedy
        "remedy": {"medicine": remedy.medicine, "dosage": remedy.dosage,  # the remedy details
                   "reaction_minutes": remedy.reaction_minutes,  # wait time
                   "note": remedy.note} if remedy else None,  # advice (or none)
        "action": ("hospital" if severity in ("high", "critical") else "remedy"),  # what action to take
    }
    if data.get("patient_id"):  # if a patient ID was given
        p = STORE.get_patient(data["patient_id"])  # find that patient
        payload["patient"] = patient_to_json(p) if p else None  # add their data to the reply
    return jsonify(payload)  # send the reply


# Returns one patient's data as JSON.
@app.route("/api/patients/<pid>")  # the get-patient API address
def api_patient(pid: str) -> Any:  # the get-patient API function
    patient = STORE.get_patient(pid)  # find the patient
    if patient is None:  # not found
        return jsonify({"error": "patient not found"}), 404  # error: not found
    return jsonify(patient_to_json(patient))  # reply with the patient data


# Returns a patient's whole history as a JSON list of episodes.
@app.route("/api/patients/<pid>/history")  # the get-history API address
def api_history(pid: str) -> Any:  # the get-history API function
    patient = STORE.get_patient(pid)  # find the patient
    if patient is None:  # not found
        return jsonify({"error": "patient not found"}), 404  # error: not found
    episodes = sorted(STORE.patient_history(pid), key=lambda e: e.created_at, reverse=True)  # sort newest first
    return jsonify([episode_to_json(e) for e in episodes])  # reply with all episodes


# Returns one episode as JSON.
@app.route("/api/episodes/<eid>")  # the get-episode API address
def api_episode(eid: str) -> Any:  # the get-episode API function
    episode = STORE.get_episode(eid)  # find the episode
    if episode is None:  # not found
        return jsonify({"error": "episode not found"}), 404  # error: not found
    return jsonify(episode_to_json(episode))  # reply with the episode data


# Lets another app trigger an action on an episode (call ambulance, notify
# hospital, call contacts, resolve, or handle insurance).
@app.route("/api/episodes/<eid>/actions", methods=["POST"])  # the trigger-action API address
def api_episode_action(eid: str) -> Any:  # the trigger-action API function
    episode = STORE.get_episode(eid)  # find the episode
    if episode is None:  # not found
        return jsonify({"error": "episode not found"}), 404  # error: not found
    data = request.get_json(silent=True) or {}  # read the incoming JSON
    if isinstance(data, str):  # if the body is just plain text
        action = data.strip().lower()  # use it as the action name
        data = {}  # no extra options
    else:  # otherwise it is a JSON object
        action = str(data.get("action", "")).strip().lower()  # read the action name
    patient = STORE.get_patient(episode.patient_id)  # find the patient
    if action == "ambulance":  # action: ambulance
        episode.status = "ambulance_dispatched"  # mark ambulance as sent
        episode.deadline_ts = None  # stop the timer
        episode.actions.append({"ts": _now(), "type": "ambulance",  # log the ambulance step
                                "message": "Ambulance dispatched via API."})  # log message
        notify_external("ambulance", _base_payload(patient, episode) if patient else {})  # send alert
    elif action == "hospital":  # action: hospital
        episode.actions.append({"ts": _now(), "type": "hospital",  # log the hospital step
                                "message": "Hospital notified via API."})  # log message
        notify_external("hospital", _base_payload(patient, episode) if patient else {})  # send alert
    elif action == "contacts":  # action: contacts
        episode.actions.append({"ts": _now(), "type": "contacts",  # log the contacts step
                                "message": "Emergency contacts called via API."})  # log message
        notify_external("contacts", _base_payload(patient, episode) if patient else {})  # send alert
    elif action == "resolve":  # action: resolve
        episode.status = "resolved"  # mark as resolved
        episode.deadline_ts = None  # stop the timer
        episode.actions.append({"ts": _now(), "type": "resolve",  # log the resolve step
                                "message": "Resolved via API."})  # log message
    elif action == "insurance":  # action: insurance
        choice = data.get("choice", "no") if isinstance(data, dict) else "no"  # read yes/no choice
        episode.insurance_status = "applied" if choice == "yes" else "declined"  # save the choice
        episode.actions.append({"ts": _now(), "type": "insurance",  # log the insurance step
                                "message": "Insurance handled via API."})  # log message
    else:  # unknown action name
        return jsonify({"error": f"unknown action '{action}'"}), 400  # error: bad request
    return jsonify(episode_to_json(episode))  # reply with the updated episode


# --------------------------- Hospital finder (server side) -----------------
# Searches OpenStreetMap data without browser CORS issues. Geocodes the
# location with Nominatim, then finds nearby hospitals via Photon
# (free OSM service). Falls back gracefully if a service is unreachable.

# Downloads a URL and turns the answer into a dictionary. Returns None if
# anything goes wrong, so the app never crashes because of the internet.
def _http_get_json(url: str, timeout: int = 25) -> Optional[Dict[str, Any]]:  # helper: download a URL as JSON
    try:  # try this
        req = urllib.request.Request(url, headers={  # build the request
            "User-Agent": "Health360App/1.0 (local demo)",  # tell the site who we are
            "Accept": "application/json",  # ask for JSON back
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # download with a time limit
            return json.loads(resp.read().decode("utf-8"))  # read and turn into a dictionary
    except Exception:  # if anything goes wrong
        return None  # return nothing (no crash)


# Turns a place name (like "Mumbai") into latitude/longitude coordinates.
def _geocode(location: str) -> Optional[List[float]]:  # helper: find coordinates of a place
    data = _http_get_json(  # ask the Nominatim service
        "https://nominatim.openstreetmap.org/search?format=json&limit=1&q="  # the URL
        + urllib.parse.quote(location))  # with the place name added safely
    if data and len(data) > 0:  # if we got an answer
        return [float(data[0]["lat"]), float(data[0]["lon"])]  # return its latitude and longitude
    data = _http_get_json(  # try a backup: the Photon service
        "https://photon.komoot.io/api/?q=" + urllib.parse.quote(location) + "&limit=1")  # the URL
    if data and data.get("features"):  # if we got an answer
        c = data["features"][0]["geometry"]["coordinates"]  # get the coordinates
        return [float(c[1]), float(c[0])]  # return latitude and longitude
    return None  # could not find it: return nothing


# Finds up to 25 hospitals near the given coordinates. The inner "add"
# helper skips hospitals with no name and removes duplicates.
def _find_hospitals_near(lat: float, lon: float) -> List[Dict[str, Any]]:  # helper: find hospitals near a spot
    seen: Dict[str, Dict[str, Any]] = {}  # a dictionary to remove duplicate names

    def add(h: Dict[str, Any]) -> None:  # inner helper: adds one hospital if new
        if not h.get("name"):  # skip if it has no name
            return  # stop
        key = h["name"].strip().lower()  # make a name key (lowercase)
        if key in seen:  # if we already have this hospital
            return  # stop (duplicate)
        seen[key] = h  # otherwise add it

    for osm_tag in ("amenity:hospital", "healthcare"):  # ask for two kinds of places
        url = ("https://photon.komoot.io/api/?q=hospital&lat={}&lon={}"  # the search URL
               "&limit=25&osm_tag={}").format(lat, lon, osm_tag)  # with our coordinates and tag
        data = _http_get_json(url)  # download the results
        if not data:  # if the download failed
            continue  # try the next tag
        for f in data.get("features", []):  # go through each result
            p = f.get("properties", {}) or {}  # get its properties
            g = f.get("geometry", {}) or {}  # get its geometry
            coords = g.get("coordinates") or []  # get its coordinates
            add({  # add the hospital info
                "name": p.get("name", ""),  # hospital name
                "street": p.get("street", ""),  # street
                "city": p.get("city", "") or p.get("locality", "") or p.get("county", ""),  # city
                "postcode": p.get("postcode", ""),  # postcode
                "lat": coords[1] if len(coords) > 1 else None,  # latitude
                "lon": coords[0] if len(coords) > 0 else None,  # longitude
            })
    return list(seen.values())[:25]  # return up to 25 hospitals


# The insurance page's hospital search: "?location=Mumbai" returns a JSON list
# of nearby hospitals. (Called from the insurance page in the browser.)
@app.route("/api/hospitals")  # the hospital-search API address
def api_hospitals() -> Any:  # the hospital-search API function
    location = request.args.get("location", "").strip()  # read the location from the URL
    if not location:  # no location given
        return jsonify({"error": "Location is required", "hospitals": []}), 400  # error: bad request
    coords = _geocode(location)  # turn the place name into coordinates
    if not coords:  # could not find the place
        return jsonify({"error": f"Could not locate '{location}'. "  # error message
                                 "Try a more specific location (e.g. 'Mumbai, Maharashtra').",  # hint
                        "hospitals": []}), 404  # error: not found
    hospitals = _find_hospitals_near(coords[0], coords[1])  # find hospitals near those coordinates
    return jsonify({  # reply with the results
        "location": location, "lat": coords[0], "lon": coords[1],  # the searched place
        "count": len(hospitals), "hospitals": hospitals,  # how many and the list
    })


# ---------------------------------------------------------------------------
# 8. ENTRY POINT  (the part that starts the app when you run "python app.py")
# ---------------------------------------------------------------------------

def main() -> None:  # the main start function
    print(f"[{APP_NAME}] starting on http://{HOST}:{PORT}")  # tell the terminal it's starting
    print(f"[{APP_NAME}] Timer mode: {'fast (seconds, demo)' if TIMER_MODE == 'fast' else 'real (minutes, production)'}")  # show the timer mode
    # Start the background timer-checker (it runs forever in its own thread).
    threading.Thread(target=background_sweeper, daemon=True, name="ambulance-sweeper").start()  # start the checker
    # After a short moment, open the website in the browser automatically.
    threading.Timer(1.5, lambda: webbrowser.open(f"http://{HOST}:{PORT}")).start()  # open the browser soon
    # Run the website until the user closes it.
    app.run(host=HOST, port=PORT, debug=False)  # start the website server


# This line makes sure main() runs ONLY when this file is run directly
# (not when it is imported by another file).
if __name__ == "__main__":  # "am I being run directly?"
    main()  # if yes, start the app
