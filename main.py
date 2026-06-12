import streamlit as st
import google.generativeai as genai
import json

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="CASE FILES",
    layout="wide"
)

# ---------------- GEMINI SETUP ----------------

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    MODEL = genai.GenerativeModel("gemini-1.5-flash")
except:
    MODEL = None

# ---------------- UI ----------------

st.markdown("""
<style>

.stApp{
    background: radial-gradient(circle at top, #0b0b0f, #050505);
    color:white;
}

.title{
    font-size:30px;
    font-weight:800;
    color:#ff2a2a;
    margin-bottom:10px;
}

.card{
    background: linear-gradient(145deg, #1a1a1a, #0f0f0f);
    padding:12px;
    border-radius:10px;
    border:1px solid #2a2a2a;
    margin-bottom:10px;
    font-size:14px;
    line-height:1.5;
}

button {
    border-radius:8px !important;
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
    "toast_shown": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------- CASE GENERATION ----------------

def generate_case():

    if MODEL:
        try:
            prompt = """
Create a murder mystery.

Return ONLY JSON:

{
"title":"",
"victim":"",
"crime_scene":"",
"murder_time":"",
"weapon":"",
"killer":"",
"hint":"",
"suspects":[
{
"name":"",
"occupation":"",
"relationship":"",
"alibi":"",
"secret":"",
"motive":""
}
],
"evidence":[
{
"name":"",
"description":"",
"points_to":""
}
],
"contradictions":[
{
"title":"",
"suspect":""
}
]
}

Exactly 4 suspects, 4 evidence, 4 contradictions.
Keep it short.
"""

            response = MODEL.generate_content(prompt)
            text = response.text.replace("```json", "").replace("```", "")
            return json.loads(text)

        except:
            pass

    # fallback
    return {
        "title": "The Blackwood Murder",
        "victim": "Victor Blackwood",
        "crime_scene": "Library",
        "murder_time": "9:30 PM",
        "weapon": "Letter Opener",
        "killer": "Arthur Kane",
        "hint": "Follow the inheritance.",
        "suspects": [
            {"name":"Arthur Kane","occupation":"Lawyer","relationship":"Business Partner","alibi":"Library","secret":"Debt","motive":"Inheritance"},
            {"name":"Sophia Reed","occupation":"Artist","relationship":"Daughter","alibi":"Garden","secret":"Argument","motive":"Revenge"},
            {"name":"Daniel Hart","occupation":"Doctor","relationship":"Friend","alibi":"Kitchen","secret":"Forgery","motive":"Money"},
            {"name":"Naomi Cole","occupation":"Journalist","relationship":"Ex Employee","alibi":"Study","secret":"Blackmail","motive":"Exposure"}
        ],
        "evidence": [
            {"name":"Bank Transfer","description":"Large payment","points_to":"Arthur Kane"},
            {"name":"Threat Message","description":"Victim threatened","points_to":"Sophia Reed"},
            {"name":"Fingerprint","description":"On weapon","points_to":"Arthur Kane"},
            {"name":"Changed Will","description":"Inheritance altered","points_to":"Arthur Kane"}
        ],
        "contradictions": [
            {"title":"Library camera inactive","suspect":"Arthur Kane"},
            {"title":"No garden witness","suspect":"Sophia Reed"},
            {"title":"Kitchen closed","suspect":"Daniel Hart"},
            {"title":"Study locked","suspect":"Naomi Cole"}
        ]
    }


# ---------------- RESET ----------------

def reset_game():
    st.session_state.case = generate_case()
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

    if st.button("🔄 Restart Case", use_container_width=True):
        reset_game()
        st.rerun()


# ---------------- START SCREEN ----------------

if st.session_state.case is None:
    st.markdown("<div class='title'>CASE FILES</div>", unsafe_allow_html=True)
    st.write("Start a new case to begin investigation.")
    st.stop()

case = st.session_state.case

# toast only once
if not st.session_state.toast_shown:
    st.toast("New case loaded 🕵️", icon="🔴")
    st.session_state.toast_shown = True


# ---------------- HEADER ----------------

st.markdown(f"""
<div style="
background:#121212;
padding:15px;
border-radius:12px;
border:1px solid #2a2a2a;
margin-bottom:15px;
">

<h3 style="color:#ff2a2a;margin:0;">🕵 {case['title']}</h3>

<p>
<b>Victim:</b> {case['victim']} <br>
<b>Time:</b> {case['murder_time']} <br>
<b>Weapon:</b> {case['weapon']} <br>
<b>Score:</b> {st.session_state.score}
</p>

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
    Occupation: {s['occupation']}<br>
    Relationship: {s['relationship']}<br>
    Alibi: {s['alibi']}<br>
    Secret: {s['secret']}<br>
    Motive: {s['motive']}
    </div>
    """, unsafe_allow_html=True)


# ---------------- EVIDENCE ----------------

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
        st.success(f"{e['name']} → {e['description']}")


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

choice = st.selectbox("Choose Killer", names)

if st.button("⚖ ACCUSE"):

    if choice == case["killer"]:
        st.success("🎉 CASE SOLVED!")
        st.balloons()
    else:
        st.error(f"❌ Wrong! Killer was {case['killer']}")