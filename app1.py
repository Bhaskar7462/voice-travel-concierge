import streamlit as st
import requests
import Speech_To_Text as STT
from Text_To_Speech import speak

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(page_title="Voice Travel Concierge", layout="centered")

# ==================================================
# BASIC DARK UI (NO BUTTON COLOR CHANGE)
# ==================================================
st.markdown("""
<style>
.stApp { background-color:#0e1117; color:#e6e6e6; }
.app-title { text-align:center; font-size:38px; font-weight:700; margin-top:30px; }
.app-subtitle { text-align:center; font-size:15px; color:#9aa4b2; margin-bottom:40px; }
.section-title { text-align:center; font-size:22px; font-weight:600; margin-top:35px; }
.card {
    background-color:#161a23;
    padding:18px;
    border-radius:12px;
    border:1px solid #242a38;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
defaults = {
    "user_input": "",
    "details": {},
    "itinerary": "",
    "audio_bytes": None,
    "images": [],
    "generate_clicked": False
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==================================================
# API CONFIG
# ==================================================
API_KEY = st.secrets["OPENROUTER_API_KEY"]
UNSPLASH_KEY = st.secrets["UNSPLASH_ACCESS_KEY"]
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# ==================================================
# HEADER
# ==================================================
st.markdown("<div class='app-title'>Voice Travel Concierge</div>", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>Plan your trip using just your voice</div>", unsafe_allow_html=True)

# ==================================================
# SAY BUTTON (EXACT CENTER)
# ==================================================
col1, col2, col3 = st.columns([3,2,3])
with col2:
    say_clicked = st.button("   🎙 Say   ")

if say_clicked:
    with st.spinner("Listening..."):
        spoken = STT.get_text()

    if spoken:
        for k in defaults:
            st.session_state[k] = defaults[k]
        st.session_state.user_input = spoken
    else:
        st.error("Could not understand your voice")

# ==================================================
# LLM CALL
# ==================================================
def deepseek_generate(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-r1-0528",
        "messages": [
            {"role": "system", "content": "You are a precise travel assistant"},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 700
    }
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ==================================================
# UNSPLASH IMAGE FETCH
# ==================================================
def get_images(place, count=6):
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": place, "per_page": count, "orientation": "landscape"}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return [img["urls"]["regular"] for img in r.json()["results"]]

# ==================================================
# PARSER
# ==================================================
def parse_details(text):
    data = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip().lower()] = v.strip()

    if "source" not in data or "destination" not in data:
        return None

    data["days"] = data.get("days", "3")
    data["budget"] = data.get("budget", "5000")
    return data

# ==================================================
# SHOW USER REQUEST
# ==================================================
if st.session_state.user_input:
    st.markdown("<div class='section-title'>Your Request</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>{st.session_state.user_input}</div>", unsafe_allow_html=True)

# ==================================================
# EXTRACT DETAILS
# ==================================================
if st.session_state.user_input and not st.session_state.details:
    prompt = f"""
Extract travel details.

Sentence:
{st.session_state.user_input}

Format:
Source:
Destination:
Days:
Budget:
"""
    parsed = parse_details(deepseek_generate(prompt))
    if parsed:
        st.session_state.details = parsed
    else:
        st.error("Please mention source and destination")

# ==================================================
# TRIP SUMMARY + CENTER BUTTON
# ==================================================
if st.session_state.details:
    d = st.session_state.details
    st.markdown("<div class='section-title'>Trip Summary</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.write(f"📍 Source: {d['source']}")
        st.write(f"📅 Days: {d['days']}")
    with c2:
        st.write(f"🎯 Destination: {d['destination']}")
        st.write(f"💰 Budget: ₹{d['budget']}")

    col1, col2, col3 = st.columns([3,2,3])
    with col2:
        if st.button("Generate Itinerary"):
            st.session_state.generate_clicked = True

# ==================================================
# GENERATE ITINERARY + IMAGES
# ==================================================
if st.session_state.generate_clicked and not st.session_state.itinerary:
    d = st.session_state.details
    with st.spinner("Creating itinerary..."):
        st.session_state.itinerary = deepseek_generate(
            f"Create a {d['days']}-day itinerary from {d['source']} to {d['destination']} under {d['budget']} INR"
        )
        st.session_state.images = get_images(d["destination"])

# ==================================================
# SHOW IMAGES
# ==================================================
if st.session_state.images:
    st.markdown("<div class='section-title'>Destination Preview</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, img in enumerate(st.session_state.images):
        cols[i % 3].image(img, use_container_width=True)

# ==================================================
# SHOW ITINERARY + AUDIO + RESET
# ==================================================
if st.session_state.itinerary:
    st.markdown("<div class='section-title'>Your Personalized Itinerary</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='card'>{st.session_state.itinerary}</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3,2,3])
    with col2:
        if st.button("🔊 Listen Itinerary"):
            if st.session_state.audio_bytes is None:
                st.session_state.audio_bytes = speak(st.session_state.itinerary)

    if st.session_state.audio_bytes:
        st.audio(st.session_state.audio_bytes, format="audio/mp3")

    col1, col2, col3 = st.columns([3,2,3])
    with col2:
        if st.button(" Reset"):
            for k in defaults:
                st.session_state[k] = defaults[k]
            st.rerun()
