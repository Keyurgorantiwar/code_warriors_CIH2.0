# app.py – Streamlit Real Estate Advisor (INSECURE - Hard-coded API Key, with Multi-Step UI)

"""
Real Estate Advisor: Your Personal AI-Powered Property Guide

This version features a multi-step user interface.
Step 1: User selects their primary goal.
Step 2: A dynamic form appears with questions relevant only to that goal.
Step 3: The AI analysis is unlocked using the gathered information.

Run:
    streamlit run app.py

API Key:
    The API key is HARD-CODED in this file. This is NOT secure.
    Do NOT share this file publicly.

Requirements (add to requirements.txt):
    streamlit
    google-generativeai>=0.4.0
    pandas
"""

import textwrap
import pandas as pd
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
    """Configures the Gemini API with a hard-coded key."""
    try:
        # --- REMINDER: Replace this key with a new, secret key ---
        genai.configure(api_key="YOUR_NEW_SECRET_API_KEY_HERE")
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model
    except Exception as e:
        st.error(f"Failed to configure Gemini. Please check that your API key is correct and valid. Error: {e}")
        st.stop()

MODEL = configure_gemini()

def ask_gemini(prompt: str, temperature: float = 0.4) -> str:
    """Sends a prompt to the Gemini API and returns the response text."""
    try:
        response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
        if not response.parts:
            return "Warning: The AI returned an empty response. This may be due to API safety settings."
        return response.text
    except Exception as err:
        st.error(f"An error occurred while communicating with Gemini: {err}")
        return "Warning: An error occurred. Please check the logs or your API key."

# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Fetching market data...")
def get_price_data(city: str) -> pd.DataFrame:
    """Returns mock real estate data."""
    seed = len(city)
    base_construction = 1800 + (seed % 5) * 100
    base_land = 5000 + (seed % 8) * 150
    data = {"Area (sqft)": [800, 1200, 1500, 1800, 2200], "Construction Cost (Rs/sqft)": [base_construction, base_construction + 150, base_construction + 250, base_construction + 350, base_construction + 450], "Land Price (Rs/sqft)": [base_land, base_land + 400, base_land + 700, base_land + 900, base_land + 1200]}
    return pd.DataFrame(data).set_index("Area (sqft)")

def calculate_age(born: date) -> int:
    """Calculates age based on a birth date."""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

# ─────────────────────────────────────────────────────────────────────────────
# UI Modules for Rendering Specific Form Sections
# ─────────────────────────────────────────────────────────────────────────────

def render_flat_specifics():
    st.markdown("##### Flat Details")
    details = {"plan_flat_size": st.selectbox("Flat Size", ['1BHK', '2BHK', '3BHK', '4BHK+', 'Penthouse', 'Studio', 'Custom'])}
    return details

def render_plot_specifics():
    st.markdown("##### Plot Details")
    details = {"plan_plot_area": st.number_input("Plot Area (sq. ft)", min_value=300, value=1200, step=100)}
    return details

def render_build_specifics():
    st.markdown("##### Construction Details")
    details = {
        "plan_built_up": st.number_input("Target Built-up Area (sq. ft)", min_value=200, value=1800, step=100),
        "plan_floors": st.number_input("Number of Floors Planned", min_value=1, value=2),
        "extra_floors_rent": st.checkbox("Plan extra floors for rent?"),
        "const_contract": st.selectbox("Contract Type", ['With Material (Turnkey)', 'Without Material (Labor Only)']),
        "const_vendors": st.multiselect("Specific Vendors Needed?", ['Plumbing', 'Electrical', 'Tiles', 'Paint', 'Solar', 'Interiors', 'CCTV', 'Automation', 'Landscaping']),
        "const_green": st.multiselect("Desired Green Features", ['Solar Panels', 'Rainwater Harvesting', 'Heat Insulation', 'EV Charging Point', 'Greywater Recycling']),
        "const_timeline": st.slider("Estimated Build Timeline (Months)", 3, 36, 12)
    }
    return details

