# app.py – Streamlit Real Estate Advisor (Enhanced Version)

"""
🏠 Real Estate Advisor: Your Personal AI-Powered Property Guide

This app helps users understand whether it's better to buy, build, or invest
in real estate based on income, timeframe, and current market rates. It uses
Gemini (Google Generative AI) to give insights and strategies.

This enhanced version features a more graphical and user-friendly interface.

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
def configure_gemini():
    """Configure the Gemini API, handle errors, and return the model."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        st.error("🔐 GEMINI_API_KEY not set. Please set it in your environment or Streamlit secrets.")
        st.info("You can get a free key from https://ai.google.dev/")
        st.stop()
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-pro")
        return model
    except Exception as e:
        st.error(f"Failed to configure Gemini: {e}")
        st.stop()

MODEL = configure_gemini()


def ask_gemini(prompt: str, temperature: float = 0.4) -> str:
    """Sends a prompt to the Gemini API and returns the response text."""
    if not prompt:
        return "Please provide your details to get a plan."
    try:
        response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
        # Clean up potential blocking issues if the response is empty
        if not response.parts:
            return "⚠️ The AI returned an empty response. This may be due to the safety settings of the API. Please try a different query."
        return response.text
    except Exception as err:
        st.error(f"An error occurred while communicating with Gemini: {err}")
        return "⚠️ An error occurred. Please check the logs or your API key."


# ─────────────────────────────────────────────────────────────────────────────
# Market Data Simulation (More dynamic than the original)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching market data...")
def get_price_data(city: str) -> pd.DataFrame:
    """
    Returns mock real estate data. 
    In a real app, this would hit a live API endpoint.
    This version creates semi-random data based on the city name for a more dynamic demo.
    """
    try:
        # This is where a real API call would go.
        # url = f"https://api.realestateindia.com/prices?city={city}"
        # response = requests.get(url, timeout=10)
        # response.raise_for_status()
        # return pd.DataFrame(response.json())
        raise ConnectionError("Using mock data for demonstration.")
    except Exception:
        # Fallback to dynamic mock data
        st.toast(f"Using simulated data for {city.title()}.", icon="📉")
        
        # Use city name length to create a reproducible "random" seed
        seed = len(city)
        base_construction = 1800 + (seed % 5) * 100  # e.g., 1800, 1900,... 2200
        base_land = 5000 + (seed % 8) * 150        # e.g., 5000, 5150,...

        data = {
            "Area (sqft)": [800, 1200, 1500, 1800, 2200],
            "Construction Cost (₹/sqft)": [
                base_construction,
                base_construction + 150,
                base_construction + 250,
                base_construction + 350,
                base_construction + 450,
            ],
            "Land Price (₹/sqft)": [
                base_land,
                base_land + 400,
                base_land + 700,
                base_land + 900,
                base_land + 1200,
            ],
        }
        return pd.DataFrame(data).set_index("Area (sqft)")


