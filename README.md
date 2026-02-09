# 🎙️ Voice Travel Concierge

Voice Travel Concierge is an **AI-powered travel planning web application** that allows users to generate personalized, budget-friendly travel itineraries using **just their voice**.

The app converts spoken input into text, intelligently processes it using an LLM, and generates a complete day-wise itinerary along with **real destination images**.

---

## 🚀 Features

- 🎤 Voice-based travel input (no typing required)
- 🧠 AI-powered itinerary generation
- 🗓️ Automatic extraction of source, destination, days & budget
- 💰 Budget-aware travel planning
- 🌄 Destination images using Unsplash API
- 🖥️ Clean and user-friendly UI built with Streamlit
- 🔒 Secure API key handling using Streamlit secrets

---

## 🛠️ Tech Stack

- **Language:** Python  
- **Frontend:** Streamlit  
- **Speech to Text:** SpeechRecognition  
- **AI / LLM:** DeepSeek via OpenRouter API  
- **Text to Speech:** gTTS  
- **Images:** Unsplash API  

---

## 📂 Project Structure                                                           Voice-Travel-Concierge/
│
├── app.py # Main Streamlit app
├── Speech_To_Text.py # Speech → Text module
├── Text_To_Speech.py # Text → Speech module
├── README.md # Project documentation
└── .streamlit/                                                                                                        ▶️ How to Run the Project
Clone the repository:

git clone https://github.com/Bhaskar7642/voice-travel-concierge.git
Navigate to the project folder:

cd voice-travel-concierge
Install dependencies:

pip install streamlit requests speechrecognition gtts
Run the app:

streamlit run app.py
🧪 Example Usage
Click “Speak Travel Request”

Say something like:

“Plan a 4-day trip from Delhi to Hyderabad with a budget of 5000”

The app will:

Understand your request

Generate a travel itinerary

Display destination images


└── secrets.toml # API keys (not committed)


🔮 Future Enhancements
Day-wise expandable itinerary cards

Map and route visualization

Mobile-friendly UI

Dark mode toggle

PDF export of itinerary

👤 Author
Bhaskar
AI & Software Development Enthusiast