def render_investment_specifics(purpose):
    details = {}
    if "Rental" in purpose:
        details["fin_target_rent"] = st.number_input("Target Monthly Rent Income (Rs)", min_value=0, step=1000)
    if "Resale" in purpose:
        details["fin_target_resale"] = st.number_input("Target Resale Price (Rs)", min_value=0, step=100000)
    if details:
        st.markdown("##### Investment Goals")
        # This part dynamically creates the widgets outside the main form's "with" block
        # It's a way to handle conditional inputs based on other inputs within the same form
        for key, val in details.items():
            st.session_state[key] = val
    return details


# ─────────────────────────────────────────────────────────────────────────────
# Main UI Display Functions
# ─────────────────────────────────────────────────────────────────────────────

def display_sidebar():
    """Manages the sidebar for profile creation and loading."""
    with st.sidebar:
        st.title("Profile Manager")
        st.markdown("Create or load a profile to begin.")
        
        with st.expander("Create New Profile", expanded=not st.session_state.profiles):
            with st.form("new_profile_form"):
                st.subheader("User Details")
                profile_name = st.text_input("Profile Name (e.g., 'My Nagpur Plan')")
                name = st.text_input("Full Name")
                contact = st.text_input("Email or Phone")
                dob = st.date_input("Date of Birth", min_value=date(1940, 1, 1), max_value=date.today(), value=date(2000, 1, 1))
                income = st.number_input("Annual Household Income (Rs)", min_value=100000, step=100000, value=1200000, format="%d")
                
                if st.form_submit_button("Save Profile", use_container_width=True):
                    if all([profile_name, name, contact, dob, income]):
                        if profile_name in st.session_state.profiles:
                            st.error(f"Profile '{profile_name}' already exists.")
                        else:
                            st.session_state.profiles[profile_name] = {"name": name, "contact": contact, "dob": dob, "income": income}
                            st.session_state.selected_profile = profile_name
                            st.session_state.step = 1  # Reset to step 1
                            st.success(f"Profile '{profile_name}' created!")
                            st.rerun()
                    else:
                        st.error("Please fill all fields in the profile.")
        st.markdown("---")
        if st.session_state.profiles:
            st.subheader("Load Profile")
            profile_options = list(st.session_state.profiles.keys())
            
            def on_profile_change():
                st.session_state.selected_profile = st.session_state.profile_select_key
                st.session_state.step = 1  # Reset to step 1
                st.session_state.property_details = {}

            try:
                current_index = profile_options.index(st.session_state.selected_profile)
            except (ValueError, TypeError):
                current_index = 0
                if profile_options: st.session_state.selected_profile = profile_options[0]
            
            st.selectbox("Select Profile", options=profile_options, index=current_index, key="profile_select_key", on_change=on_profile_change)

def display_step1_intent_form():
    """Shows the first step: selecting the primary real estate goal."""
    st.subheader("STEP 1: What is your primary goal?")
    with st.form("step1_form"):
        intent_type = st.selectbox("Select your goal", ['Buy a Flat', 'Build a House', 'Buy a Plot', 'Mixed / Rent Invest'])
        submitted = st.form_submit_button("Next: Add Details")
        if submitted:
            st.session_state.intent_type = intent_type
            st.session_state.step = 2
            st.rerun()

