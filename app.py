import streamlit as st
import requests
import Speech_To_Text as STT

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Voice Travel Concierge",
    layout="centered"
)

# ==================================================
# LIGHT UI
# ==================================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f9fbff 0%, #eef4ff 100%);
    color: #0f172a;
}

.app-title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    margin-top: 40px;
}

.app-subtitle {
    text-align: center;
    font-size: 16px;
    color: #475569;
    margin-bottom: 40px;
}

.center-btn {
    display: flex;
    justify-content: center;
    margin-bottom: 40px;
}

.center-btn button {
    width: 420px;
    height: 72px;
    font-size: 22px;
    font-weight: 700;
    border-radius: 18px;
    background: #2563eb;
    color: white;
}

.section-title {
    font-size: 22px;
    font-weight: 600;
    margin-top: 30px;
    margin-bottom: 12px;
}

.card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #dbeafe;
    box-shadow: 0 10px 24px rgba(0,0,0,0.06);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# SESSION STATE
# ==================================================
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "details" not in st.session_state:
    st.session_state.details = {}
if "itinerary" not in st.session_state:
    st.session_state.itinerary = ""
if "images" not in st.session_state:
    st.session_state.images = []

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
# SPEAK BUTTON
# ==================================================
st.markdown("<div class='center-btn'>", unsafe_allow_html=True)
clicked = st.button("🎙 Speak Travel Request")
st.markdown("</div>", unsafe_allow_html=True)

if clicked:
    with st.spinner("Listening..."):
        spoken = STT.get_text()

    if spoken:
        st.session_state.user_input = spoken
        st.session_state.details = {}
        st.session_state.itinerary = ""
        st.session_state.images = []
    else:
        st.error("Could not understand your voice.")

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
            {"role": "system", "content": "You are a precise travel assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 700
    }
    r = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# ==================================================
# IMAGE FETCH
# ==================================================
def get_destination_images(place, count=6):
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_KEY}"}
    params = {"query": place, "per_page": count, "orientation": "landscape"}
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return [img["urls"]["regular"] for img in r.json()["results"]]

# ==================================================
# PARSE DETAILS
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
# SHOW REQUEST
# ==================================================
if st.session_state.user_input:
    st.markdown("<div class='section-title'>Your Request</div>", unsafe_allow_html=True)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write(st.session_state.user_input)
    st.markdown("</div>", unsafe_allow_html=True)

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
        st.error("Please mention at least source and destination.")

# ==================================================
# TRIP SUMMARY
# ==================================================
if st.session_state.details:
    d = st.session_state.details
    st.markdown("<div class='section-title'>Trip Summary</div>", unsafe_allow_html=True)
    st.write(f"📍 Source: {d['source']}")
    st.write(f"🎯 Destination: {d['destination']}")
    st.write(f"📅 Days: {d['days']}")
    st.write(f"💰 Budget: ₹{d['budget']}")

    if st.button("Generate Itinerary"):
        with st.spinner("Creating itinerary..."):
            st.session_state.itinerary = deepseek_generate(
                f"""
Create a {d['days']}-day travel itinerary.

Rules:
- Use normal headings like "Day 1:"
- Do not use markdown symbols like ### or **
- Use simple bullet points

From: {d['source']}
To: {d['destination']}
Budget: {d['budget']} INR
"""
            )
            st.session_state.images = get_destination_images(d["destination"])

# ==================================================
# SHOW ITINERARY (FIXED MARKDOWN)
# ==================================================
if st.session_state.itinerary:
    st.markdown("<div class='section-title'>Your Personalized Itinerary</div>", unsafe_allow_html=True)

    # ✅ Correct rendering (NO ### visible)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(st.session_state.itinerary)
    st.markdown("</div>", unsafe_allow_html=True)

# ==================================================
# SHOW IMAGES
# ==================================================
if st.session_state.images:
    st.markdown("<div class='section-title'>Places You’ll Visit</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, img in enumerate(st.session_state.images):
        with cols[i % 3]:
            st.image(img, use_container_width=True)
