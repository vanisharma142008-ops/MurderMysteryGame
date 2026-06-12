import streamlit as st
from openai import OpenAI
import json
import time
import random
import re

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="CASE FILES // DETECTIVE MODE",
    layout="wide"
)

# ---------------- OPENROUTER AI ----------------

client = None

try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=st.secrets.get("OPENROUTER_API_KEY")
    )
except:
    client = None


# ---------------- CINEMATIC UI ----------------

st.markdown("""
<style>

/* DARK CINEMATIC BACKGROUND */
.stApp {
    background: radial-gradient(circle at top, #0b0b0f, #000000);
    color: white;
    font-family: 'Arial';
}

/* TITLE (MOVIE STYLE) */
.title {
    font-size: 44px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #ff2b2b;
    text-align: center;
    margin-bottom: 10px;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    color: #aaaaaa;
    margin-bottom: 20px;
}

/* GLASS CARD */
.glass {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 16px;
    padding: 16px;
    backdrop-filter: blur(12px);
    margin-bottom: 12px;
}

/* SUSPECT CARD */
.suspect {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    border-left: 3px solid #ff2b2b;
    padding: 14px;
    border-radius: 12px;
    margin-bottom: 10px;
}

/* BUTTONS */
.stButton>button {
    border-radius: 10px;
    font-weight: 700;
    border: 1px solid #333;
}

/* SCARY EFFECT BOX */
.evidence {
    background: rgba(255,0,0,0.08);
    border: 1px solid rgba(255,0,0,0.2);
    padding: 10px;
    border-radius: 10px;
    margin: 5px 0;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION ----------------

for k, v in {
    "case": None,
    "score": 0,
    "evidence": [],
    "clue_level": 1,
    "found_contradictions": []
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ---------------- AI GENERATOR ----------------

def generate_case():

    try:
        if client is None:
            return None

        seed = int(time.time() * 1000) + random.randint(1, 999999)

        prompt = f"""
You are a noir crime story engine.

Generate a DARK murder mystery.

Seed: {seed}

Return ONLY valid JSON:

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

        res = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return ONLY valid JSON. No explanation."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.2
        )

        text = res.choices[0].message.content.strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if not match:
            return None

        return json.loads(match.group())

    except:
        return None


# ---------------- START GAME ----------------

def new_case():
    case = generate_case()

    if case is None:
        case = {
            "title": "BLACKOUT MURDER FILE",
            "victim": "Unknown Victim",
            "crime_scene": "Abandoned Mansion",
            "murder_time": "03:33 AM",
            "weapon": "Unknown",
            "killer": "Unknown",
            "hint": "Even darkness leaves footprints.",
            "suspects": [],
            "evidence": [],
            "contradictions": []
        }

    st.session_state.case = case
    st.session_state.score = 0
    st.session_state.evidence = []
    st.session_state.clue_level = 1
    st.session_state.found_contradictions = []


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.title("🕵️ DETECTIVE BOARD")

    if st.button("🎬 NEW CASE", use_container_width=True):
        new_case()
        st.rerun()

    if st.button("🔄 RESET", use_container_width=True):
        new_case()
        st.rerun()


# ---------------- START SCREEN ----------------

if st.session_state.case is None:
    st.markdown("<div class='title'>CASE FILES</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>A crime awaits your judgment...</div>", unsafe_allow_html=True)
    st.stop()

case = st.session_state.case


# ---------------- HEADER (CINEMATIC) ----------------

st.markdown(f"""
<div class="glass">
    <div class="title">{case['title']}</div>
    <div class="subtitle">Every clue hides a lie...</div>
</div>
""", unsafe_allow_html=True)


# ---------------- CASE INFO ----------------

st.markdown("## 📁 Case Overview")
st.markdown(f"""
<div class="glass">
<b>Victim:</b> {case['victim']} <br>
<b>Time:</b> {case['murder_time']} <br>
<b>Weapon:</b> {case['weapon']} <br>
<b>Score:</b> {st.session_state.score}
</div>
""", unsafe_allow_html=True)


# ---------------- CRIME SCENE ----------------

st.markdown("## 📍 Crime Scene")
st.info(case["crime_scene"])


# ---------------- SUSPECTS ----------------

st.markdown("## 👤 Suspects")

for s in case.get("suspects", []):
    st.markdown(f"""
    <div class="suspect">
        <b>{s['name']}</b><br>
        {s['occupation']} | {s['relationship']}<br><br>
        🕒 Alibi: {s['alibi']}<br>
        🔒 Secret: {s['secret']}<br>
        🎯 Motive: {s['motive']}
    </div>
    """, unsafe_allow_html=True)


# ---------------- EVIDENCE ----------------

st.markdown("## 🔍 Evidence Locker")

for i, e in enumerate(case.get("evidence", [])):

    locked = i >= st.session_state.clue_level

    if locked:
        st.button("🔒 Locked Evidence", disabled=True, key=f"l{i}")
    else:
        if st.button(f"Inspect {e['name']}", key=f"e{i}"):

            if e["name"] not in st.session_state.evidence:
                st.session_state.evidence.append(e["name"])
                st.session_state.score += 10
                st.session_state.clue_level += 1
                st.rerun()

for e in case.get("evidence", []):
    if e["name"] in st.session_state.evidence:
        st.markdown(f"""
        <div class="evidence">
        🧩 {e['name']} → {e['description']}
        </div>
        """, unsafe_allow_html=True)


# ---------------- CONTRADICTIONS ----------------

st.markdown("## ⚠ Case Contradictions")

for i, c in enumerate(case.get("contradictions", [])):

    if st.button(f"Analyze {c['title']}", key=f"c{i}"):

        if c["title"] not in st.session_state.found_contradictions:
            st.session_state.found_contradictions.append(c["title"])
            st.session_state.score += 20
            st.rerun()

for c in st.session_state.found_contradictions:
    st.error(f"⚠ {c}")


# ---------------- FINAL VERDICT ----------------

st.markdown("## 🎯 Final Verdict Room")

names = [s["name"] for s in case.get("suspects", [])]

choice = st.selectbox("Who committed the crime?", names if names else ["Unknown"])

if st.button("⚖ Deliver Verdict"):

    if choice == case.get("killer"):
        st.success("🎉 CASE CLOSED — JUSTICE SERVED")
        st.balloons()
    else:
        st.error(f"❌ Wrong suspect. True killer was: {case.get('killer')}")