def display_step2_details_form():
    """Shows the second step: a dynamic form for detailed requirements."""
    intent_type = st.session_state.intent_type
    st.subheader(f"STEP 2: Details for '{intent_type}'")
    
    with st.form("step2_form"):
        details = {"intent_type": intent_type}
        
        st.markdown("#### Location & Budget")
        c1, c2 = st.columns(2)
        with c1:
            details["loc_city"] = st.text_input("Target City", value="Nagpur")
            details["loc_locality"] = st.text_input("Preferred Localities (comma-separated)")
            details["loc_pincode"] = st.text_input("Pin Code", max_chars=6)
        with c2:
            details["fin_budget"] = st.number_input("Total Budget (Rs)", min_value=100000, step=100000, value=5000000)
            details["fin_loan"] = st.checkbox("Will you need a loan?", value=True)
            details["fin_subsidy"] = st.checkbox("Interested in subsidy schemes (e.g., PMAY)?")

        st.markdown("---")
        
        details["intent_purpose"] = st.selectbox("What is the main purpose?", ['Self Use', 'Rental Income', 'Resale / Investment'])
        
        mixed_components = []
        if intent_type == 'Mixed / Rent Invest':
            st.markdown("#### Mixed Investment Components")
            mixed_components = st.multiselect("Select the components for your mixed strategy:", ['Buy a Flat', 'Build a House', 'Buy a Plot'])
            details["mixed_components"] = mixed_components

        if intent_type == 'Buy a Flat' or 'Buy a Flat' in mixed_components:
            details.update(render_flat_specifics())
        if intent_type in ['Build a House', 'Buy a Plot'] or any(c in mixed_components for c in ['Build a House', 'Buy a Plot']):
            details.update(render_plot_specifics())
        if intent_type == 'Build a House' or 'Build a House' in mixed_components:
            details.update(render_build_specifics())
            
        st.markdown("---")
        
        st.markdown("#### Preferences & Concerns")
        c3, c4 = st.columns(2)
        with c3:
            details["qual_connectivity"] = st.select_slider("Connectivity Importance", ['Low', 'Medium', 'High'], value='Medium')
            details["qual_amenities"] = st.select_slider("Proximity to Schools/Hospitals", ['Not Important', 'Somewhat', 'Very Important'], value='Somewhat')
        with c4:
            details["risk_pollution"] = st.select_slider("Pollution Concern Level", ['Low', 'Medium', 'High'])
            details["risk_crime"] = st.select_slider("Crime Concern Level", ['Low', 'Medium', 'High'])
        
        details.update(render_investment_specifics(details["intent_purpose"]))

        submitted = st.form_submit_button("Save Details & Proceed to Analysis", use_container_width=True)
        if submitted:
            st.session_state.property_details = details
            st.session_state.step = 3
            st.rerun()

