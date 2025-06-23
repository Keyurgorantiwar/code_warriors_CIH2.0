# app.py – Streamlit Real Estate Advisor

"""
🏠 Real Estate Advisor: Your Personal AI-Powered Property Guide

This app helps users understand whether it's better to buy, build, or invest
in real estate based on income, timeframe, and current market rates. It uses
Gemini (Google Generative AI) to give insights and strategies.

▶ Run:
    streamlit run app.py

🔑 Environment variable required:
    GEMINI_API_KEY – Your Gemini Pro API key (https://ai.google.dev/)

📦 Requirements (add to requirements.txt):
    streamlit
    google-generativeai>=0.4.0
    pandas
    requests
"""

import os
import textwrap

import pandas as pd
import requests
import streamlit as st

try:
    import google.generativeai as genai
except ImportError:
    st.error("Gemini API library not found. Please install 'google-generativeai' in your environment.")
    raise

# ─────────────────────────────────────────────────────────────────────────────
# Gemini Setup
# ─────────────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("🔐 GEMINI_API_KEY not set. Please set it in your environment or Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)
MODEL = genai.GenerativeModel("gemini-pro")


def ask_gemini(prompt: str, temperature: float = 0.3) -> str:
    """Sends prompt to Gemini API and returns the response text."""
    try:
        response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
        return response.text
    except Exception as err:
        return f"⚠️ Gemini returned an error: {err}"


# ─────────────────────────────────────────────────────────────────────────────
# Sample Market Data (Replace with real data in production)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_price_data(city: str) -> pd.DataFrame:
    """Returns mock real estate data. Replace this with a real API later."""
    try:
        url = f"https://example.com/realestate/prices?city={city}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception:
        # Temporary fallback data (example for demo/testing)
        data = {
            "Area (sqft)": [800, 1200, 1600],
            "Construction Cost (₹/sqft)": [1800, 2000, 2200],
            "Land Price (₹/sqft)": [5000, 5500, 6000],
        }
        return pd.DataFrame(data)


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit Interface
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="Real Estate Advisor", page_icon="🏠", layout="wide")

    st.title("🏠 Real Estate Advisor")
    st.write("Your personal AI consultant for making smart real estate decisions in India.")

    # Sidebar Inputs
    with st.sidebar:
        st.header("🔍 Your Profile")
        name = st.text_input("Name")
        income = st.number_input("Annual Household Income (₹)", min_value=0, step=50000)
        timeframe = st.slider("How many years from now do you want to buy/build?", 1, 30, 5)
        city = st.text_input("Preferred City", value="Nagpur")
        st.markdown("---")
        st.caption("📢 Disclaimer: The suggestions given are AI-generated. Always consult a professional before taking financial decisions.")

    # Market Info
    st.subheader(f"📈 Real Estate Market Snapshot – {city.title()}")
    df_prices = get_price_data(city)
    st.dataframe(df_prices, use_container_width=True)

    # Advisory Section
    st.subheader("🤖 AI-Powered Guidance")
    if st.button("🧠 Get My Real Estate Plan"):
        prompt = textwrap.dedent(
            f"""
            I'm planning to invest in property in {city}. My annual income is ₹{income} and 
            I want to achieve this goal in the next {timeframe} years.

            Here's the market data:
            {df_prices.to_markdown(index=False)}

            ➤ Compare construction costs and land prices.
            ➤ Suggest whether I should buy a flat, buy land and build, or wait.
            ➤ Give me a personalised plan based on my income and timeframe.
            ➤ Include basic cost estimates, financing options, and a friendly action plan.
            """
        )
        with st.spinner("Analyzing your situation with Gemini..."):
            response = ask_gemini(prompt)
        st.markdown(response)


if _name_ == "_main_":
    main()