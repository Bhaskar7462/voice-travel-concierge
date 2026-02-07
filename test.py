import streamlit as st
import requests
import Speech_To_Text as STT
import Text_To_Speech as TTS


# ---------------- CONFIG ----------------
API_KEY = st.secrets["OPENROUTER_API_KEY"]
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

st.set_page_config(page_title="Voice Travel Concierge",page_icon="🎙️", layout="centered")
st.title("🎙️ Voice Travel Concierge")
st.caption("Plan your trip using just your voice")

#-----------------------------------INTERNAL STATE--------------------
if "user_input" not in st.session_state:
    st.session_state.user_input = None

if "details" not in st.session_state:
    st.session_state.details = None

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None


# ---------------- LLM FUNCTION ----------------
def deepseek_generate(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek/deepseek-r1-0528",
        "messages": [
            {"role": "system", "content": "You are a helpful travel assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 300
    }

    try:
        r = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()  # ❗ yahin se exception throw hota hai
        return r.json()["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"LLM Error: {e}"


#----------------------------- PARSER-------------------------
# parse_details is for the deriving the useful or machine understandable data from first prompt
import re

def parse_details(text: str):
    data = {
        "source": None,
        "destination": None,
        "days": None,
        "budget": None
    }

    for line in text.splitlines():
        line = line.strip().lower()

        if "source" in line:
            data["source"] = line.split(":")[-1].strip()

        elif "destination" in line:
            data["destination"] = line.split(":")[-1].strip()

        elif "day" in line:
            match = re.search(r"\d+", line)
            if match:
                data["days"] = match.group()

        elif "budget" in line or "rs" in line or "₹" in line:
            match = re.search(r"\d+", line)
            if match:
                data["budget"] = match.group()

    return data



# ---------------- UI ----------------
st.divider()
st.header("🗣️ 1. Speak Your Travel Request")
st.markdown("Click the button and speak your travel request")


if st.button("🎤 Speak Travel Request", use_container_width=True):
    with st.spinner("Listening..."):
        st.session_state.user_input = STT.get_text()


    if not st.session_state.user_input:
        st.error("Could not understand audio. Try again.")
    else:
        st.success("Speech captured!")
        st.info(f"🗣️ You said: {st.session_state.user_input}")


# ---------------- PROCESS ----------------
if st.session_state.user_input:
    st.divider()
    st.header("🧳 2. Understanding Your Trip")
    prompt = f"""
Extract travel details.

Sentence: {st.session_state.user_input}

Return exactly in this format:
Source:
Destination:
Days:
Budget:
"""

    with st.spinner("Understanding your request..."):
        output = deepseek_generate(prompt)
    if output.startswith("LLM Error"):
        st.error(output)
    else:
        st.session_state.details = parse_details(output)



#-------------------- ITINERARY GENERATITION---------------
if st.session_state.details:
    st.divider()
    st.header("🗺️ 3. Your Personalized Itinerary")


    itinerary_prompt = f"""
    Create a budget-friendly travel itinerary.

    Source: {st.session_state.details.get("source")}
    Destination: {st.session_state.details.get("destination")}
    Days: {st.session_state.details.get("days")}
    Budget: {st.session_state.details.get("budget")}

    Rules:
    - Do NOT exceed the budget
    - Suggest low-cost transport and stays
    - Mention approximate costs per day
    - Make a realistic day-wise plan

    Output format:
    Day 1:
    Day 2:
    """
    with st.spinner("Creating your itinerary..."):
        st.session_state.itinerary = deepseek_generate(itinerary_prompt)

    if st.session_state.itinerary.startswith("LLM Error"):
        st.error(st.session_state.itinerary)
    else:
        st.markdown(st.session_state.itinerary)



#-----------------------TEXT TO SPEECH-----------------
if st.session_state.itinerary:
    st.divider()
    if st.button("🔊 Listen to Itinerary", use_container_width=True):
        TTS.speak(st.session_state.itinerary)

st.divider()
st.caption("🚀 Voice Travel Concierge • Built with Streamlit, Speech Recognition & LLMs")

