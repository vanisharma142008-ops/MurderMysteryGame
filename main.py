import streamlit as st
import google.generativeai as genai
import json
import time
import random
import re

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="🕵️ Case Files",
    layout="wide"
)

# ---------------- API SETUP ----------------

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
}

/* Title */
.title {
    font-size: 34px;
    font-weight: 900;
    color: #ff2a2a;
    margin-bottom: 10px;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 10px;
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

for k, v in {
    "case": None,
    "score": 0,
    "evidence": [],
    "contradictions": [],
    "clue": 1
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------- SAFE AI CASE ----------------

def generate_case():

    if MODEL is None:
        return None

    try:
        seed = int(time.time() * 1000) + random.randint(1, 999999)

        prompt = f"""
Create a unique murder mystery.

Seed: {seed}

Return ONLY JSON:

{{
"title":"",
"victim":"",
"crime_scene":"",
"murder_time":"",
"weapon":"",
"killer":"",
"hint":"",
"suspects":[
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}},
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}},
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}},
{{"name":"","occupation":"","relationship":"","alibi":"","secret":"","motive":""}}
],
"evidence":[
{{"name":"","description":"","points_to":""}},
{{"name":"","description":"","points_to":""}},
{{"name":"","description":"","points_to":""}},
{{"name":"","description":"","points_to":""}}
],
"contradictions":[
{{"title":"","suspect":""}},
{{"title":"","suspect":""}},
{{"title":"","suspect":""}},
{{"title":"","suspect":""}}
]
}}
"""

        res = MODEL.generate_content(
            prompt,
            generation_config={
                "temperature": 1.3,
                "top_p": 0.95
            }
        )

        text = res.text.replace("```json", "").replace("```", "")

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            return None

        case = json.loads(match.group())
        case["seed"] = seed
        return case

    except:
        return None


# ---------------- RESET ----------------

def new_game():
    case = generate_case()

    if case is None:
        case = {
            "title": "Offline Case (Fallback Mode)",
            "victim": "Unknown",
            "crime_scene": "Unknown",
            "murder_time": "Unknown",
            "weapon": "Unknown",
            "killer": "Unknown",
            "hint": "AI not available",
            "suspects": [],
            "evidence": [],
            "contradictions": []
        }

    st.session_state.case = case
    st.session_state.score = 0
    st.session_state.evidence = []
    st.session_state.contradictions = []
    st.session_state.clue = 1


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("🕵️ DETECTIVE PANEL")

    if st.button("🎬 New Case", use_container_width=True):
        new_game()
        st.rerun()

    if st.button("🔄 Reset", use_container_width=True):
        new_game()
        st.rerun()


# ---------------- START ----------------

if st.session_state.case is None:
    st.markdown("<div class='title'>CASE FILES</div>", unsafe_allow_html=True)
    st.write("Click **New Case** to begin investigation.")
    st.stop()

case = st.session_state.case


# ---------------- HEADER ----------------

st.markdown(f"""
<div class="card">
<div class="title">🕵️ {case['title']}</div>

<b>Victim:</b> {case['victim']} <br>
<b>Time:</b> {case['murder_time']} <br>
<b>Weapon:</b> {case['weapon']} <br>
<b>Score:</b> {st.session_state.score}
</div>
""", unsafe_allow_html=True)


# ---------------- CRIME SCENE ----------------

st.subheader("📍 Crime Scene")
st.info(case["crime_scene"])


# ---------------- SUSPECTS ----------------

st.subheader("👥 Suspects")

for s in case.get("suspects", []):
    st.markdown(f"""
    <div class="card">
    <b>{s['name']}</b><br>
    Occupation: {s['occupation']}<br>
    Relationship: {s['relationship']}<br>
    Alibi: {s['alibi']}<br>
    Secret: {s['secret']}<br>
    Motive: {s['motive']}
    </div>
    """, unsafe_allow_html=True)


# ---------------- EVIDENCE ----------------

st.subheader("🔍 Evidence Board")

for i, e in enumerate(case.get("evidence", [])):

    locked = i >= st.session_state.clue

    if locked:
        st.button("🔒 Locked", disabled=True, key=f"l{i}")
    else:
        if st.button(f"Reveal {e['name']}", key=f"e{i}"):

            if e["name"] not in st.session_state.evidence:
                st.session_state.evidence.append(e["name"])
                st.session_state.score += 10
                st.session_state.clue += 1
                st.rerun()

for e in case.get("evidence", []):
    if e["name"] in st.session_state.evidence:
        st.success(f"🧩 {e['name']} → {e['description']}")


# ---------------- CONTRADICTIONS ----------------

st.subheader("⚠ Contradictions")

for i, c in enumerate(case.get("contradictions", [])):

    if st.button(f"Check {c['title']}", key=f"c{i}"):

        if c["title"] not in st.session_state.contradictions:
            st.session_state.contradictions.append(c["title"])
            st.session_state.score += 20
            st.rerun()

for c in st.session_state.contradictions:
    st.error(f"⚠ {c}")


# ---------------- HINT ----------------

st.subheader("🧠 Hint")

if st.button("Get Hint"):
    st.info(case["hint"])


# ---------------- FINAL ACCUSATION ----------------

st.subheader("🎯 Final Decision")

names = [s["name"] for s in case.get("suspects", [])]

choice = st.selectbox("Who is the killer?", names if names else ["No suspects"])

if st.button("⚖ Accuse"):

    if choice == case.get("killer"):
        st.success("🎉 CASE SOLVED!")
        st.balloons()
    else:
        st.error(f"❌ Wrong! Killer was {case.get('killer')}")