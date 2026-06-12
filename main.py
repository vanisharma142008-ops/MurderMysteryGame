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

/* GLOBAL CINEMA DARK MODE */
.stApp {
    background: radial-gradient(circle at top, #0a0a0f, #000000);
    color: white;
}

/* TITLE GLITCH STYLE */
.title {
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 4px;
    text-align: center;
    color: #ff2b2b;
    text-shadow: 0 0 10px #ff2b2b;
}

/* SUBTITLE */
.subtitle {
    text-align: center;
    color: #aaa;
    font-size: 14px;
}

/* GLASS PANEL */
.glass {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 16px;
    backdrop-filter: blur(12px);
}

/* SUSPECT CARD */
.suspect {
    background: rgba(255,255,255,0.04);
    border-left: 3px solid #ff2b2b;
    padding: 14px;
    border-radius: 10px;
}

/* EVIDENCE CARD */
.evidence {
    background: rgba(0,255,100,0.06);
    border-left: 4px solid #00ff88;
    padding: 10px;
    border-radius: 10px;
}

/* BUTTON STYLE */
.stButton>button {
    background: black;
    color: white;
    border: 1px solid #333;
    border-radius: 8px;
}

.stButton>button:hover {
    border: 1px solid #ff2b2b;
    box-shadow: 0 0 10px #ff2b2b;
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

def cinematic_intro():
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:40px; font-weight:900; color:#ff2b2b; letter-spacing:3px;">
            CASE FILES
        </div>
        <div style="color:#888; margin-top:10px;">
            INITIATING INVESTIGATION SYSTEM...
        </div>
    </div>
    """, unsafe_allow_html=True)

    progress = st.empty()

    for i in range(1, 101, 3):
        time.sleep(0.02)
        progress.markdown(f"""
        <div style="width:100%;background:#222;height:8px;border-radius:5px;">
            <div style="width:{i}%;background:#ff2b2b;height:8px;border-radius:5px;"></div>
        </div>
        """, unsafe_allow_html=True)

    st.success("🕵️ Case Loaded. Entering Crime Scene...")

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
    st.markdown("## 🕵️ DETECTIVE CONTROL PANEL")

    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.05);
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 10px;
    ">
        <b>🎯 Score:</b> {st.session_state.score}<br>
        <b>🔍 Evidence Found:</b> {len(st.session_state.evidence)}<br>
        <b>⚠ Clues Unlocked:</b> {st.session_state.clue_level}
    </div>
    """, unsafe_allow_html=True)

    progress = min(100, len(st.session_state.evidence) * 20)

    st.markdown(f"""
    <div style="margin-bottom:10px;">
        <b>Case Progress</b>
        <div style="background:#222;height:10px;border-radius:5px;">
            <div style="width:{progress}%;height:10px;background:#ff2b2b;border-radius:5px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🎬 NEW CASE", use_container_width=True):
        new_case()
        st.rerun()

    if st.button("🔄 RESET CASE", use_container_width=True):
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
<div class="glass" style="text-align:center">
    <div class="title">🕵️ {case['title']}</div>
    <div class="subtitle">
        🧠 Every clue changes the truth • Every contradiction exposes the killer
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;color:#888;font-size:14px;margin-bottom:10px'>
📡 Case File Active • Surveillance Mode Enabled • Truth is hidden in contradictions
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

    is_locked = i >= st.session_state.clue_level

    with st.container():

        if is_locked:
            st.button(f"🔒 Evidence File Locked", disabled=True, key=f"l{i}")
        else:
            if st.button(f"🔓 Unlock File: {e['name']}", key=f"e{i}"):

                if e["name"] not in st.session_state.evidence:
                    st.session_state.evidence.append(e["name"])
                    st.session_state.score += 10
                    st.session_state.clue_level += 1
                    st.success("📂 Evidence added to case board")
                    st.rerun()

# Evidence display (better cards)
st.markdown("### 📁 Evidence Board")

if not st.session_state.evidence:
    st.info("No evidence unlocked yet... start investigating.")

for e in case.get("evidence", []):
    if e["name"] in st.session_state.evidence:
        st.markdown(f"""
        <div style="
            background: rgba(0,255,100,0.06);
            border-left: 4px solid #00ff88;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 8px;
        ">
            🧩 <b>{e['name']}</b><br>
            <span style="color:#aaa">{e['description']}</span>
        </div>
        """, unsafe_allow_html=True)


# ---------------- CONTRADICTIONS ----------------

st.markdown("## ⚠ Suspicious Patterns")

for i, c in enumerate(case.get("contradictions", [])):

    if st.button(f"🔍 Analyze: {c['title']}", key=f"c{i}"):

        if c["title"] not in st.session_state.found_contradictions:
            st.session_state.found_contradictions.append(c["title"])
            st.session_state.score += 20
            st.success("⚠ Contradiction added to evidence board")
            st.rerun()

st.markdown("### 📌 Discovered Contradictions")

if not st.session_state.found_contradictions:
    st.warning("No contradictions found yet... investigate suspects carefully.")

for c in st.session_state.found_contradictions:
    st.markdown(f"""
    <div style="
        background: rgba(255,50,50,0.08);
        border-left: 4px solid #ff3b3b;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 8px;
    ">
        ⚠️ {c}
    </div>
    """, unsafe_allow_html=True)


# ---------------- FINAL VERDICT ----------------

st.markdown("## ⚖ COURTROOM // FINAL VERDICT")

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    background:rgba(255,255,255,0.03);
    border-radius:12px;
">
    🧑‍⚖️ The court awaits your judgment. Choose carefully.
</div>
""", unsafe_allow_html=True)

names = [s["name"] for s in case.get("suspects", [])]

choice = st.selectbox("Who is the killer?", names if names else ["Unknown"])

if st.button("⚖ Deliver Verdict"):

    st.markdown("### 🎬 Verdict Processing...")

    time.sleep(1)

    if choice == case.get("killer"):
        st.success("🎉 JUSTICE SERVED — CASE CLOSED")
        st.balloons()

        st.markdown("""
        <div style="text-align:center; color:#aaa;">
        The truth always leaves traces behind...
        </div>
        """, unsafe_allow_html=True)

    else:
        st.error("❌ WRONG VERDICT")

        st.markdown(f"""
        <div style="color:#aaa;text-align:center;">
        The real killer was: <b>{case.get('killer')}</b>
        </div>
        """, unsafe_allow_html=True)