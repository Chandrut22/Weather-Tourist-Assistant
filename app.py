import streamlit as st
import google.generativeai as genai
import requests
from decouple import Config

config = Config("config.toml")

OPENWEATHER_API_KEY = config("OPENWEATHER_API_KEY")
GEMINI_API_KEY = config("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

st.set_page_config(page_title="☁️ Weather & Tourist Assistant", page_icon="🌦️")
st.title("🌤️ Weather & Tourist Assistant")

def extract_location(text):
    
    prompt = f"""
    You are a helpful assistant. Extract the location name from the following text:
    "{text}"
    Only return the location name without any additional text.
    """
    response = model.generate_content(prompt)
    location = response.text.strip()
    return location

def get_weather(location):
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
    res = requests.get(url)
    return res.json() if res.status_code == 200 else None

def get_tourist_attractions(location):
    
    prompt = f"""
    You are a helpful assistant. Provide a list of top tourist attractions in {location}.
    Include brief descriptions for each attraction.
    """
    response = model.generate_content(prompt)
    attractions = response.text.strip()
    return attractions

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask me about today's weather or tourist attractions...")

if user_input:
    # print(f"User input: {user_input}")
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            location = extract_location(user_input)
            weather_data = get_weather(location)
            attractions = get_tourist_attractions(location)

            if weather_data:
                weather_prompt = f"""
                You are a smart weather assistant.
                The user asked: "{user_input}"
                Real-time weather in {location} is:
                {weather_data}
                
                Respond conversationally, summarizing the weather in a friendly way.
                """
                weather_response = model.generate_content(weather_prompt).text
            else:
                weather_response = "I couldn't find weather data for this location. Please try another location."

            if attractions:
                attractions_response = f"Here are some top tourist attractions in {location}:\n\n{attractions}"
            else:
                attractions_response = "I couldn't find tourist attractions for this location. Please try another location."

            # Combine the responses
            combined_response = f"{weather_response}\n\n{attractions_response}"

            # Refine the response using the LLM
            refinement_prompt = f"""
            You are a helpful assistant. Refine the following response to make it more conversational and user-friendly:
            "{combined_response}"
            """
            final_response = model.generate_content(refinement_prompt).text

            # Display the final response
            st.markdown(final_response)
            # print(f"Final response: {final_response}")

    st.session_state.messages.append({"role": "assistant", "content": final_response})