def display_step3_analysis_section(user_profile, prop_details):
    """Shows the final step: saved details and the AI generation button."""
    st.subheader("STEP 3: Review and Generate AI Strategy")
    
    st.success("Your requirements have been saved. Review the details below and generate your plan.")
    
    with st.expander("Your Saved Requirements", expanded=True):
        st.write(prop_details)

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Generate My Real Estate Strategy", type="primary", use_container_width=True):
            prompt = build_ai_prompt(user_profile, prop_details)
            with st.spinner("Analyzing your detailed requirements and crafting a custom strategy..."):
                response = ask_gemini(prompt)
            st.session_state.ai_response = response
            st.rerun()
    with col2:
        if st.button("Edit Details", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

    if 'ai_response' in st.session_state and st.session_state.ai_response:
        st.markdown("---")
        st.markdown(st.session_state.ai_response)


def build_ai_prompt(user_profile, prop_details):
    """Constructs the detailed prompt for the Gemini API."""
    prompt = f"""
        Act as a friendly, expert real estate advisor in India for a client named {user_profile['name']}.

        **CLIENT'S BASE PROFILE:**
        - Age: {calculate_age(user_profile['dob'])} years
        - Annual Income: Rs {user_profile['income']:,}

        **CLIENT'S DETAILED REQUIREMENTS:**
        - Primary Goal: {prop_details.get('intent_type', 'N/A')}
        - Main Purpose: {prop_details.get('intent_purpose', 'N/A')}
        - Target City: {prop_details.get('loc_city', 'N/A')}
        - Budget: Rs {prop_details.get('fin_budget', 0):,}
        - Needs Loan: {'Yes' if prop_details.get('fin_loan') else 'No'}
        - Interest in Subsidy: {'Yes' if prop_details.get('fin_subsidy') else 'No'}

        **PROPERTY SPECIFICS (only consider relevant fields):**
        - For Mixed Strategy: {', '.join(prop_details.get('mixed_components', [])) or 'N/A'}
        - Flat Size: {prop_details.get('plan_flat_size', 'N/A')}
        - Plot Area: {prop_details.get('plan_plot_area', 'N/A')} sq. ft
        - Built-up Area: {prop_details.get('plan_built_up', 'N/A')} sq. ft
        - Floors to Build: {prop_details.get('plan_floors', 'N/A')}
        - Extra floors for rent: {'Yes' if prop_details.get('extra_floors_rent') else 'No'}
        
        **CONSTRUCTION DETAILS (if building):**
        - Contract Type: {prop_details.get('const_contract', 'N/A')}
        - Build Timeline: {prop_details.get('const_timeline', 'N/A')} months
        - Vendors Needed: {', '.join(prop_details.get('const_vendors', [])) or 'N/A'}
        - Green Features: {', '.join(prop_details.get('const_green', [])) or 'N/A'}

        **INVESTMENT GOALS (if applicable):**
        - Target Rental Income: Rs {prop_details.get('fin_target_rent', 0):,}
        - Target Resale Price: Rs {prop_details.get('fin_target_resale', 0):,}

        **PREFERENCES & CONCERNS:**
        - Connectivity Importance: {prop_details.get('qual_connectivity', 'N/A')}
        - Proximity to Amenities: {prop_details.get('qual_amenities', 'N/A')}
        - Concerns: Pollution Level ({prop_details.get('risk_pollution', 'N/A')}), Crime Level ({prop_details.get('risk_crime', 'N/A')})

        **MARKET DATA CONTEXT for {prop_details.get('loc_city', 'your city')}:**
        {get_price_data(prop_details.get('loc_city', '')).to_markdown()}
        ---
        **YOUR TASK:** Generate a comprehensive and highly personalized report in Markdown. Address ONLY the fields provided.
        1. ### Executive Summary: Give a direct recommendation based on their goal. Justify it against their budget, purpose, and market data.
        2. ### Strategy Deep Dive: Elaborate on the recommendation. Address their specific requirements and risk concerns. If it's a 'Mixed' strategy, analyze each component.
        3. ### Financial Analysis: Provide a realistic cost breakdown vs. their budget. Estimate loan eligibility and a potential EMI. Mention the feasibility of their investment goals (rent/resale).
        4. ### Action Plan: Create a checklist of the immediate next 5 steps for {user_profile['name']}, directly tied to their specific plan.
    """
    return textwrap.dedent(prompt)

# ─────────────────────────────────────────────────────────────────────────────
# Main App Controller
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Real Estate Advisor", page_icon="🏠", layout="wide")

    # Initialize session state keys
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'profiles' not in st.session_state:
        st.session_state.profiles = {}
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None
    if 'property_details' not in st.session_state:
        st.session_state.property_details = {}

    display_sidebar()
    st.title("AI Real Estate Advisor")

    if not st.session_state.selected_profile:
        st.info("Welcome! Please create a new profile or load an existing one from the sidebar to begin.")
    else:
        active_profile_name = st.session_state.selected_profile
        user_profile = st.session_state.profiles[active_profile_name]
        
        st.markdown(f"### Plan for **{user_profile['name'].title()}** (Profile: *{active_profile_name}*)")
        st.markdown("---")
        
        # --- Multi-Step UI Controller ---
        if st.session_state.step == 1:
            display_step1_intent_form()
        elif st.session_state.step == 2:
            display_step2_details_form()
        elif st.session_state.step == 3:
            display_step3_analysis_section(user_profile, st.session_state.property_details)

if __name__ == "__main__":
    main()