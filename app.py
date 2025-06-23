# app.py – Streamlit Real Estate Advisor (INSECURE - Hard-coded API Key, with Detailed Requirements)

"""
Real Estate Advisor: Your Personal AI-Powered Property Guide

This version integrates a comprehensive requirements gathering form before AI generation,
leading to a highly personalized and detailed strategy.

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
    """
    Configures the Gemini API with a hard-coded key.
    WARNING: This is not a secure practice.
    """
    try:
        # --- REMINDER: Replace this key with a new, secret key ---
        genai.configure(api_key="AIzaSyBb-KXLYLyRO4o2TFAeiOQNv4fG54O0GEU")
        
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
            return "Warning: The AI returned an empty response. This may be due to the safety settings of the API. Please try a different query."
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
# Streamlit Interface
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="Real Estate Advisor", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

    # --- Initialize Session State ---
    if 'profiles' not in st.session_state:
        st.session_state.profiles = {}
    if 'selected_profile' not in st.session_state:
        st.session_state.selected_profile = None
    if 'details_submitted' not in st.session_state:
        st.session_state.details_submitted = False
    if 'property_details' not in st.session_state:
        st.session_state.property_details = {}

    # --- Sidebar for Profile Management ---
    with st.sidebar:
        st.image("https://i.imgur.com/rLdD2b5.png", width=150)
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
                            st.session_state.details_submitted = False
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
                st.session_state.details_submitted = False
                st.session_state.property_details = {}

            try:
                current_index = profile_options.index(st.session_state.selected_profile)
            except (ValueError, TypeError):
                current_index = 0
                if profile_options:
                    st.session_state.selected_profile = profile_options[0]
            
            st.selectbox("Select Profile", options=profile_options, index=current_index, key="profile_select_key", on_change=on_profile_change)

    # --- Main App Body ---
    st.title("AI Real Estate Advisor")

    if not st.session_state.selected_profile:
        st.info("Welcome! Please create a new profile or load an existing one from the sidebar to begin.")
    else:
        active_profile_name = st.session_state.selected_profile
        p = st.session_state.profiles[active_profile_name]
        st.markdown(f"### Plan for **{p['name'].title()}** (Profile: *{active_profile_name}*)")
        st.markdown("---")
        
        # --- Step 1: Detailed Requirements Form ---
        st.subheader("STEP 1: Tell Us Your Requirements")
        
        with st.form("property_details_form"):
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("#### Property Intent")
                intent_type = st.selectbox("Property Type", ['Build', 'Buy Flat', 'Buy Plot', 'Rent Invest', 'Mixed'])
                intent_purpose = st.selectbox("Purpose", ['Self Use', 'Rent', 'Resale', 'Joint Invest'])
                
                st.markdown("#### Location")
                loc_city = st.text_input("City", value="Nagpur")
                loc_locality = st.text_input("Preferred Locality / Area")
                loc_pincode = st.text_input("Pin Code", max_chars=6)
                
                st.markdown("#### Budget and Finance")
                fin_budget = st.number_input("Total Budget (Rs)", min_value=100000, step=100000, format="%d")
                fin_loan = st.checkbox("Loan Needed")
                
            with c2:
                st.markdown("#### Property Plan")
                if intent_type == 'Build' or intent_type == 'Buy Plot':
                    plan_plot_area = st.number_input("Plot Area (sq. ft)", min_value=300, value=1200)
                if intent_type == 'Build':
                    plan_built_up = st.number_input("Built-up Area (sq. ft)", min_value=200, value=1000)
                if intent_type == 'Buy Flat':
                    plan_flat_size = st.selectbox("Flat Size", ['1BHK', '2BHK', '3BHK', '4BHK+', 'Custom'])

                st.markdown("#### Optional Extras")
                opt_parking = st.checkbox("Parking Needed")
                opt_design = st.selectbox("Preferred Design Style", ['No Preference', 'Modern', 'Traditional', 'Eco-friendly', 'Minimalist'])
                opt_quality = st.selectbox("Material Quality", ['Basic', 'Standard', 'Premium'])
            
            if intent_type == 'Build':
                st.markdown("---")
                st.markdown("#### Construction Details (for 'Build' only)")
                c3, c4 = st.columns(2)
                with c3:
                    const_contract = st.selectbox("Contract Type", ['With Material', 'Without Material'])
                    const_vendors = st.multiselect("Vendors Needed", ['Plumbing', 'Electrical', 'Tiles', 'Paint', 'Solar', 'Interiors', 'CCTV', 'Automation', 'Landscaping'])
                with c4:
                    const_green = st.multiselect("Green Features", ['Solar Panels', 'Rainwater Harvesting', 'Heat Insulation', 'EV Charging Point', 'Greywater Recycling'])
                    const_timeline = st.slider("Build Timeline (Months)", 3, 36, 12)
            
            st.markdown("---")
            st.markdown("#### Risk and Location Quality")
            c5, c6 = st.columns(2)
            with c5:
                risk_flood = st.checkbox("Concerned about Flood Zones?")
                risk_eco = st.checkbox("Concerned about Eco-sensitive Zones?")
                risk_dispute = st.checkbox("Concerned about Land Disputes?")
            with c6:
                qual_connectivity = st.select_slider("Connectivity Importance", ['Low', 'Medium', 'High'])
                qual_amenities = st.select_slider("Proximity to Schools/Hospitals", ['Not Important', 'Somewhat', 'Very Important'])
                qual_group_buy = st.checkbox("Open to Group Buying?")

            st.markdown("---")
            consent = st.checkbox(f"I, {p['name'].title()}, consent to using this data for analysis.")
            
            submitted = st.form_submit_button("Save Requirements and Unlock AI Analysis", use_container_width=True)
            if submitted:
                if not consent:
                    st.error("You must provide consent to proceed.")
                else:
                    st.session_state.property_details = {
                        "intent_type": intent_type, "intent_purpose": intent_purpose,
                        "loc_city": loc_city, "loc_locality": loc_locality, "loc_pincode": loc_pincode,
                        "fin_budget": fin_budget, "fin_loan": "Yes" if fin_loan else "No",
                        "plan_plot_area": locals().get("plan_plot_area"), "plan_built_up": locals().get("plan_built_up"), "plan_flat_size": locals().get("plan_flat_size"),
                        "opt_parking": "Yes" if opt_parking else "No", "opt_design": opt_design, "opt_quality": opt_quality,
                        "const_contract": locals().get("const_contract"), "const_vendors": locals().get("const_vendors", []), "const_green": locals().get("const_green", []), "const_timeline": locals().get("const_timeline"),
                        "risk_flood": "Yes" if risk_flood else "No", "risk_eco": "Yes" if risk_eco else "No", "risk_dispute": "Yes" if risk_dispute else "No",
                        "qual_connectivity": qual_connectivity, "qual_amenities": qual_amenities, "qual_group_buy": "Yes" if qual_group_buy else "No"
                    }
                    st.session_state.details_submitted = True
                    st.success("Requirements saved! You can now generate your personalized strategy below.")
                    st.rerun()

        # --- Step 2: AI Plan Generation ---
        st.markdown("---")
        st.subheader("STEP 2: Generate Your AI-Powered Strategy")
        
        if st.button("Generate My Real Estate Strategy", type="primary", use_container_width=True, disabled=not st.session_state.details_submitted):
            user_profile = p
            prop_details = st.session_state.property_details
            
            prompt = textwrap.dedent(f"""
                Act as a friendly, expert real estate advisor in India for a client named {user_profile['name']}.

                CLIENT'S BASE PROFILE:
                - Age: {calculate_age(user_profile['dob'])} years
                - Annual Income: Rs {user_profile['income']:,}
                - Contact: {user_profile['contact']}

                DETAILED PROPERTY REQUIREMENTS:
                
                Intent and Location:
                - Goal: {prop_details['intent_type']} a property for the purpose of {prop_details['intent_purpose']}.
                - Location: {prop_details['loc_locality']}, {prop_details['loc_city']} ({prop_details['loc_pincode']})

                Financials:
                - Total Budget: Rs {prop_details['fin_budget']:,}
                - Needs Loan: {prop_details['fin_loan']}

                Property Plan:
                - Type Specifics:
                  {'Plot Area: ' + str(prop_details['plan_plot_area']) + ' sq. ft' if prop_details.get('plan_plot_area') else ''}
                  {'Built-up Area: ' + str(prop_details['plan_built_up']) + ' sq. ft' if prop_details.get('plan_built_up') else ''}
                  {'Flat Size: ' + str(prop_details['plan_flat_size']) if prop_details.get('plan_flat_size') else ''}
                - Preferences: Parking: {prop_details['opt_parking']}, Design: {prop_details['opt_design']}, Material Quality: {prop_details['opt_quality']}

                Risk and Quality Factors:
                - Concerns: Flood Zone ({prop_details['risk_flood']}), Eco-sensitive Zone ({prop_details['risk_eco']}), Land Disputes ({prop_details['risk_dispute']})
                - Priorities: Connectivity is of {prop_details['qual_connectivity']} importance. Proximity to amenities is {prop_details['qual_amenities']}.
                - Group Buying: Client is {'open' if prop_details['qual_group_buy'] == 'Yes' else 'not open'} to group buying.
                
                Construction Details (if applicable):
                {'Contract Type: ' + str(prop_details.get('const_contract')) if prop_details.get('const_contract') else ''}
                {'Timeline: ' + str(prop_details.get('const_timeline')) + ' months' if prop_details.get('const_timeline') else ''}
                {'Vendors Needed: ' + ', '.join(prop_details.get('const_vendors', [])) if prop_details.get('const_vendors') else ''}
                {'Green Features Desired: ' + ', '.join(prop_details.get('const_green', [])) if prop_details.get('const_green') else ''}

                MARKET DATA CONTEXT for {prop_details['loc_city']}:
                {get_price_data(prop_details['loc_city']).to_markdown()}

                ---
                YOUR TASK: Generate a comprehensive and highly personalized report in Markdown.
                1. ### Executive Summary: Give a direct recommendation (e.g., "Proceed with Buying a 2BHK Flat," "Re-evaluate Budget for Building," "Focus on Plot Investment"). Justify based on the client's detailed requirements vs. their budget and market data.
                2. ### Strategy Deep Dive: Elaborate on the recommendation. If 'Buy', suggest specific configurations. If 'Build', discuss material and contract choices. If 'Invest', suggest potential ROI. Address their specific risk concerns (flood, eco-zones) and how to mitigate them.
                3. ### Financial Analysis: Provide a realistic breakdown. Is their budget feasible for their plan in {prop_details['loc_city']}? Estimate loan eligibility based on their income. Project a down payment and potential EMI.
                4. ### Action Plan: Create a checklist of the immediate next 5 steps for {user_profile['name']}, directly tied to their plan. (e.g., 'Verify {prop_details['loc_locality']} for flood plain maps', 'Get pre-approved loan amount', 'Contact 3 architects for quotes').
            """)
            
            with st.spinner("Analyzing your detailed requirements and crafting a custom strategy..."):
                response = ask_gemini(prompt)
            st.markdown(response)
            
        elif not st.session_state.details_submitted:
            st.warning("Please fill out and save your requirements in Step 1 to enable this button.")

if __name__ == "__main__":
    main()