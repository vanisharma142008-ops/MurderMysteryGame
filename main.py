import streamlit as st
import google.generativeai as genai
import json
import time
import random

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="CASE FILES: Detective Mode",
    layout="wide"
)

# ---------------- GEMINI SETUP ----------------

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    MODEL = genai.GenerativeModel("gemini-1.5-flash")
except:
    MODEL = None

# ---------------- MODERN UI ----------------

st.markdown("""
<style>

.stApp {
    background: radial-gradient(circle at top, #0b0b0f, #050505);
    color: white;
    font-family: Arial;
}

/* Header Title */
.title {
    font-size: 34px;
    font-weight: 900;
    color: #ff2a2a;
    letter-spacing: 1px;
}

/* Glass Card */
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 10px;
    backdrop-filter: blur(6px);
}

/* Buttons */
button {
    border-radius: 10px !important;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION INIT ----------------

for key, default in {
    "case": None,
    "score": 0,
    "found_evidence": [],
    "found_contradictions": [],
    "clues_unlocked": 1,
    "toast_shown": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------- AI CASE GENERATOR ----------------

def generate_case():

    if not MODEL:
        st.error("Gemini API not found. AI cases cannot be generated.")
        return None

    try:
        seed = int(time.time() * 1000) + random.randint(1, 999999)

        prompt = f"""
You are a world-class crime story writer.

Generate a COMPLETELY UNIQUE murder mystery case.

Rules:
- Never reuse old patterns (no repeated motives like inheritance/revenge)
- Make story fresh, cinematic, realistic
- Ensure strong detective logic

Random Seed: {seed}

Return ONLY valid JSON:

{{
"title": "",
"victim": "",
"crime_scene": "",
"murder_time": "",
"weapon": "",
"killer": "",
"hint": "",
"suspects": [
{{
"name": "",
"occupation": "",
"relationship": "",
"alibi": "",
"secret": "",
"motive": ""
}}
],
"evidence": [
{{
"name": "",
"description": "",
"points_to": ""
}}
],
"contradictions": [
{{
"title": "",
"suspect": ""
}}
]
}}

STRICT:
- 4 suspects
- 4 evidence items
- 4 contradictions
- Keep everything short and sharp
"""

        response = MODEL.generate_content(
            prompt,
            generation_config={
                "temperature": 1.25,
                "top_p": 0.95
            }
        )

        text = response.text.replace("```json", "").replace("```", "").strip()
        case = json.loads(text)
        case["seed"] = seed
        return case

    except Exception as e:
        st.error(f"AI Error: {e}")
        return None


# ---------------- RESET GAME ----------------

def reset_game():
    new_case = generate_case()

    if new_case is None:
        return

    st.session_state.case = new_case
    st.session_state.score = 0
    st.session_state.found_evidence = []
    st.session_state.found_contradictions = []
    st.session_state.clues_unlocked = 1
    st.session_state.toast_shown = False


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("🕵 CASE FILES")

    if st.button("🎬 New Case", use_container_width=True):
        reset_game()
        st.rerun()

    if st.button("🔄 Restart Investigation", use_container_width=True):
        reset_game()
        st.rerun()


# ---------------- START SCREEN ----------------

if st.session_state.case is None:
    st.markdown("<div class='title'>CASE FILES: DETECTIVE MODE</div>", unsafe_allow_html=True)
    st.write("Click **New Case** to start your investigation.")
    st.stop()

case = st.session_state.case

if not st.session_state.toast_shown:
    st.toast("New case loaded 🕵️‍♂️", icon="🔴")
    st.session_state.toast_shown = True


# ---------------- HEADER ----------------

st.markdown(f"""
<div class="card">
    <div class="title">🕵 {case['title']}</div>
    <br>
    <b>Victim:</b> {case['victim']} <br>
    <b>Time:</b> {case['murder_time']} <br>
    <b>Weapon:</b> {case['weapon']} <br>
    <b>Score:</b> {st.session_state.score} <br>
</div>
""", unsafe_allow_html=True)


# ---------------- CRIME SCENE ----------------

st.subheader("📍 Crime Scene")
st.info(case["crime_scene"])


# ---------------- SUSPECTS ----------------

st.subheader("👥 Suspects")

for s in case["suspects"]:
    st.markdown(f"""
    <div class="card">
        <b>{s['name']}</b><br><br>
        🧠 Occupation: {s['occupation']}<br>
        🤝 Relationship: {s['relationship']}<br>
        🕒 Alibi: {s['alibi']}<br>
        🔒 Secret: {s['secret']}<br>
        🎯 Motive: {s['motive']}
    </div>
    """, unsafe_allow_html=True)


# ---------------- EVIDENCE SYSTEM ----------------

st.subheader("🔍 Evidence Board")

for i, e in enumerate(case["evidence"]):

    locked = i >= st.session_state.clues_unlocked

    if locked:
        st.button("🔒 Locked Evidence", disabled=True, key=f"lock{i}")
    else:
        if st.button(f"Reveal {e['name']}", key=f"e{i}"):

            if e["name"] not in st.session_state.found_evidence:
                st.session_state.found_evidence.append(e["name"])
                st.session_state.score += 10

                st.session_state.clues_unlocked = min(
                    st.session_state.clues_unlocked + 1,
                    len(case["evidence"])
                )

                st.rerun()


for e in case["evidence"]:
    if e["name"] in st.session_state.found_evidence:
        st.success(f"🧩 {e['name']} → {e['description']}")


# ---------------- CONTRADICTIONS ----------------

st.subheader("⚠ Contradictions")

for i, c in enumerate(case["contradictions"]):

    if st.button(f"Investigate {c['title']}", key=f"c{i}"):

        if c["title"] not in st.session_state.found_contradictions:
            st.session_state.found_contradictions.append(c["title"])
            st.session_state.score += 20
            st.rerun()

for c in st.session_state.found_contradictions:
    st.error(f"⚠ {c}")


# ---------------- HINT ----------------

st.subheader("🧠 Detective Hint")

if st.button("Get Hint"):
    st.info(case["hint"])


# ---------------- FINAL ACCUSATION ----------------

st.subheader("🎯 Final Accusation")

names = [s["name"] for s in case["suspects"]]

choice = st.selectbox("Who is the killer?", names)

if st.button("⚖ Submit Accusation"):

    if choice == case["killer"]:
        st.success("🎉 CASE SOLVED! YOU ARE A MASTER DETECTIVE")
        st.balloons()
    else:
        st.error(f"❌ Wrong accusation! The real killer was {case['killer']}")