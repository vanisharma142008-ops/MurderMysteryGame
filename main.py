import streamlit as st
import google.generativeai as genai
import json
import time
import random
import re

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="CASE FILES: Detective Mode",
    layout="wide"
)

# ---------------- GEMINI SETUP ----------------

MODEL = None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    MODEL = genai.GenerativeModel("gemini-1.5-flash")
except:
    MODEL = None

# ---------------- UI ----------------

st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #0b0b0f, #050505);
    color: white;
    font-family: Arial;
}

.title {
    font-size: 32px;
    font-weight: 900;
    color: #ff2a2a;
}

.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

for key, default in {
    "case": None,
    "score": 0,
    "found_evidence": [],
    "found_contradictions": [],
    "clues_unlocked": 1,
    "toast": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------- SAFE AI GENERATION ----------------

def generate_case():

    if MODEL is None:
        st.error("❌ Gemini API not configured (check secrets.toml)")
        return None

    try:
        seed = int(time.time() * 1000) + random.randint(1, 999999)

        prompt = f"""
You are a crime story generator.

Create a UNIQUE murder mystery.

Random seed: {seed}

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
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}},
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}},
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}},
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}}
],
"evidence": [
{{"name":"","description":"","points_to":""}},
{{"name":"","description":"","points_to":""}},
{{"name":"","description":"","points_to":""}},
{{"name":"","description":"","points_to":""}}
],
"contradictions": [
{{"title":"","suspect":""}},
{{"title":"","suspect":""}},
{{"title":"","suspect":""}},
{{"title":"","suspect":""}}
]
}}
"""

        response = MODEL.generate_content(
            prompt,
            generation_config={
                "temperature": 1.3,
                "top_p": 0.95
            }
        )

        if not response or not response.text:
            st.error("❌ Empty response from AI")
            return None

        text = response.text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            st.error("❌ AI returned invalid format")
            return None

        case = json.loads(match.group())
        case["seed"] = seed

        return case

    except Exception as e:
        st.error(f"❌ AI Error: {e}")
        return None


# ---------------- RESET ----------------

def reset_game():
    new_case = generate_case()

    if new_case is None:
        st.warning("⚠ Could not generate case. Try again.")
        return

    st.session_state.case = new_case
    st.session_state.score = 0
    st.session_state.found_evidence = []
    st.session_state.found_contradictions = []
    st.session_state.clues_unlocked = 1
    st.session_state.toast = False


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("🕵 CASE FILES")

    if st.button("🎬 New Case", use_container_width=True):
        reset_game()
        st.rerun()

    if st.button("🔄 Restart", use_container_width=True):
        reset_game()
        st.rerun()


# ---------------- START CHECK ----------------

if st.session_state.case is None:
    st.markdown("<div class='title'>CASE FILES</div>", unsafe_allow_html=True)
    st.write("Click **New Case** to start.")
    st.stop()

case = st.session_state.case

# ---------------- TOAST (ONCE ONLY) ----------------

if not st.session_state.toast:
    st.toast("New case loaded 🕵️", icon="🔴")
    st.session_state.toast = True


# ---------------- HEADER ----------------

st.markdown(f"""
<div class="card">
<div class="title">🕵 {case.get('title','Unknown Case')}</div>
<b>Victim:</b> {case.get('victim')} <br>
<b>Time:</b> {case.get('murder_time')} <br>
<b>Weapon:</b> {case.get('weapon')} <br>
<b>Score:</b> {st.session_state.score}
</div>
""", unsafe_allow_html=True)


# ---------------- CRIME SCENE ----------------

st.subheader("📍 Crime Scene")
st.info(case.get("crime_scene", "Unknown"))


# ---------------- SUSPECTS ----------------

st.subheader("👥 Suspects")

for s in case.get("suspects", []):
    st.markdown(f"""
    <div class="card">
    <b>{s.get('name','')}</b><br><br>
    Occupation: {s.get('occupation','')}<br>
    Relationship: {s.get('relationship','')}<br>
    Alibi: {s.get('alibi','')}<br>
    Secret: {s.get('secret','')}<br>
    Motive: {s.get('motive','')}
    </div>
    """, unsafe_allow_html=True)


# ---------------- EVIDENCE ----------------

st.subheader("🔍 Evidence")

for i, e in enumerate(case.get("evidence", [])):

    locked = i >= st.session_state.clues_unlocked

    if locked:
        st.button("🔒 Locked", disabled=True, key=f"l{i}")
    else:
        if st.button(f"Reveal {e.get('name')}", key=f"e{i}"):

            if e.get("name") not in st.session_state.found_evidence:
                st.session_state.found_evidence.append(e.get("name"))
                st.session_state.score += 10
                st.session_state.clues_unlocked = min(
                    st.session_state.clues_unlocked + 1,
                    len(case.get("evidence", []))
                )
                st.rerun()


for e in case.get("evidence", []):
    if e.get("name") in st.session_state.found_evidence:
        st.success(f"🧩 {e.get('name')} → {e.get('description')}")


# ---------------- CONTRADICTIONS ----------------

st.subheader("⚠ Contradictions")

for i, c in enumerate(case.get("contradictions", [])):

    if st.button(f"Check {c.get('title')}", key=f"c{i}"):

        if c.get("title") not in st.session_state.found_contradictions:
            st.session_state.found_contradictions.append(c.get("title"))
            st.session_state.score += 20
            st.rerun()


for c in st.session_state.found_contradictions:
    st.error(f"⚠ {c}")


# ---------------- FINAL ACCUSATION ----------------

st.subheader("🎯 Final Accusation")

names = [s.get("name") for s in case.get("suspects", [])]

choice = st.selectbox("Who is the killer?", names)

if st.button("⚖ Accuse"):

    if choice == case.get("killer"):
        st.success("🎉 CASE SOLVED!")
        st.balloons()
    else:
        st.error(f"❌ Wrong! Killer was {case.get('killer')}")