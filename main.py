import streamlit as st
import google.generativeai as genai
import json
import os
import random

# ---------------- CONFIG ----------------

st.set_page_config(
    page_title="CASE FILES",
    layout="wide"
)


MODEL = None

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    API_KEY = None

# ---------------- UI ----------------

st.markdown("""
<style>

.stApp{
background:#0b0b0f;
color:white;
}

.title{
font-size:42px;
font-weight:800;
color:#e50914;
}

.card{
background:#181818;
padding:15px;
border-radius:12px;
border:1px solid #333;
margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SESSION ----------------

if "case" not in st.session_state:
    st.session_state.case = None

if "score" not in st.session_state:
    st.session_state.score = 0

if "found_evidence" not in st.session_state:
    st.session_state.found_evidence = []

if "found_contradictions" not in st.session_state:
    st.session_state.found_contradictions = []

# ---------------- CASE GENERATION ----------------

def generate_case():

    if MODEL:

        try:

            prompt = """
Create a murder mystery.

Return ONLY JSON.

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

Exactly 4 suspects.
Exactly 4 evidence.
Exactly 4 contradictions.

Keep everything short.
"""

            response = MODEL.generate_content(prompt)

            text = response.text

            text = text.replace(
                "```json",
                ""
            ).replace(
                "```",
                ""
            )

            return json.loads(text)

        except:
            pass

    # fallback

    return {

        "title":"The Blackwood Murder",

        "victim":"Victor Blackwood",

        "crime_scene":"Library",

        "murder_time":"9:30 PM",

        "weapon":"Letter Opener",

        "killer":"Arthur Kane",

        "hint":"Follow the inheritance.",

        "suspects":[

            {
                "name":"Arthur Kane",
                "occupation":"Lawyer",
                "relationship":"Business Partner",
                "alibi":"Library",
                "secret":"Huge Debt",
                "motive":"Inheritance"
            },

            {
                "name":"Sophia Reed",
                "occupation":"Artist",
                "relationship":"Daughter",
                "alibi":"Garden",
                "secret":"Argument",
                "motive":"Revenge"
            },

            {
                "name":"Daniel Hart",
                "occupation":"Doctor",
                "relationship":"Friend",
                "alibi":"Kitchen",
                "secret":"Forgery",
                "motive":"Money"
            },

            {
                "name":"Naomi Cole",
                "occupation":"Journalist",
                "relationship":"Ex Employee",
                "alibi":"Study",
                "secret":"Blackmail",
                "motive":"Exposure"
            }

        ],

        "evidence":[

            {
                "name":"Bank Transfer",
                "description":"Large payment",
                "points_to":"Arthur Kane"
            },

            {
                "name":"Threat Message",
                "description":"Victim threatened",
                "points_to":"Sophia Reed"
            },

            {
                "name":"Fingerprint",
                "description":"Found on weapon",
                "points_to":"Arthur Kane"
            },

            {
                "name":"Changed Will",
                "description":"Inheritance altered",
                "points_to":"Arthur Kane"
            }

        ],

        "contradictions":[

            {
                "title":"Library camera inactive",
                "suspect":"Arthur Kane"
            },

            {
                "title":"No garden witness",
                "suspect":"Sophia Reed"
            },

            {
                "title":"Kitchen closed",
                "suspect":"Daniel Hart"
            },

            {
                "title":"Study locked",
                "suspect":"Naomi Cole"
            }

        ]

    }

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.title("🕵 CASE FILES")

    if st.button("🎬 New Case"):

        st.session_state.case = generate_case()
        st.session_state.score = 0
        st.session_state.found_evidence = []
        st.session_state.found_contradictions = []

        st.rerun()

    if st.button("🔄 Restart"):

        st.session_state.score = 0
        st.session_state.found_evidence = []
        st.session_state.found_contradictions = []

        st.rerun()

# ---------------- START ----------------

if st.session_state.case is None:

    st.markdown(
        "<div class='title'>CASE FILES</div>",
        unsafe_allow_html=True
    )

    st.write("Start a new case.")

    st.stop()

case = st.session_state.case

# ---------------- HEADER ----------------

st.markdown(
    f"<div class='title'>{case['title']}</div>",
    unsafe_allow_html=True
)

c1,c2,c3,c4 = st.columns(4)

c1.metric("Victim", case["victim"])
c2.metric("Time", case["murder_time"])
c3.metric("Weapon", case["weapon"])
c4.metric("Score", st.session_state.score)

# ---------------- CRIME BOARD ----------------

st.subheader("📋 Crime Board")

st.info(
    f"""
Crime Scene: {case['crime_scene']}
"""
)

# ---------------- SUSPECT FILES ----------------

st.subheader("👥 Suspect Files")

for suspect in case["suspects"]:

    st.markdown(f"""
<div class="card">

<b>{suspect['name']}</b>

<br><br>

Occupation: {suspect['occupation']}

<br>

Relationship: {suspect['relationship']}

<br>

Alibi: {suspect['alibi']}

<br>

Secret: {suspect['secret']}

<br>

Motive: {suspect['motive']}

</div>
""", unsafe_allow_html=True)

# ---------------- EVIDENCE ----------------

st.subheader("🔍 Evidence Board")

for i,evidence in enumerate(
    case["evidence"]
):

    if st.button(
        f"Reveal {evidence['name']}",
        key=f"e{i}"
    ):

        if evidence["name"] not in st.session_state.found_evidence:

            st.session_state.found_evidence.append(
                evidence["name"]
            )

            st.session_state.score += 10

for evidence in case["evidence"]:

    if evidence["name"] in st.session_state.found_evidence:

        st.success(
            f"{evidence['name']} → {evidence['description']}"
        )

# ---------------- CONTRADICTIONS ----------------

st.subheader("⚠ Contradictions")

for i,con in enumerate(
    case["contradictions"]
):

    if st.button(
        f"Investigate {con['title']}",
        key=f"c{i}"
    ):

        if con["title"] not in st.session_state.found_contradictions:

            st.session_state.found_contradictions.append(
                con["title"]
            )

            st.session_state.score += 20

for con in st.session_state.found_contradictions:

    st.warning(con)

# ---------------- HINT ----------------

st.subheader("🧠 Detective Assistant")

if st.button("Get Hint"):

    st.info(case["hint"])

# ---------------- FINAL ACCUSATION ----------------

st.subheader("🎯 Final Accusation")

names = [
    s["name"]
    for s in case["suspects"]
]

choice = st.selectbox(
    "Choose Killer",
    names
)

if st.button("⚖ ACCUSE"):

    if choice == case["killer"]:

        st.success("🎉 CASE SOLVED")
        st.balloons()

    else:

        st.error(
            f"Wrong! Killer was {case['killer']}"
        )