<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Health 360</title>
<style>
  :root {
    --teal: #0f766e;
    --teal-dark: #115e59;
    --teal-light: #ccfbf1;
    --red: #dc2626;
    --gray: #64748b;
    --bg: #f1f5f9;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: var(--bg);
    min-height: 100vh;
  }
  header {
    background: linear-gradient(135deg, var(--teal), var(--teal-dark));
    color: #fff;
    padding: 18px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.15);
  }
  header h1 { font-size: 26px; letter-spacing: 1px; }
  .page { display: none; max-width: 640px; margin: 30px auto; padding: 0 16px; }
  .page.active { display: block; }
  .card {
    background: #fff;
    border-radius: 14px;
    padding: 26px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  }
  .card h2 { color: var(--teal-dark); margin-bottom: 16px; }
  .card p.sub { color: var(--gray); margin-bottom: 20px; font-size: 14px; }
  label { display: block; font-weight: 600; margin: 14px 0 6px; font-size: 14px; color: #1e293b; }
  input, select, textarea {
    width: 100%;
    padding: 10px 12px;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    font-size: 15px;
    font-family: inherit;
    outline: none;
  }
  input:focus, select:focus, textarea:focus { border-color: var(--teal); }
  .row { display: flex; gap: 12px; }
  .row > div { flex: 1; }
  button {
    border: none;
    border-radius: 8px;
    padding: 12px 18px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.15s;
  }
  button:hover { opacity: 0.88; }
  .btn-primary { background: var(--teal); color: #fff; width: 100%; margin-top: 22px; }
  .btn-ghost { background: #e2e8f0; color: #1e293b; }
  .btn-small { padding: 7px 12px; font-size: 13px; }
  .btn-add { background: var(--teal-light); color: var(--teal-dark); margin-top: 12px; }
  .error { color: var(--red); font-size: 13px; margin-top: 5px; min-height: 18px; }
  .ok-msg { color: var(--teal); font-size: 13px; margin-top: 5px; }
  .modal-backdrop {
    display: none;
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.5);
    z-index: 10;
    align-items: center;
    justify-content: center;
  }
  .modal-backdrop.show { display: flex; }
  .modal {
    background: #fff;
    border-radius: 14px;
    max-width: 560px;
    width: 92%;
    max-height: 82vh;
    overflow-y: auto;
    padding: 26px;
  }
  .disclaimer {
    color: var(--red);
    font-weight: 700;
    background: #fef2f2;
    border: 1.5px solid var(--red);
    border-radius: 8px;
    padding: 12px;
    margin: 14px 0;
  }
  .contact-block {
    border: 1.5px dashed #cbd5e1;
    border-radius: 10px;
    padding: 14px;
    margin-top: 14px;
    background: #f8fafc;
  }
  .contact-block .remove { margin-top: 12px; background: #fee2e2; color: var(--red); }
  .radio-group { display: flex; gap: 24px; margin-top: 6px; }
  .radio-group label { font-weight: 400; display: flex; align-items: center; gap: 6px; margin: 0; }
  .radio-group input { width: auto; }
  .hint { font-size: 12px; color: var(--gray); margin-top: 4px; }
  .section-title {
    margin-top: 26px; padding-top: 20px;
    border-top: 2px solid #e2e8f0;
    color: var(--teal-dark); font-size: 18px;
  }
  .btn-logout { background: transparent; color: #fff; border: 1.5px solid #fff; padding: 7px 14px; font-size: 13px; }
  .profile-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px; }
  .profile-grid .item .k { color: var(--gray); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
  .profile-grid .item .v { font-weight: 600; font-size: 15px; margin-top: 2px; word-break: break-word; }
  .profile-section { margin-top: 22px; }
  .profile-section h3 { color: var(--teal-dark); font-size: 16px; margin-bottom: 8px; border-bottom: 1.5px solid #e2e8f0; padding-bottom: 6px; }
  .contact-card {
    border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; background: #f8fafc;
  }
  .contact-card p { font-size: 14px; color: #334155; margin: 2px 0; }
  .contact-card .name { font-weight: 700; color: #0f172a; }
  .hospital-note {
    background: #eff6ff; border: 1.5px solid #93c5fd; color: #1e40af;
    border-radius: 8px; padding: 12px; margin-top: 14px; font-size: 14px;
  }
  .hospital-card {
    border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px;
    margin-top: 10px; background: #f8fafc;
  }
  .hospital-card .h-name { font-weight: 700; color: #0f172a; font-size: 15px; }
  .hospital-card .h-detail { font-size: 13px; color: #475569; margin-top: 3px; }
  .hospital-card a { color: var(--teal); font-size: 13px; margin-right: 14px; }
  .hospital-count { font-size: 13px; color: var(--gray); margin-top: 10px; }
  #hospitalLoading { color: var(--teal); font-size: 14px; margin-top: 12px; }
  .hospital-empty { font-size: 14px; color: #b45309; background: #fffbeb;
    border: 1.5px solid #f59e0b; border-radius: 8px; padding: 12px; margin-top: 12px; }
  .btn-row { display: flex; gap: 10px; margin-top: 22px; }
  .btn-row .btn-primary { margin-top: 0; }
  .btn-row .btn-ghost { flex: 1; }
</style>
</head>
<body>

<header>
  <h1>Health 360</h1>
  <button id="logoutBtn" class="btn-logout" style="display:none;" onclick="logout()">Sign Out</button>
</header>

<!-- ============ PAGE 1 : WELCOME / SIGN IN ============ -->
<div id="page-welcome" class="page active">
  <div class="card" style="text-align:center; padding-top: 50px; padding-bottom: 50px;">
    <h2 style="font-size: 32px;">Welcome to Health 360</h2>
    <p class="sub">Your all-in-one health profile manager.</p>
    <button class="btn-primary" onclick="goto('page-signin')">Sign In</button>
    <div style="margin: 10px 0; color: var(--gray); font-size: 13px;">or</div>
    <button class="btn-primary" style="background: var(--teal-dark); margin-top: 0;" onclick="goto('page-terms')">Create Account</button>
  </div>
</div>

<!-- ============ PAGE 2 : TERMS & CONDITIONS ============ -->
<div id="page-terms" class="page">
  <div class="card">
    <h2>Terms &amp; Conditions</h2>
    <p class="sub">Please read and agree to continue.</p>
    <div style="max-height: 260px; overflow-y: auto; border: 1.5px solid #e2e8f0; border-radius: 8px; padding: 14px; font-size: 14px; color: #334155;">
      <p><strong>1. Use of the App.</strong> Health 360 stores the health information you voluntarily provide in your browser for the purpose of building your personal health profile.</p>
      <p style="margin-top:10px;"><strong>2. Not Medical Advice.</strong> Health 360 is not a medical service. Nothing in this app constitutes a diagnosis, treatment plan, or medical advice.</p>
      <p style="margin-top:10px;"><strong>3. Emergency.</strong> If you are experiencing a medical emergency, call your local emergency number immediately. Do not rely on this app.</p>
      <p style="margin-top:10px;"><strong>4. Data.</strong> Your data is stored locally on your device. Always keep your login details safe and do not share your account.</p>
      <p style="margin-top:10px;"><strong>5. Changes.</strong> We may update these terms at any time.</p>
    </div>
    <div class="disclaimer">
      DISCLAIMER: We are NOT responsible for the patient during the usage of this web app. Use of Health 360 is entirely at your own risk.
    </div>
    <button class="btn-primary" onclick="goto('page-account')">I Agree to the Terms &amp; Conditions</button>
    <button class="btn-primary" style="background:#e2e8f0; color:#1e293b; margin-top:10px;" onclick="goto('page-welcome')">Decline</button>
  </div>
</div>

<!-- ============ PAGE 3 : CREATE ACCOUNT ============ -->
<div id="page-account" class="page">
  <div class="card">
    <h2>Create Account</h2>
    <p class="sub">Sign up to start building your profile.</p>
    <label for="regEmail">Email / Username</label>
    <input type="text" id="regEmail" placeholder="you@example.com" autocomplete="off">
    <div class="error" id="regEmailErr"></div>
    <label for="regPass">Password</label>
    <input type="password" id="regPass" placeholder="Enter a password">
    <div class="error" id="regPassErr"></div>
    <label for="regPass2">Confirm Password</label>
    <input type="password" id="regPass2" placeholder="Re-enter your password">
    <div class="error" id="regPass2Err"></div>
    <button class="btn-primary" onclick="createAccount()">Create Account</button>
    <p style="margin-top:14px; font-size:14px; color:var(--gray);">
      Already have an account? <a href="#" style="color:var(--teal);" onclick="goto('page-signin')">Sign in</a>
    </p>
  </div>
</div>

<!-- ============ PAGE : SIGN IN ============ -->
<div id="page-signin" class="page">
  <div class="card">
    <h2>Sign In</h2>
    <p class="sub">Welcome back to Health 360.</p>
    <label for="loginEmail">Email / Username</label>
    <input type="text" id="loginEmail" placeholder="you@example.com" autocomplete="off">
    <div class="error" id="loginEmailErr"></div>
    <label for="loginPass">Password</label>
    <input type="password" id="loginPass" placeholder="Your password">
    <div class="error" id="loginPassErr"></div>
    <button class="btn-primary" onclick="signIn()">Sign In</button>
    <p style="margin-top:14px; font-size:14px; color:var(--gray);">
      New here? <a href="#" style="color:var(--teal);" onclick="goto('page-terms')">Create an account</a>
    </p>
  </div>
</div>

<!-- ============ PAGE 4 : USER CREDENTIALS / HEALTH PROFILE ============ -->
<div id="page-creds" class="page">
  <div class="card">
    <h2>Personal Details</h2>
    <p class="sub">Tell us about yourself.</p>

    <label for="fullName">Full Name</label>
    <input type="text" id="fullName" placeholder="e.g. John Doe">
    <div class="error" id="fullNameErr"></div>

    <div class="row">
      <div>
        <label for="age">Age</label>
        <input type="number" id="age" placeholder="e.g. 25" min="0" max="150">
        <div class="error" id="ageErr"></div>
      </div>
      <div>
        <label for="gender">Gender</label>
        <select id="gender">
          <option value="">Select...</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Non-binary">Non-binary</option>
          <option value="Other">Other</option>
          <option value="Prefer not to say">Prefer not to say</option>
        </select>
        <div class="error" id="genderErr"></div>
      </div>
    </div>

    <div class="row">
      <div>
        <label for="height">Height (cm)</label>
        <input type="number" id="height" placeholder="e.g. 170">
        <div class="error" id="heightErr"></div>
      </div>
      <div>
        <label for="weight">Weight (kg)</label>
        <input type="number" id="weight" placeholder="e.g. 65">
        <div class="error" id="weightErr"></div>
      </div>
    </div>

    <label for="phone">Phone Number</label>
    <input type="tel" id="phone" placeholder="e.g. 1234567890" inputmode="numeric">
    <div class="hint">Numbers only, up to 15 digits.</div>
    <div class="error" id="phoneErr"></div>

    <label for="location">Location</label>
    <input type="text" id="location" placeholder="City, State / Country">
    <div class="error" id="locationErr"></div>

    <div class="section-title">Emergency Contacts</div>
    <p class="sub" style="margin-bottom:0;">Add at least one person to reach in an emergency.</p>
    <div id="contactsContainer"></div>
    <button class="btn-add" onclick="addContact()">+ Add Another Contact</button>

    <div class="section-title">Health Information</div>
    <label for="illnessActual">Actual Illness (if any)</label>
    <textarea id="illnessActual" rows="2" placeholder="e.g. cancer"></textarea>
    <label for="illnessChronic">Chronic Illness (if any)</label>
    <textarea id="illnessChronic" rows="2" placeholder="e.g. asthma"></textarea>
    <label for="medications">Current Medications</label>
    <textarea id="medications" rows="3" placeholder="List any medications you currently take (comma separated)"></textarea>

    <div class="btn-row">
      <button class="btn-primary" onclick="saveCreds()">Continue</button>
      <button class="btn-ghost" id="credsBackBtn" onclick="editCancel()" style="display:none;">Cancel</button>
    </div>
  </div>
</div>

<!-- ============ PAGE 5 : INSURANCE & HOSPITALS ============ -->
<div id="page-insurance" class="page">
  <div class="card">
    <h2>Insurance &amp; Hospitals</h2>
    <p class="sub">Almost done!</p>

    <label for="insurance">Insurance Company Name</label>
    <input type="text" id="insurance" placeholder="e.g. Blue Cross Blue Shield">
    <div class="error" id="insuranceErr"></div>

    <div class="section-title">Find Hospitals Nearby</div>
    <p class="sub">Based on your location: <strong id="locPreview">-</strong></p>
    <button class="btn-primary" style="margin-top:0;" onclick="findHospitals()">Find Hospitals Near Me</button>
    <div id="hospitalResult">
      <div class="hospital-note" id="hospitalStub">
        Click "Find Hospitals Near Me" to search for hospitals near your location using free OpenStreetMap data.
      </div>
      <div id="hospitalLoading" style="display:none;">Searching for hospitals near your location&hellip;</div>
      <div id="hospitalCount" class="hospital-count" style="display:none;"></div>
      <div id="hospitalList"></div>
    </div>

    <div class="section-title">Insurance Coverage</div>
    <label>Are there any hospitals that your insurance company does not cover?</label>
    <div class="radio-group">
      <label><input type="radio" name="notCovered" value="No"> No</label>
      <label><input type="radio" name="notCovered" value="Yes"> Yes</label>
    </div>
    <div class="error" id="notCoveredErr"></div>
    <div id="notCoveredListWrap" style="display:none;">
      <label for="notCoveredList">List the hospitals not covered:</label>
      <textarea id="notCoveredList" rows="3" placeholder="e.g. St. Mary's Hospital, City General"></textarea>
    </div>

    <div class="btn-row">
      <button class="btn-primary" onclick="finishSignup()">Finish</button>
      <button class="btn-ghost" id="insBackBtn" onclick="goto('page-creds')" style="display:none;">Back</button>
    </div>
  </div>
</div>

<!-- ============ PROFILE PAGE ============ -->
<div id="page-profile" class="page">
  <div class="card">
    <h2>Your Health 360 Profile</h2>
    <div class="profile-section">
      <h3>Account</h3>
      <div class="profile-grid">
        <div class="item"><div class="k">Email</div><div class="v" id="pEmail">-</div></div>
        <div class="item"><div class="k">Password</div><div class="v">&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;&#9679;</div></div>
      </div>
    </div>
    <div class="profile-section">
      <h3>Personal Details</h3>
      <div class="profile-grid">
        <div class="item"><div class="k">Full Name</div><div class="v" id="pName">-</div></div>
        <div class="item"><div class="k">Age</div><div class="v" id="pAge">-</div></div>
        <div class="item"><div class="k">Gender</div><div class="v" id="pGender">-</div></div>
        <div class="item"><div class="k">Height</div><div class="v" id="pHeight">-</div></div>
        <div class="item"><div class="k">Weight</div><div class="v" id="pWeight">-</div></div>
        <div class="item"><div class="k">Phone</div><div class="v" id="pPhone">-</div></div>
        <div class="item"><div class="k">Location</div><div class="v" id="pLocation">-</div></div>
      </div>
    </div>
    <div class="profile-section">
      <h3>Emergency Contacts</h3>
      <div id="pContacts"></div>
    </div>
    <div class="profile-section">
      <h3>Health Information</h3>
      <div class="profile-grid">
        <div class="item"><div class="k">Actual Illness</div><div class="v" id="pIllnessActual">-</div></div>
        <div class="item"><div class="k">Chronic Illness</div><div class="v" id="pIllnessChronic">-</div></div>
        <div class="item"><div class="k">Current Medications</div><div class="v" id="pMedications">-</div></div>
      </div>
    </div>
    <div class="profile-section">
      <h3>Insurance &amp; Hospitals</h3>
      <div class="profile-grid">
        <div class="item"><div class="k">Insurance Company</div><div class="v" id="pInsurance">-</div></div>
        <div class="item"><div class="k">Coverage Notes</div><div class="v" id="pCoverage">-</div></div>
      </div>
      <div id="pUncovered" style="margin-top:10px;"></div>
    </div>
    <div class="btn-row">
      <button class="btn-primary" onclick="editProfile()">Edit Profile</button>
      <button class="btn-ghost" onclick="logout()">Sign Out</button>
    </div>
  </div>
</div>

<script>
  const DB_KEY = 'health360_user';

  function goto(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId).classList.add('active');
    window.scrollTo(0, 0);
  }

  function getData() {
    try { return JSON.parse(localStorage.getItem(DB_KEY)) || null; }
    catch (e) { return null; }
  }
  function saveData(user) { localStorage.setItem(DB_KEY, JSON.stringify(user)); }

  /* ---------- Password hashing (Web Crypto) ---------- */
  function makeSalt() {
    const bytes = crypto.getRandomValues(new Uint8Array(16));
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
  }
  async function hashPassword(pw, salt) {
    const data = new TextEncoder().encode(salt + ':' + pw);
    const digest = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, '0')).join('');
  }
  async function verifyPassword(pw, user) {
    if (!user.salt) {
      if (user.password === pw) {
        const salt = makeSalt();
        user.salt = salt;
        user.password = await hashPassword(pw, salt);
        saveData(user);
        return true;
      }
      return false;
    }
    return hashPassword(pw, user.salt) === user.password;
  }

  /* ---------- Page 3: Create Account ---------- */
  async function createAccount() {
    const email = document.getElementById('regEmail').value.trim();
    const pass = document.getElementById('regPass').value;
    const pass2 = document.getElementById('regPass2').value;
    clearErrs('regEmailErr', 'regPassErr', 'regPass2Err');

    let ok = true;
    if (!isValidEmail(email)) {
      document.getElementById('regEmailErr').textContent = 'Enter a valid email address (e.g. name@example.com).';
      ok = false;
    }
    if (pass.length < 6) {
      document.getElementById('regPassErr').textContent = 'Password must be at least 6 characters';
      ok = false;
    }
    if (pass !== pass2) {
      document.getElementById('regPass2Err').textContent = 'Passwords do not match';
      ok = false;
    }
    if (!ok) return;

    const existing = getData();
    if (existing && existing.email.toLowerCase() === email.toLowerCase()) {
      document.getElementById('regEmailErr').textContent = 'An account with this email already exists. Please sign in.';
      return;
    }

    const salt = makeSalt();
    saveData({
      email, salt, password: await hashPassword(pass, salt),
      name: '', age: '', gender: '', height: '', weight: '',
      phone: '', location: '', contacts: [],
      illnessActual: '', illnessChronic: '', medications: '',
      insurance: '', notCovered: '', uncoveredList: ''
    });
    resetSignupFlow();
    goto('page-creds');
  }

  /* ---------- Sign In ---------- */
  async function signIn() {
    const email = document.getElementById('loginEmail').value.trim();
    const pass = document.getElementById('loginPass').value;
    clearErrs('loginEmailErr', 'loginPassErr');

    const user = getData();
    if (!user) {
      document.getElementById('loginEmailErr').textContent = 'No account found. Please create an account first.';
      return;
    }
    if (user.email.toLowerCase() !== email.toLowerCase()) {
      document.getElementById('loginEmailErr').textContent = 'No account found with this email.';
      return;
    }
    if (!(await verifyPassword(pass, user))) {
      document.getElementById('loginPassErr').textContent = 'Incorrect password.';
      return;
    }
    showProfile();
  }

  /* ---------- Page 4: Credentials ---------- */
  function addContact(data) {
    const c = document.getElementById('contactsContainer');
    const block = document.createElement('div');
    block.className = 'contact-block';
    block.innerHTML = `
      <label>Emergency Contact's Full Name</label>
      <input type="text" class="c-name" placeholder="e.g. Jane Smith" value="${data ? escapeHtml(data.name) : ''}">
      <label>Relationship to You</label>
      <input type="text" class="c-rel" placeholder="e.g. Mother, Friend" value="${data ? escapeHtml(data.rel) : ''}">
      <label>Phone Number</label>
      <input type="tel" class="c-phone" placeholder="e.g. 9876543210" inputmode="numeric" maxlength="15" value="${data ? escapeHtml(data.phone) : ''}">
      <label>Email (optional)</label>
      <input type="text" class="c-email" placeholder="e.g. jane@example.com" value="${data ? escapeHtml(data.email) : ''}">
      <button class="btn-small remove" onclick="this.parentElement.remove()">Remove Contact</button>
    `;
    c.appendChild(block);
    block.querySelector('.c-phone').addEventListener('input', enforceDigits);
  }

  function enforceDigits(e) {
    const el = e.target;
    el.value = el.value.replace(/\D/g, '').slice(0, 15);
  }

  function resetSignupFlow() {
    seeded = false;
    document.getElementById('contactsContainer').innerHTML = '';
    document.getElementById('credsBackBtn').style.display = 'none';
    document.getElementById('insBackBtn').style.display = 'none';
  }

  function editCancel() {
    showProfile();
  }

  function saveCreds() {
    const name = document.getElementById('fullName').value.trim();
    const age = document.getElementById('age').value.trim();
    const gender = document.getElementById('gender').value;
    const height = document.getElementById('height').value.trim();
    const weight = document.getElementById('weight').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const location = document.getElementById('location').value.trim();
    clearErrs('fullNameErr', 'ageErr', 'genderErr', 'heightErr', 'weightErr', 'phoneErr', 'locationErr');

    let ok = true;
    if (!name) { document.getElementById('fullNameErr').textContent = 'Full name is required.'; ok = false; }
    if (!age || age < 0 || age > 150) { document.getElementById('ageErr').textContent = 'Enter a valid age.'; ok = false; }
    if (!gender) { document.getElementById('genderErr').textContent = 'Select a gender.'; ok = false; }
    if (!height || height <= 0) { document.getElementById('heightErr').textContent = 'Enter a valid height.'; ok = false; }
    if (!weight || weight <= 0) { document.getElementById('weightErr').textContent = 'Enter a valid weight.'; ok = false; }
    if (!phone) { document.getElementById('phoneErr').textContent = 'Phone number is required.'; ok = false; }
    if (!/^\d+$/.test(phone)) { document.getElementById('phoneErr').textContent = 'Phone number must contain digits only.'; ok = false; }
    if (phone.length > 15) { document.getElementById('phoneErr').textContent = 'Phone number can be at most 15 digits.'; ok = false; }
    if (!location) { document.getElementById('locationErr').textContent = 'Location is required.'; ok = false; }

    const contacts = collectContacts();
    if (!contacts.length) { ok = false; alert('Please add at least one emergency contact.'); }
    if (!ok) return;

    const user = getData();
    if (!user) { goto('page-welcome'); return; }
    user.name = name; user.age = age; user.gender = gender;
    user.height = height; user.weight = weight; user.phone = phone;
    user.location = location; user.contacts = contacts;
    user.illnessActual = document.getElementById('illnessActual').value.trim();
    user.illnessChronic = document.getElementById('illnessChronic').value.trim();
    user.medications = document.getElementById('medications').value.trim();
    saveData(user);

    document.getElementById('locPreview').textContent = location;
    goto('page-insurance');
  }

  function collectContacts() {
    const blocks = document.querySelectorAll('#contactsContainer .contact-block');
    const list = [];
    blocks.forEach(b => {
      const name = b.querySelector('.c-name').value.trim();
      const rel = b.querySelector('.c-rel').value.trim();
      const phone = b.querySelector('.c-phone').value.trim();
      const email = b.querySelector('.c-email').value.trim();
      if (name && rel && phone) {
        list.push({ name, rel, phone, email });
      }
    });
    return list;
  }

  /* ---------- Page 5: Insurance & Hospitals ---------- */
  async function findHospitals() {
    const user = getData();
    const loc = user ? user.location : '';
    const ins = document.getElementById('insurance').value.trim();

    const stub = document.getElementById('hospitalStub');
    const loading = document.getElementById('hospitalLoading');
    const count = document.getElementById('hospitalCount');
    const list = document.getElementById('hospitalList');

    list.innerHTML = '';
    count.style.display = 'none';

    if (!loc) {
      stub.style.display = 'block';
      stub.textContent = 'Please enter your location in the Personal Details step before searching for hospitals.';
      return;
    }

    stub.style.display = 'none';
    loading.style.display = 'block';

    try {
      const geoUrl = 'https://nominatim.openstreetmap.org/search?format=json&limit=1&q=' +
        encodeURIComponent(loc);
      const geoRes = await fetch(geoUrl, { headers: { 'Accept': 'application/json' } });
      if (!geoRes.ok) throw new Error('Geocoding request failed.');
      const geoData = await geoRes.json();
      if (!geoData.length) {
        throw new Error('Could not locate "' + loc + '". Please try a more specific location.');
      }
      const lat = parseFloat(geoData[0].lat);
      const lon = parseFloat(geoData[0].lon);

      const query = '[out:json][timeout:25];(' +
        'node["amenity"="hospital"](around:10000,' + lat + ',' + lon + ');' +
        'way["amenity"="hospital"](around:10000,' + lat + ',' + lon + ');' +
        ');out center tags;';

      const overpassRes = await fetch('https://overpass-api.de/api/interpreter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'data=' + encodeURIComponent(query)
      });
      if (!overpassRes.ok) throw new Error('Hospital search request failed.');
      const data = await overpassRes.json();

      const seen = new Set();
      const hospitals = [];
      (data.elements || []).forEach(el => {
        const tags = el.tags || {};
        const name = tags.name || '';
        if (!name) return;
        const key = name.trim().toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        const c = el.type === 'node' ? { lat: el.lat, lon: el.lon } : el.center || {};
        hospitals.push({
          name: name.trim(),
          street: tags['addr:street'] || '',
          city: tags['addr:city'] || '',
          postcode: tags['addr:postcode'] || '',
          phone: tags.phone || tags['contact:phone'] || '',
          website: tags.website || tags['contact:website'] || '',
          lat: c.lat,
          lon: c.lon
        });
      });

      const coveredChoice = document.querySelector('input[name="notCovered"]:checked');
      let uncovered = [];
      if (coveredChoice && coveredChoice.value === 'Yes') {
        uncovered = document.getElementById('notCoveredList').value
          .split(/[\n,;]+/).map(s => s.trim().toLowerCase()).filter(Boolean);
      }
      const filtered = hospitals.filter(h => {
        const n = h.name.toLowerCase();
        return !uncovered.some(u => n.includes(u) || u.includes(n));
      });

      if (!filtered.length) {
        list.innerHTML = '<div class="hospital-empty">No hospitals found within 10 km of "' +
          escapeHtml(loc) + (hospitals.length && uncovered.length
            ? '". All nearby hospitals may be on your not-covered list.'
            : '". Try a more specific location or a larger search.') + '</div>';
      } else {
        count.style.display = 'block';
        count.textContent = filtered.length + ' hospital' + (filtered.length > 1 ? 's' : '') +
          ' found near "' + loc + '"' +
          (ins ? ' (with ' + ins + ' coverage)' : '') +
          (uncovered.length ? '. Excluded ' + (hospitals.length - filtered.length) + ' not-covered hospital(s).' : '') + '.';
        filtered.slice(0, 25).forEach(h => {
          const card = document.createElement('div');
          card.className = 'hospital-card';
          let addrParts = [h.street, h.postcode + (h.postcode && h.city ? ' ' : '') + h.city]
            .filter(Boolean);
          let html = '<div class="h-name">' + escapeHtml(h.name) + '</div>';
          if (addrParts.length) html += '<div class="h-detail">' + escapeHtml(addrParts.join(', ')) + '</div>';
          if (h.phone) html += '<div class="h-detail">Phone: ' + escapeHtml(h.phone) + '</div>';
          html += '<div style="margin-top:8px;">';
          if (h.lat && h.lon) {
            html += '<a href="https://www.google.com/maps/dir/?api=1&destination=' +
              h.lat + ',' + h.lon + '" target="_blank" rel="noopener">Get Directions</a>';
          }
          const site = safeUrl(h.website);
          if (site) {
            html += '<a href="' + escapeHtml(site) + '" target="_blank" rel="noopener">Website</a>';
          }
          html += '</div>';
          card.innerHTML = html;
          list.appendChild(card);
        });
        if (filtered.length > 25) {
          list.insertAdjacentHTML('beforeend',
            '<div class="hospital-empty">Showing the closest 25 of ' + filtered.length +
            ' hospitals. Move closer to your target area for more results.</div>');
        }
      }
    } catch (e) {
      stub.style.display = 'block';
      stub.textContent = 'Hospital search failed: ' + e.message +
        ' Please check your internet connection and try again.';
    } finally {
      loading.style.display = 'none';
    }
  }

  function finishSignup() {
    const ins = document.getElementById('insurance').value.trim();
    clearErrs('insuranceErr', 'notCoveredErr');
    if (!ins) { document.getElementById('insuranceErr').textContent = 'Insurance company name is required.'; return; }

    const coveredChoice = document.querySelector('input[name="notCovered"]:checked');
    if (!coveredChoice) { document.getElementById('notCoveredErr').textContent = 'Please answer the coverage question.'; return; }

    const user = getData();
    if (!user) { goto('page-welcome'); return; }
    user.insurance = ins;
    user.notCovered = coveredChoice.value;
    user.uncoveredList = coveredChoice.value === 'Yes' ? document.getElementById('notCoveredList').value.trim() : '';
    saveData(user);
    showProfile();
  }

  /* ---------- Profile ---------- */
  function showProfile() {
    const u = getData();
    if (!u) { goto('page-signin'); return; }
    document.getElementById('logoutBtn').style.display = 'block';

    document.getElementById('pEmail').textContent = u.email;
    document.getElementById('pName').textContent = u.name || '-';
    document.getElementById('pAge').textContent = u.age || '-';
    document.getElementById('pGender').textContent = u.gender || '-';
    document.getElementById('pHeight').textContent = u.height ? u.height + ' cm' : '-';
    document.getElementById('pWeight').textContent = u.weight ? u.weight + ' kg' : '-';
    document.getElementById('pPhone').textContent = u.phone || '-';
    document.getElementById('pLocation').textContent = u.location || '-';
    document.getElementById('pIllnessActual').textContent = u.illnessActual || 'None';
    document.getElementById('pIllnessChronic').textContent = u.illnessChronic || 'None';
    document.getElementById('pMedications').textContent = u.medications || 'None';
    document.getElementById('pInsurance').textContent = u.insurance || '-';
    document.getElementById('pCoverage').textContent =
      u.notCovered === 'Yes' ? 'There are hospitals NOT covered by insurance' : 'All hospitals covered';

    const contactsEl = document.getElementById('pContacts');
    contactsEl.innerHTML = '';
    (u.contacts || []).forEach(c => {
      const div = document.createElement('div');
      div.className = 'contact-card';
      div.innerHTML = `
        <p class="name">${escapeHtml(c.name)} (${escapeHtml(c.rel)})</p>
        <p>Phone: ${escapeHtml(c.phone)}</p>
        ${c.email ? '<p>Email: ' + escapeHtml(c.email) + '</p>' : ''}
      `;
      contactsEl.appendChild(div);
    });

    const uncoveredEl = document.getElementById('pUncovered');
    uncoveredEl.innerHTML = '';
    if (u.notCovered === 'Yes' && u.uncoveredList) {
      const div = document.createElement('div');
      div.className = 'contact-card';
      div.innerHTML = '<p><strong>Hospitals not covered:</strong> ' + escapeHtml(u.uncoveredList) + '</p>';
      uncoveredEl.appendChild(div);
    }

    goto('page-profile');
  }

  function editProfile() {
    const u = getData();
    if (!u) { goto('page-signin'); return; }

    document.getElementById('fullName').value = u.name || '';
    document.getElementById('age').value = u.age || '';
    document.getElementById('gender').value = u.gender || '';
    document.getElementById('height').value = u.height || '';
    document.getElementById('weight').value = u.weight || '';
    document.getElementById('phone').value = u.phone || '';
    document.getElementById('location').value = u.location || '';
    document.getElementById('illnessActual').value = u.illnessActual || '';
    document.getElementById('illnessChronic').value = u.illnessChronic || '';
    document.getElementById('medications').value = u.medications || '';

    const container = document.getElementById('contactsContainer');
    container.innerHTML = '';
    (u.contacts || []).forEach(c => addContact(c));
    if (!(u.contacts || []).length) addContact();

    document.getElementById('insurance').value = u.insurance || '';
    const yes = document.querySelector('input[name="notCovered"][value="Yes"]');
    const no = document.querySelector('input[name="notCovered"][value="No"]');
    yes.checked = (u.notCovered === 'Yes');
    no.checked = (u.notCovered === 'No');
    document.getElementById('notCoveredList').value = u.uncoveredList || '';
    document.getElementById('notCoveredListWrap').style.display = (u.notCovered === 'Yes') ? 'block' : 'none';
    document.getElementById('locPreview').textContent = u.location || '-';

    seeded = true;
    document.getElementById('credsBackBtn').style.display = 'block';
    document.getElementById('insBackBtn').style.display = 'block';
    goto('page-creds');
  }

  function logout() {
    if (!confirm('Sign out of Health 360? (Your data stays saved on this device.)')) return;
    document.getElementById('logoutBtn').style.display = 'none';
    goto('page-welcome');
  }

  /* ---------- Utilities ---------- */
  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[a-zA-Z]{2,}$/.test(email);
  }
  function clearErrs(...ids) { ids.forEach(id => { document.getElementById(id).textContent = ''; }); }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  }
  function safeUrl(u) {
    try {
      const x = new URL(u);
      return (x.protocol === 'http:' || x.protocol === 'https:') ? x.href : '';
    } catch (e) { return ''; }
  }

  /* ---------- Wire up input restrictions ---------- */
  document.getElementById('phone').addEventListener('input', enforceDigits);
  document.querySelectorAll('.c-phone').forEach(p => p.addEventListener('input', enforceDigits));

  document.querySelectorAll('input[name="notCovered"]').forEach(r => {
    r.addEventListener('change', () => {
      const checked = document.querySelector('input[name="notCovered"]:checked');
      document.getElementById('notCoveredListWrap').style.display =
        checked && checked.value === 'Yes' ? 'block' : 'none';
    });
  });

  let seeded = false;
  const origGoto = goto;
  goto = function (id) {
    if (id === 'page-creds' && !seeded) {
      seeded = true;
      addContact();
    }
    origGoto(id);
  };
</script>
</body>
</html>
