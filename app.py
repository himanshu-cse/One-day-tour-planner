import streamlit as st
import openai
from datetime import datetime
import requests

user_memory = {}

openai.api_key = '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'  # Replace with your actual API key

import time
from datetime import datetime, timedelta

cache = {}
last_api_call = datetime.now() - timedelta(minutes=1)  

def call_llm_api(prompt):
    global last_api_call
    if prompt in cache:
        return cache[prompt]
    
    if datetime.now() - last_api_call < timedelta(seconds=10):  # Wait 10 seconds between calls
        st.warning("Please wait a few seconds between requests to avoid rate limits.")
        time.sleep(10)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        last_api_call = datetime.now()
        cache[prompt] = response.choices[0].message['content'].strip()
        return cache[prompt]
    except openai.error.RateLimitError:
        st.error("Rate limit exceeded. Please wait and try again later.")
        return "Unable to process request due to rate limiting."



def generate_itinerary(city, start_time, end_time, interests, budget, starting_point):
    itinerary_prompt = (f"Plan a one-day tour in {city} starting from {starting_point}. "
                        f"The user is interested in {', '.join(interests)} with a budget of {budget}. "
                        f"Start time is {start_time} and end time is {end_time}.")
    return call_llm_api(itinerary_prompt)

st.title("One-Day Tour Planning Assistant")

if "city" not in user_memory:
    user_memory["city"] = st.text_input("Which city would you like to visit?")

if "date" not in user_memory:
    user_memory["date"] = st.date_input("Select the date of your trip")

if "start_time" not in user_memory:
    user_memory["start_time"] = st.time_input("Select start time")

if "end_time" not in user_memory:
    user_memory["end_time"] = st.time_input("Select end time")

if "interests" not in user_memory:
    user_memory["interests"] = st.multiselect(
        "Select your interests",
        ["Historical Sites", "Food", "Shopping", "Nature", "Adventure"]
    )

if "budget" not in user_memory:
    user_memory["budget"] = st.number_input("Enter your budget", min_value=0)

if "starting_point" not in user_memory:
    user_memory["starting_point"] = st.text_input("Enter your starting point")

if st.button("Generate Itinerary"):
    itinerary = generate_itinerary(
        user_memory["city"],
        user_memory["start_time"],
        user_memory["end_time"],
        user_memory["interests"],
        user_memory["budget"],
        user_memory["starting_point"]
    )
    st.write("### Your Itinerary")
    st.write(itinerary)

st.write("### Adjust Your Preferences")
adjustments = st.text_area("Enter any changes or additional preferences")
if st.button("Update Itinerary"):
    adjusted_prompt = f"{itinerary}. Update the itinerary based on: {adjustments}"
    updated_itinerary = call_llm_api(adjusted_prompt)
    st.write("### Updated Itinerary")
    st.write(updated_itinerary)

if st.button("Finalize Plan"):
    st.write("### Finalized Itinerary")
    st.write(itinerary)

if "date" in user_memory and "city" in user_memory:
    weather_api_key = 'YOUR_WEATHER_API_KEY'  
    city = user_memory["city"]
    weather_response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key={weather_api_key}&q={city}&days=1")
    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        forecast = weather_data['forecast']['forecastday'][0]['day']
        st.write("### Weather Forecast")
        st.write(f"Weather for {city} on {user_memory['date']}: {forecast['condition']['text']}, {forecast['avgtemp_c']}°C")
    else:
        st.write("Could not retrieve weather data.")

