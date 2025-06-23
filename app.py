# app.py – Streamlit Real Estate Advisor (INSECURE - Hard-coded API Key, with Professional Validation)

"""
🏠 Real Estate Advisor: Your Personal AI-Powered Property Guide

This version adds professional validation for Date of Birth (age check) and
Phone Number, and makes profile management a core feature.

▶ Run:
    streamlit run app.py

🔑 API Key:
    The API key is HARD-CODED in this file. This is NOT secure.
    Do NOT share this file publicly.

📦 Requirements (add to requirements.txt):
    streamlit
    google-generativeai>=0.4.0
    pandas
    requests
"""

import textwrap
import pandas as pd
import requests
import streamlit as st
from datetime import date

# --- SECURITY WARNING ---
# You are using a hard-coded API key. This is a significant security risk.
# Revoke any public keys and use a secure method like Streamlit Secrets.

try:
    import google.generativeai as genai
except ImportError:
    st.error("Gemini API library not found. Please install 'google-generativeai' in your environment.")
    raise

# ─────────────────────────────────────────────────────────────────────────────
# Gemini Setup (Insecure - Hard-coded Key)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def configure_gemini():
    """
    Configures the Gemini API with a hard-coded key.
    WARNING: This is not a secure practice.
    """
    try:
        # --- ▼▼▼ REMINDER: Replace this key with a new, secret key ▼▼▼ ---
        genai.configure(api_key="YOUR_NEW_SECRET_API_KEY_HERE")
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        return model
    except Exception as e:
        st.error("Failed to configure Gemini. Please check that your API key is correct and valid.")
        st.error(f"Error details: {e}")
        st.stop()

MODEL = configure_gemini()


def ask_gemini(prompt: str, temperature: float = 0.4) -> str:
    """Sends a prompt to the Gemini API and returns the response text."""
    try:
        response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
        if not response.parts:
            return "⚠️ The AI returned an empty response. This may be due to the safety settings of the API. Please try a different query."
        return response.text
    except Exception as err:
        st.error(f"An error occurred while communicating with Gemini: {err}")
        return "⚠️ An error occurred. Please check the logs or your API key."

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching market data...")
def get_price_data(city: str) -> pd.DataFrame:
    """Returns mock real estate data."""
    seed = len(city)
    base_construction = 1800 + (seed % 5) * 100
    base_land = 5000 + (seed % 8) * 150
    data = {"Area (sqft)": [800, 1200, 1500, 1800, 2200], "Construction Cost (₹/sqft)": [base_construction, base_construction + 150, base_construction + 250, base_construction + 350, base_construction + 450], "Land Price (₹/sqft)": [base_land, base_land + 400, base_land + 700, base_land + 900, base_land + 1200]}
    return pd.DataFrame(data).set_index("Area (sqft)")

def calculate_age(born: date) -> int:
    """Calculates age based on a birth date."""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# ─────────────────────────────────────────────────────────────────────────────