# ─────────────────────────────────────────────────────────────────────────────
# Streamlit Interface
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Real Estate Advisor", 
        page_icon="🏠", 
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- Sidebar for User Inputs ---
    with st.sidebar:
        st.image("https://i.imgur.com/rLdD2b5.png", width=150) # A simple logo
        st.title("Your Profile")
        st.markdown("Tell us about your real estate goals.")
        
        name = st.text_input("👤 Name", placeholder="e.g., Priya")
        income = st.number_input("💰 Annual Household Income (₹)", min_value=100000, value=1200000, step=100000, format="%d")
        timeframe = st.slider("🗓️ Timeframe to Buy/Build (Years)", 1, 30, 5)
        city = st.text_input("🏙️ Preferred City", value="Nagpur")
        
        st.markdown("---")
        st.markdown("This app uses **Google's Gemini AI**.")
        st.caption("📢 Disclaimer: AI-generated suggestions are for informational purposes only. Always consult with a qualified financial advisor and real estate professional.")

    # --- Main Page ---
    st.title("🏠 AI Real Estate Advisor")
    st.markdown(f"Welcome, **{name.title() if name else 'User'}**! Let's build your property plan.")

    col1, col2 = st.columns((2, 1.5), gap="large")

    with col1:
        st.subheader("📊 Market Snapshot")
        if city:
            df_prices = get_price_data(city)
            
            with st.container(border=True):
                st.markdown(f"#### Average Costs in **{city.title()}**")
                # Display metrics for quick insights
                avg_land_cost = df_prices["Land Price (₹/sqft)"].mean()
                avg_build_cost = df_prices["Construction Cost (₹/sqft)"].mean()

                metric_col1, metric_col2 = st.columns(2)
                metric_col1.metric(
                    label="Avg. Land Price", 
                    value=f"₹ {avg_land_cost:,.0f} / sqft",
                    help="Average price of land per square foot in the sampled areas."
                )
                metric_col2.metric(
                    label="Avg. Construction Cost",
                    value=f"₹ {avg_build_cost:,.0f} / sqft",
                    help="Average cost to build a structure per square foot."
                )
                
                # Display chart for visual comparison
                st.bar_chart(df_prices)
        else:
            st.warning("Please enter a city name to see market data.")

    with col2:
        st.subheader("🎯 Your Financial Profile")
        with st.container(border=True, height=350):
            st.markdown("##### Key Information")
            st.write(f"**Income:** ₹ {income:,.0f} per year")
            st.write(f"**Timeframe:** {timeframe} years")
            st.write(f"**Target City:** {city.title() if city else 'Not specified'}")
            st.markdown("---")
            st.info("Your details will be used by the AI to create a personalized plan.", icon="🤖")


    st.markdown("---")

    # --- AI Advisory Section ---
    st.subheader("🤖 Your Personalized AI-Powered Plan")
    
    if st.button("🧠 Generate My Real Estate Strategy", type="primary", use_container_width=True):
        if not all([name, income, timeframe, city]):
            st.warning("Please fill in all the details in the sidebar to get your plan.")
            st.stop()
            
        prompt = textwrap.dedent(
            f"""
            **Act as a friendly, expert real estate advisor in India.** My name is {name}.
            My goal is to own property in **{city}**. Please generate a personalized real estate plan for me.
            Use a positive and encouraging tone. The output must be well-structured in Markdown.

            **My Profile:**
            - Annual Household Income: ₹{income:,.0f}
            - Timeframe for Purchase/Construction: {timeframe} years

            **Market Data for {city} (in Markdown Table Format):**
            {df_prices.to_markdown()}

            **Your Task:**
            Generate a detailed report covering the points below. Use the provided name for personalization. Format the entire response in clean Markdown with emojis.

            **1. Executive Summary (Use `### 🎯 Executive Summary`)**
               - Briefly summarize the recommendation: Is it better for {name} to buy a pre-built property (like a flat/apartment), buy land and build a house, or wait and invest for now? Justify the choice based on income, timeframe, and market data.

            **2. Buy vs. Build Analysis (Use `### ⚖️ Buy vs. Build Analysis`)**
               - **Cost:** Compare the total estimated cost of buying a 1200 sqft apartment vs. buying a 1500 sqft plot and building a 1200 sqft house. Use the market data to make rough estimates.
               - **Pros and Cons:** Create a small table comparing the pros and cons of buying vs. building for someone with my profile.
            
            **3. Personalized Strategy for {name} (Use `### 💡 Personalized Strategy for {name}`)**
               - Based on the summary, provide a clear, actionable strategy.
               - If "Buy": Suggest the type of property (e.g., 2BHK or 3BHK flat) and budget.
               - If "Build": Suggest a land area to target and a phased construction plan.
               - If "Wait": Suggest specific investment goals to reach before reconsidering.

            **4. Financial Breakdown (Use `### 💰 Financial Breakdown`)**
               - **Savings Goal:** How much down payment should I aim for?
               - **Loan Eligibility:** Estimate a potential home loan amount based on my income (assume a standard debt-to-income ratio).
               - **EMI Estimate:** Provide a rough monthly EMI (Equated Monthly Instalment) estimate for the suggested loan amount.

            **5. Next Steps (Use `### 🚀 Action Plan`)**
               - Provide a clear, step-by-step checklist of the next 3-5 actions {name} should take. For example: '1. Solidify budget', '2. Research micro-locations in {city}', '3. Consult a home loan provider.'
            """
        )

        with st.spinner("🧠 Gemini is analyzing your profile and crafting your plan... Please wait."):
            response = ask_gemini(prompt)
        
        st.markdown(response)

if __name__ == "__main__":
    main()