# Streamlit Interface
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Real Estate Advisor", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

    if 'profiles' not in st.session_state:
        st.session_state.profiles = {}

    with st.sidebar:
        st.image("https://i.imgur.com/rLdD2b5.png", width=150)
        st.title("User Profile")
        
        # --- Profile Input Fields ---
        name = st.text_input("👤 Name", placeholder="e.g., Priya", key="user_name_input")
        dob = st.date_input("🎂 Date of Birth", value=date(2000, 1, 1), max_value=date.today(), key="user_dob_input")
        phone = st.text_input("📞 Phone Number", placeholder="10-digit number", max_chars=10, key="user_phone_input")
        income = st.number_input("💰 Annual Household Income (₹)", min_value=100000, value=1200000, step=100000, format="%d", key="user_income_input")
        timeframe = st.slider("🗓️ Timeframe to Buy/Build (Years)", 1, 30, 5, key="user_timeframe_slider")
        city = st.text_input("🏙️ Preferred City", value="Nagpur", key="user_city_input")
        
        st.markdown("---")
        
        # --- Profile Management ---
        st.subheader("📁 Profile Management")
        st.info("You must save a profile before generating a plan.")
        profile_name = st.text_input("Profile Name to Save/Load", key="profile_name")
        col_save, col_load, col_del = st.columns(3)

        with col_save:
            if st.button("Save", use_container_width=True, key="save_button"):
                if profile_name:
                    st.session_state.profiles[profile_name] = {"name": name, "dob": dob, "phone": phone, "income": income, "timeframe": timeframe, "city": city}
                    st.success(f"Profile '{profile_name}' saved!")
                else:
                    st.warning("Please enter a profile name to save.")

        if st.session_state.profiles:
            profile_keys = ["---"] + list(st.session_state.profiles.keys())
            selected_key = st.selectbox("Select Profile", options=profile_keys, key="profile_select")
            with col_load:
                if st.button("Load", use_container_width=True, key="load_button"):
                    if selected_key != "---":
                        p = st.session_state.profiles[selected_key]
                        st.session_state.update(user_name_input=p["name"], user_dob_input=p["dob"], user_phone_input=p["phone"], user_income_input=p["income"], user_timeframe_slider=p["timeframe"], user_city_input=p["city"])
                        st.success(f"Profile '{selected_key}' loaded!")
                        st.rerun()
            with col_del:
                if st.button("Delete", use_container_width=True, key="delete_button"):
                    if selected_key != "---":
                        del st.session_state.profiles[selected_key]
                        st.success(f"Profile '{selected_key}' deleted.")
                        st.rerun()

        st.markdown("---")
        st.caption("📢 AI-generated suggestions are informational only. Consult a professional.")

    st.title("🏠 AI Real Estate Advisor")
    st.markdown(f"Welcome, **{name.title() if name else 'User'}**! Let's build your property plan.")

    col1, col2 = st.columns((2, 1.5), gap="large")

    with col2:
        st.subheader("🎯 Your Financial Profile")
        with st.container(border=True, height=380):
            st.markdown("##### Key Information")
            st.write(f"**Name:** {name}")
            st.write(f"**Date of Birth:** {dob.strftime('%d-%b-%Y')}")
            st.write(f"**Phone:** {phone}")
            st.write(f"**Income:** ₹ {income:,.0f} per year")
            st.write(f"**Timeframe:** {timeframe} years")
            st.write(f"**Target City:** {city.title() if city else 'Not specified'}")
            st.markdown("---")
            st.info("Your details are used for validation and creating a personalized plan.", icon="🤖")

    with col1:
        st.subheader("📊 Market Snapshot & AI Plan")
        if city:
            df_prices = get_price_data(city)
            st.toast(f"Using simulated data for {city.title()}.", icon="📉")

            with st.container(border=True):
                st.markdown(f"#### Average Costs in **{city.title()}**")
                avg_land = df_prices["Land Price (₹/sqft)"].mean()
                avg_build = df_prices["Construction Cost (₹/sqft)"].mean()
                c1, c2 = st.columns(2)
                c1.metric("Avg. Land Price", f"₹ {avg_land:,.0f} / sqft")
                c2.metric("Avg. Construction Cost", f"₹ {avg_build:,.0f} / sqft")
                st.bar_chart(df_prices)
            
            st.markdown("---")
            st.subheader("🤖 Your Personalized AI-Powered Plan")
            
            if st.button("🧠 Generate My Real Estate Strategy", type="primary", use_container_width=True, key="generate_button"):
                # --- Validation Sequence ---
                is_valid = True
                
                # 1. Check if all fields are filled
                if not all([name, dob, phone, income, timeframe, city]):
                    st.error("Please fill in all the fields in the sidebar.")
                    is_valid = False

                # 2. Check if the profile is saved
                if is_valid and name not in [p['name'] for p in st.session_state.profiles.values()]:
                    st.error(f"Profile for '{name}' not found. Please save the profile first.")
                    is_valid = False

                # 3. Validate Phone Number
                if is_valid and not (phone.isdigit() and len(phone) == 10):
                    st.error("Invalid phone number. It must be exactly 10 digits.")
                    is_valid = False
                
                # 4. Validate Age
                if is_valid:
                    age = calculate_age(dob)
                    if age < 18:
                        st.error(f"You must be at least 18 years old to proceed. Your current age is {age}.")
                        is_valid = False

                # --- Proceed if all checks passed ---
                if is_valid:
                    prompt = textwrap.dedent(f"""
                        **Act as a friendly, expert real estate advisor in India.** My name is {name}. My goal is to own property in **{city}**.
                        My Profile: Annual Household Income: ₹{income:,.0f}, Timeframe: {timeframe} years.
                        Market Data for {city}:\n{df_prices.to_markdown()}
                        **Task:** Generate a detailed report in Markdown with emojis.
                        1. ### 🎯 Executive Summary: Should {name} buy, build, or wait? Justify.
                        2. ### ⚖️ Buy vs. Build Analysis: Cost comparison for a 1200 sqft property and pros/cons.
                        3. ### 💡 Personalized Strategy for {name}: Clear strategy (buy/build/wait) with budget/type.
                        4. ### 💰 Financial Breakdown: Down payment goal, loan eligibility, and estimated EMI.
                        5. ### 🚀 Action Plan: A checklist of the next 3-5 steps for {name}.
                    """)
                    with st.spinner("🧠 Gemini is analyzing your profile and crafting your plan..."):
                        response = ask_gemini(prompt)
                    st.markdown(response)
        else:
            st.warning("Please enter a city name to see market data and get your plan.")

if __name__ == "__main__":
    main()