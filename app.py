# app.py – Streamlit Real Estate Advisor (Multi-Language, Multi-Step, & File-based)

"""
🏠 AI Real Estate Advisor: Your Guided Project Planner

This is a comprehensive, multi-language version that combines a guided workflow 
with a robust project storage system. Users can switch between English, Hindi, 
and Marathi.

FEATURES:
- **Multi-Language Support:** UI and AI responses in English, Hindi, and Marathi.
- **Guided Multi-Step UI:** A clear 4-step process for defining a project.
- **Dynamic Forms:** The UI adapts to the user's specific goals (Buy, Build, etc.).
- **Individual Project Files:** Each project is saved as a unique CSV in a 'projects' 
  directory for easy management.
- **Enhanced Sidebar:** A dynamic sidebar shows the active project and provides 
  controls to switch, load, create, or delete projects.
- **Quantitative AI Analysis:** Generates detailed financial reports in the selected language.

▶ Run:
    streamlit run app.py

📦 Requirements (add to requirements.txt):
    streamlit
    google-generativeai>=0.4.0
    pandas
"""

import os
import random
import textwrap
import pandas as pd
import streamlit as st
from datetime import date

# --- Directory for storing individual project files ---
PROJECTS_DIR = "projects"
os.makedirs(PROJECTS_DIR, exist_ok=True)

try:
    import google.generativeai as genai
except ImportError:
    st.error("Gemini API library not found. Please run 'pip install google-generativeai' in your environment.")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# Gemini Setup with Multiple Keys (More Robust for Development)
# ─────────────────────────────────────────────────────────────────────────────
# WARNING: For production, use Streamlit Secrets (st.secrets). Hardcoding keys is insecure.
GEMINI_API_KEYS = [
    "AIzaSyADl4G5aVaq3xw73HJiPDalelfqFH_XHCI", "AIzaSyBvx7uEa_JvFsnwyoubw380dg4HUOr9ASY",
    # Add more keys as needed
]
valid_api_keys = [key for key in GEMINI_API_KEYS if "YOUR_API_KEY" not in key]

if not valid_api_keys:
    st.error("🔐 No valid Gemini API Keys found. Please add your keys to the GEMINI_API_KEYS list in the code.")
    st.stop()

selected_key = random.choice(valid_api_keys)
genai.configure(api_key=selected_key)
MODEL = genai.GenerativeModel("gemini-1.5-flash")

# --- Translation Dictionary ---
TRANSLATIONS = {
    'en': {
        "language_name": "English",
        "app_title": "AI Real Estate Advisor",
        "project_manager_title": "Project Manager",
        "active_project_caption": "Active Project",
        "switch_project_button": "🔄 Switch Project",
        "danger_zone_header": "🚨 Danger Zone",
        "delete_confirm_checkbox": "Confirm deletion",
        "delete_project_button": "❌ Delete Project Permanently",
        "project_deleted_success": "Project '{project_name}' has been deleted.",
        "project_file_not_found_warning": "Project file for '{project_name}' not found.",
        "delete_project_error": "Error deleting project: {e}",
        "create_new_project_header": "➕ Create New Project",
        "new_project_name_label": "Enter a Unique Project Name",
        "start_new_project_button": "Start New Project",
        "project_name_exists_error": "Project name already exists.",
        "enter_project_name_warning": "Please enter a project name.",
        "load_existing_project_header": "📂 Load Existing Project",
        "select_project_placeholder": "Choose a project...",
        "load_project_button": "Load Project",
        "project_loaded_success": "Project '{project_name}' loaded successfully!",
        "load_project_error": "Failed to load project '{project_name}': {e}",
        "disclaimer_info": "AI-generated advice. Always consult a professional before making financial decisions.",
        "welcome_message": "👋 **Welcome!** To begin, please create a new project or load an existing one from the sidebar.",
        "current_project_header": "Current Project: **{project_name}**",
        "step1_header": "STEP 1: Your Personal Details",
        "full_name_label": "Full Name",
        "dob_label": "Date of Birth",
        "contact_label": "Email or Phone",
        "income_label": "Annual Household Income (₹)",
        "next_goal_button": "Next: Define Your Goal",
        "fill_all_details_error": "Please fill in all details.",
        "step2_header": "STEP 2: What is Your Primary Goal?",
        "select_goal_label": "Select your goal",
        "buy_flat": "Buy a Flat",
        "build_house": "Build a House",
        "buy_plot": "Buy a Plot",
        "mixed_investment": "Mixed / Investment",
        "next_specifics_button": "Next: Add Specifics",
        "step3_header": "STEP 3: Specifics for '{intent_type}'",
        "location_budget_header": "Location & Budget",
        "target_city_label": "Target City",
        "localities_label": "Preferred Localities (comma-separated)",
        "pincode_label": "Pin Code",
        "budget_label": "Total Budget (₹)",
        "need_loan_checkbox": "Need a loan?",
        "subsidy_checkbox": "Interested in subsidy schemes?",
        "main_purpose_label": "Main purpose?",
        "self_use": "Self Use",
        "rental_income": "Rental Income",
        "resale_investment": "Resale / Investment",
        "mixed_components_label": "Select all that apply:",
        "flat_details_header": "Flat Details",
        "flat_size_label": "Flat Size",
        "plot_details_header": "Plot Details",
        "plot_area_label": "Plot Area (sq. ft)",
        "construction_details_header": "Construction Details",
        "built_up_area_label": "Target Built-up Area (sq. ft)",
        "floors_label": "Number of Floors Planned",
        "extra_floors_rent_checkbox": "Plan extra floors for rent?",
        "contract_type_label": "Contract Type",
        "vendors_label": "Specific Vendors Needed?",
        "green_features_label": "Desired Green Features",
        "timeline_label": "Estimated Build Timeline (Months)",
        "preferences_concerns_header": "Preferences & Concerns",
        "connectivity_label": "Connectivity Importance",
        "amenities_label": "Proximity to Schools/Hospitals",
        "pollution_label": "Pollution Concern Level",
        "crime_label": "Crime Concern Level",
        "investment_goals_header": "Investment Goals",
        "target_rent_label": "Target Monthly Rent Income (₹)",
        "target_resale_label": "Target Resale Price (₹)",
        "save_proceed_button": "Save Project & Proceed to Analysis",
        "step4_header": "STEP 4: Review and Generate AI Strategy",
        "project_saved_success": "Your project is saved. Review the details below and generate your personalized financial plan.",
        "view_details_expander": "View/Hide Your Saved Project Details",
        "market_snapshot_header": "📈 Market Snapshot: {city}",
        "generate_strategy_button": "🧠 Generate Financial Strategy",
        "edit_details_button": "✏️ Edit Project Details",
        "analyzing_spinner": "🤖 Analyzing your project and crafting a detailed financial plan...",
        "strategy_header": "💡 Your Personalized Financial Strategy",
        "follow_up_expander": "💬 Ask a Follow-up Question",
        "follow_up_placeholder": "e.g., What happens if the interest rate increases by 0.5%?",
        "ask_gemini_button": "✉️ Ask Gemini",
        "enter_question_warning": "Please enter a question.",
        "thinking_spinner": "🤔 Thinking...",
    },
    'hi': {
        "language_name": "Hindi (हिन्दी)",
        "app_title": "एआई रियल एस्टेट सलाहकार",
        "project_manager_title": "प्रोजेक्ट मैनेजर",
        "active_project_caption": "सक्रिय प्रोजेक्ट",
        "switch_project_button": "🔄 प्रोजेक्ट बदलें",
        "danger_zone_header": "🚨 खतरा क्षेत्र",
        "delete_confirm_checkbox": "हटाने की पुष्टि करें",
        "delete_project_button": "❌ प्रोजेक्ट स्थायी रूप से हटाएं",
        "project_deleted_success": "प्रोजेक्ट '{project_name}' हटा दिया गया है।",
        "project_file_not_found_warning": "प्रोजेक्ट '{project_name}' की फ़ाइल नहीं मिली।",
        "delete_project_error": "प्रोजेक्ट हटाने में त्रुटि: {e}",
        "create_new_project_header": "➕ नया प्रोजेक्ट बनाएं",
        "new_project_name_label": "एक अद्वितीय प्रोजेक्ट नाम दर्ज करें",
        "start_new_project_button": "नया प्रोजेक्ट शुरू करें",
        "project_name_exists_error": "प्रोजेक्ट का नाम पहले से मौजूद है।",
        "enter_project_name_warning": "कृपया एक प्रोजेक्ट नाम दर्ज करें।",
        "load_existing_project_header": "📂 मौजूदा प्रोजेक्ट लोड करें",
        "select_project_placeholder": "एक प्रोजेक्ट चुनें...",
        "load_project_button": "प्रोजेक्ट लोड करें",
        "project_loaded_success": "प्रोजेक्ट '{project_name}' सफलतापूर्वक लोड हो गया!",
        "load_project_error": "प्रोजेक्ट '{project_name}' लोड करने में विफल: {e}",
        "disclaimer_info": "एआई-जनित सलाह। वित्तीय निर्णय लेने से पहले हमेशा एक पेशेवर से सलाह लें।",
        "welcome_message": "👋 **आपका स्वागत है!** शुरू करने के लिए, कृपया एक नया प्रोजेक्ट बनाएं या साइडबार से किसी मौजूदा प्रोजेक्ट को लोड करें।",
        "current_project_header": "वर्तमान प्रोजेक्ट: **{project_name}**",
        "step1_header": "चरण 1: आपका व्यक्तिगत विवरण",
        "full_name_label": "पूरा नाम",
        "dob_label": "जन्म तिथि",
        "contact_label": "ईमेल या फ़ोन",
        "income_label": "वार्षिक घरेलू आय (₹)",
        "next_goal_button": "अगला: अपना लक्ष्य परिभाषित करें",
        "fill_all_details_error": "कृपया सभी विवरण भरें।",
        "step2_header": "चरण 2: आपका प्राथमिक लक्ष्य क्या है?",
        "select_goal_label": "अपना लक्ष्य चुनें",
        "buy_flat": "फ्लैट खरीदें",
        "build_house": "घर बनाएं",
        "buy_plot": "प्लॉट खरीदें",
        "mixed_investment": "मिश्रित / निवेश",
        "next_specifics_button": "अगला: विवरण जोड़ें",
        "step3_header": "चरण 3: '{intent_type}' के लिए विवरण",
        "location_budget_header": "स्थान और बजट",
        "target_city_label": "लक्षित शहर",
        "localities_label": "पसंदीदा इलाके (अल्पविराम से अलग)",
        "pincode_label": "पिन कोड",
        "budget_label": "कुल बजट (₹)",
        "need_loan_checkbox": "ऋण चाहिए?",
        "subsidy_checkbox": "सब्सिडी योजनाओं में रुचि है?",
        "main_purpose_label": "मुख्य उद्देश्य?",
        "self_use": "स्वयं उपयोग",
        "rental_income": "किराये से आय",
        "resale_investment": "पुनर्विक्रय / निवेश",
        "mixed_components_label": "सभी लागू होने वाले चुनें:",
        "flat_details_header": "फ्लैट का विवरण",
        "flat_size_label": "फ्लैट का आकार",
        "plot_details_header": "प्लॉट का विवरण",
        "plot_area_label": "प्लॉट क्षेत्र (वर्ग फुट)",
        "construction_details_header": "निर्माण विवरण",
        "built_up_area_label": "लक्षित निर्मित क्षेत्र (वर्ग फुट)",
        "floors_label": "नियोजित मंजिलों की संख्या",
        "extra_floors_rent_checkbox": "किराए के लिए अतिरिक्त मंजिल की योजना बनाएं?",
        "contract_type_label": "अनुबंध का प्रकार",
        "vendors_label": "विशिष्ट विक्रेताओं की आवश्यकता है?",
        "green_features_label": "वांछित हरित सुविधाएँ",
        "timeline_label": "अनुमानित निर्माण समय-सीमा (महीने)",
        "preferences_concerns_header": "वरीयताएँ और चिंताएँ",
        "connectivity_label": "कनेक्टिविटी का महत्व",
        "amenities_label": "स्कूलों/अस्पतालों से निकटता",
        "pollution_label": "प्रदूषण चिंता स्तर",
        "crime_label": "अपराध चिंता स्तर",
        "investment_goals_header": "निवेश लक्ष्य",
        "target_rent_label": "लक्षित मासिक किराया आय (₹)",
        "target_resale_label": "लक्षित पुनर्विक्रय मूल्य (₹)",
        "save_proceed_button": "प्रोजेक्ट सहेजें और विश्लेषण के लिए आगे बढ़ें",
        "step4_header": "चरण 4: समीक्षा करें और एआई रणनीति उत्पन्न करें",
        "project_saved_success": "आपका प्रोजेक्ट सहेज लिया गया है। नीचे दिए गए विवरणों की समीक्षा करें और अपनी व्यक्तिगत वित्तीय योजना बनाएं।",
        "view_details_expander": "सहेजे गए प्रोजेक्ट विवरण देखें/छुपाएं",
        "market_snapshot_header": "📈 बाजार स्नैपशॉट: {city}",
        "generate_strategy_button": "🧠 वित्तीय रणनीति उत्पन्न करें",
        "edit_details_button": "✏️ प्रोजेक्ट विवरण संपादित करें",
        "analyzing_spinner": "🤖 आपके प्रोजेक्ट का विश्लेषण किया जा रहा है और एक विस्तृत वित्तीय योजना तैयार की जा रही है...",
        "strategy_header": "💡 आपकी व्यक्तिगत वित्तीय रणनीति",
        "follow_up_expander": "💬 एक अनुवर्ती प्रश्न पूछें",
        "follow_up_placeholder": "उदा., यदि ब्याज दर 0.5% बढ़ जाती है तो क्या होगा?",
        "ask_gemini_button": "✉️ जेमिनी से पूछें",
        "enter_question_warning": "कृपया एक प्रश्न दर्ज करें।",
        "thinking_spinner": "🤔 सोच रहा हूँ...",
    },
    'mr': {
        "language_name": "Marathi (मराठी)",
        "app_title": "एआय रिअल इस्टेट सल्लागार",
        "project_manager_title": "प्रकल्प व्यवस्थापक",
        "active_project_caption": "सक्रिय प्रकल्प",
        "switch_project_button": "🔄 प्रकल्प बदला",
        "danger_zone_header": "🚨 धोकादायक क्षेत्र",
        "delete_confirm_checkbox": "हटवण्याची पुष्टी करा",
        "delete_project_button": "❌ प्रकल्प कायमचा हटवा",
        "project_deleted_success": "प्रकल्प '{project_name}' हटवला आहे.",
        "project_file_not_found_warning": "प्रकल्प '{project_name}' ची फाइल सापडली नाही.",
        "delete_project_error": "प्रकल्प हटवण्यात त्रुटी: {e}",
        "create_new_project_header": "➕ नवीन प्रकल्प तयार करा",
        "new_project_name_label": "एक अद्वितीय प्रकल्प नाव प्रविष्ट करा",
        "start_new_project_button": "नवीन प्रकल्प सुरू करा",
        "project_name_exists_error": "प्रकल्पाचे नाव आधीच अस्तित्वात आहे.",
        "enter_project_name_warning": "कृपया प्रकल्पाचे नाव प्रविष्ट करा.",
        "load_existing_project_header": "📂 विद्यमान प्रकल्प लोड करा",
        "select_project_placeholder": "एक प्रकल्प निवडा...",
        "load_project_button": "प्रकल्प लोड करा",
        "project_loaded_success": "प्रकल्प '{project_name}' यशस्वीरित्या लोड झाला!",
        "load_project_error": "प्रकल्प '{project_name}' लोड करण्यात अयशस्वी: {e}",
        "disclaimer_info": "एआय-व्युत्पन्न सल्ला. आर्थिक निर्णय घेण्यापूर्वी नेहमी व्यावसायिकांचा सल्ला घ्या.",
        "welcome_message": "👋 **स्वागत आहे!** सुरू करण्यासाठी, कृपया नवीन प्रकल्प तयार करा किंवा साइडबारमधून विद्यमान प्रकल्प लोड करा.",
        "current_project_header": "सध्याचा प्रकल्प: **{project_name}**",
        "step1_header": "पायरी 1: आपले वैयक्तिक तपशील",
        "full_name_label": "पूर्ण नाव",
        "dob_label": "जन्म तारीख",
        "contact_label": "ईमेल किंवा फोन",
        "income_label": "वार्षिक कौटुंबिक उत्पन्न (₹)",
        "next_goal_button": "पुढील: आपले ध्येय निश्चित करा",
        "fill_all_details_error": "कृपया सर्व तपशील भरा.",
        "step2_header": "पायरी 2: आपले प्राथमिक ध्येय काय आहे?",
        "select_goal_label": "आपले ध्येय निवडा",
        "buy_flat": "फ्लॅट खरेदी करा",
        "build_house": "घर बांधा",
        "buy_plot": "प्लॉट खरेदी करा",
        "mixed_investment": "मिश्र / गुंतवणूक",
        "next_specifics_button": "पुढील: तपशील जोडा",
        "step3_header": "पायरी 3: '{intent_type}' साठी तपशील",
        "location_budget_header": "स्थान आणि बजेट",
        "target_city_label": "लक्ष्य शहर",
        "localities_label": "पसंतीचे परिसर (स्वल्पविरामाने वेगळे)",
        "pincode_label": "पिन कोड",
        "budget_label": "एकूण बजेट (₹)",
        "need_loan_checkbox": "कर्ज हवे आहे का?",
        "subsidy_checkbox": "अनुदान योजनांमध्ये रस आहे का?",
        "main_purpose_label": "मुख्य उद्देश?",
        "self_use": "स्वतःचा वापर",
        "rental_income": "भाड्याचे उत्पन्न",
        "resale_investment": "पुनर्विक्री / गुंतवणूक",
        "mixed_components_label": "लागू असलेले सर्व निवडा:",
        "flat_details_header": "फ्लॅट तपशील",
        "flat_size_label": "फ्लॅटचा आकार",
        "plot_details_header": "प्लॉट तपशील",
        "plot_area_label": "प्लॉट क्षेत्र (चौ. फूट)",
        "construction_details_header": "बांधकाम तपशील",
        "built_up_area_label": "लक्ष्यित बिल्ट-अप क्षेत्र (चौ. फूट)",
        "floors_label": "नियोजित मजल्यांची संख्या",
        "extra_floors_rent_checkbox": "भाड्यासाठी अतिरिक्त मजल्यांची योजना आहे का?",
        "contract_type_label": "कराराचा प्रकार",
        "vendors_label": "विशिष्ट विक्रेत्यांची आवश्यकता आहे का?",
        "green_features_label": "इच्छित हरित वैशिष्ट्ये",
        "timeline_label": "अंदाजित बांधकाम कालावधी (महिने)",
        "preferences_concerns_header": "प्राधान्ये आणि चिंता",
        "connectivity_label": "कनेक्टिव्हिटीचे महत्त्व",
        "amenities_label": "शाळा/रुग्णालयांपासूनचे अंतर",
        "pollution_label": "प्रदूषण चिंता पातळी",
        "crime_label": "गुन्हेगारी चिंता पातळी",
        "investment_goals_header": "गुंतवणूक ध्येये",
        "target_rent_label": "लक्ष्यित मासिक भाडे उत्पन्न (₹)",
        "target_resale_label": "लक्ष्यित पुनर्विक्री किंमत (₹)",
        "save_proceed_button": "प्रकल्प जतन करा आणि विश्लेषणासाठी पुढे जा",
        "step4_header": "पायरी 4: पुनरावलोकन करा आणि एआय धोरण तयार करा",
        "project_saved_success": "तुमचा प्रकल्प जतन झाला आहे. खालील तपशीलांचे पुनरावलोकन करा आणि तुमची वैयक्तिक आर्थिक योजना तयार करा.",
        "view_details_expander": "जतन केलेले प्रकल्प तपशील पहा/लपवा",
        "market_snapshot_header": "📈 बाजारपेठेचा स्नॅपशॉट: {city}",
        "generate_strategy_button": "🧠 आर्थिक धोरण तयार करा",
        "edit_details_button": "✏️ प्रकल्प तपशील संपादित करा",
        "analyzing_spinner": "🤖 तुमच्या प्रकल्पाचे विश्लेषण करत आहे आणि तपशीलवार आर्थिक योजना तयार करत आहे...",
        "strategy_header": "💡 तुमची वैयक्तिक आर्थिक धोरण",
        "follow_up_expander": "💬 एक फॉलो-अप प्रश्न विचारा",
        "follow_up_placeholder": "उदा., व्याजदर 0.5% ने वाढल्यास काय होईल?",
        "ask_gemini_button": "✉️ जेमिनीला विचारा",
        "enter_question_warning": "कृपया एक प्रश्न प्रविष्ट करा.",
        "thinking_spinner": "🤔 विचार करत आहे...",
    }
}

def t(key):
    """Translation helper function."""
    return TRANSLATIONS[st.session_state.language].get(key, key)

# --- Constants ---
CSV_COLUMNS = [
    'project_name','name','contact','dob','income','intent_type','intent_purpose','loc_city','loc_locality',
    'loc_pincode','fin_budget','fin_loan','fin_subsidy','mixed_components','plan_flat_size','plan_plot_area',
    'plan_built_up','plan_floors','extra_floors_rent','const_contract','const_vendors','const_green',
    'const_timeline','qual_connectivity','qual_amenities','risk_pollution','risk_crime',
    'fin_target_rent','fin_target_resale'
]

# ─────────────────────────────────────────────────────────────────────────────
# Core Functions (AI & Project Management)
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def ask_gemini(prompt: str, temperature: float = 0.4) -> str:
    """Sends prompt to Gemini API and returns the response text."""
    try:
        response = MODEL.generate_content(prompt, generation_config={"temperature": temperature})
        return response.text
    except Exception as err:
        st.error(f"⚠️ An error occurred with the Gemini API: {err}", icon="🤖")
        return "Sorry, I couldn't process your request. The API may be busy. Please try again."

def get_saved_projects():
    """Scans the projects directory and returns a list of project names."""
    return sorted([f.replace(".csv", "").replace("_", " ") for f in os.listdir(PROJECTS_DIR) if f.endswith(".csv")])

def get_project_filepath(project_name):
    """Generates the standard filepath for a given project name."""
    return os.path.join(PROJECTS_DIR, f"{project_name.replace(' ', '_')}.csv")

def save_project():
    """Saves the current project data from session state to a dedicated CSV file."""
    project_name = st.session_state.selected_project
    if not project_name:
        st.error("Cannot save: No project is currently active.")
        return

    data_to_save = {}
    for key in CSV_COLUMNS:
        data_to_save[key] = st.session_state.get(key)
    data_to_save['project_name'] = project_name

    for key in ['mixed_components', 'const_vendors', 'const_green']:
        if key in data_to_save and isinstance(data_to_save[key], list):
            data_to_save[key] = '|'.join(map(str, data_to_save[key]))
    
    if 'dob' in data_to_save and isinstance(data_to_save[key], date):
        data_to_save['dob'] = data_to_save['dob'].isoformat()

    try:
        df = pd.DataFrame([data_to_save])
        df = df[CSV_COLUMNS]
        filepath = get_project_filepath(project_name)
        df.to_csv(filepath, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving project '{project_name}': {e}")
        return False

def load_project(project_name):
    """Loads a project from a CSV file into the session state."""
    filepath = get_project_filepath(project_name)
    try:
        df = pd.read_csv(filepath).fillna('')
        project_dict = df.to_dict('records')[0]
        
        for key in ['mixed_components', 'const_vendors', 'const_green']:
            if isinstance(project_dict.get(key), str) and project_dict[key]:
                project_dict[key] = project_dict[key].split('|')
            else:
                project_dict[key] = []
        
        if 'dob' in project_dict and project_dict['dob']:
            project_dict['dob'] = date.fromisoformat(str(project_dict['dob']))
        else:
            project_dict['dob'] = date(2000, 1, 1)
        
        st.session_state.selected_project = project_name
        for key, value in project_dict.items():
            st.session_state[key] = value

        st.session_state.step = 4
        st.session_state.ai_response = None
        st.session_state.follow_up_response = None
        st.success(t('project_loaded_success').format(project_name=project_name))
    except Exception as e:
        st.error(t('load_project_error').format(project_name=project_name, e=e))

def delete_project(project_name):
    """Deletes the CSV file for a given project."""
    try:
        filepath = get_project_filepath(project_name)
        if os.path.exists(filepath):
            os.remove(filepath)
            st.success(t('project_deleted_success').format(project_name=project_name))
            return True
        else:
            st.warning(t('project_file_not_found_warning').format(project_name=project_name))
            return False
    except Exception as e:
        st.error(t('delete_project_error').format(e=e))
        return False

# ─────────────────────────────────────────────────────────────────────────────
# Helper & UI Rendering Functions
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Fetching market data...", ttl=3600)
def get_price_data(city: str) -> pd.DataFrame:
    """Generates mock market data based on the city name."""
    city_hash = hash(city.lower())
    base_construction = 1800 + (city_hash % 500)
    base_land = 5000 + (city_hash % 2000)
    data = {
        "Property Type": ["Small Plot (1200 sqft)", "Medium Plot (1800 sqft)", "Large Plot (2400 sqft)", "2BHK Flat (1100 sqft)", "3BHK Villa (2000 sqft)"],
        "Typical Price (₹)": [
            f"₹{(base_land * 1200) + (base_construction * 1000):,.0f}", 
            f"₹{(base_land * 1800) + (base_construction * 1500):,.0f}", 
            f"₹{(base_land * 2400) + (base_construction * 2000):,.0f}", 
            f"₹{6000000 + (city_hash % 2000000):,.0f}", 
            f"₹{12000000 + (city_hash % 4000000):,.0f}"
        ],
        "Land Price (₹/sqft)": [base_land, base_land + 500, base_land + 1000, "N/A", "N/A"],
        "Construction Cost (₹/sqft)": [base_construction, base_construction + 200, base_construction + 400, "N/A", "N/A"],
    }
    return pd.DataFrame(data)

def calculate_age(born: date) -> int:
    """Calculates age from a date object."""
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def render_flat_specifics():
    st.markdown(f"##### {t('flat_details_header')}")
    st.selectbox(t('flat_size_label'), ['1BHK', '2BHK', '3BHK', '4BHK+', 'Penthouse', 'Studio', 'Custom'], key='plan_flat_size')

def render_plot_specifics():
    st.markdown(f"##### {t('plot_details_header')}")
    st.number_input(t('plot_area_label'), min_value=300, value=1200, step=100, key='plan_plot_area')

def render_build_specifics():
    st.markdown(f"##### {t('construction_details_header')}")
    st.number_input(t('built_up_area_label'), min_value=200, value=1800, step=100, key='plan_built_up')
    st.number_input(t('floors_label'), min_value=1, value=2, key='plan_floors')
    st.checkbox(t('extra_floors_rent_checkbox'), key='extra_floors_rent')
    st.selectbox(t('contract_type_label'), ['With Material (Turnkey)', 'Without Material (Labor Only)'], key='const_contract')
    st.multiselect(t('vendors_label'), ['Plumbing', 'Electrical', 'Tiles', 'Paint', 'Solar', 'Interiors', 'CCTV', 'Automation', 'Landscaping'], key='const_vendors')
    st.multiselect(t('green_features_label'), ['Solar Panels', 'Rainwater Harvesting', 'Heat Insulation', 'EV Charging Point', 'Greywater Recycling'], key='const_green')
    st.slider(t('timeline_label'), 3, 36, 12, key='const_timeline')
    
def render_investment_specifics(purpose):
    if "Rental" in purpose or t('rental_income') in purpose:
        st.number_input(t('target_rent_label'), min_value=0, step=1000, key='fin_target_rent')
    if "Resale" in purpose or t('resale_investment') in purpose:
        st.number_input(t('target_resale_label'), min_value=0, step=100000, key='fin_target_resale')

# ─────────────────────────────────────────────────────────────────────────────
# Multi-Step UI Display Functions
# ─────────────────────────────────────────────────────────────────────────────

def display_sidebar():
    with st.sidebar:
        language_map = {lang_code: details['language_name'] for lang_code, details in TRANSLATIONS.items()}
        selected_language_name = st.selectbox(
            "Language / भाषा", 
            options=language_map.values(), 
            index=list(language_map.keys()).index(st.session_state.language)
        )
        # Find the language code corresponding to the selected name
        new_lang_code = next(code for code, name in language_map.items() if name == selected_language_name)
        if new_lang_code != st.session_state.language:
            st.session_state.language = new_lang_code
            st.rerun()

        st.title(f"🗂️ {t('project_manager_title')}")

        if st.session_state.selected_project:
            with st.container(border=True):
                st.caption(t('active_project_caption'))
                st.subheader(st.session_state.selected_project)
                if st.button(t('switch_project_button'), use_container_width=True):
                    st.session_state.selected_project = None
                    st.session_state.step = 0
                    st.rerun()
                with st.expander(t('danger_zone_header')):
                    if st.checkbox(t('delete_confirm_checkbox'), key="delete_confirm"):
                        if st.button(t('delete_project_button'), type="primary", use_container_width=True):
                            if delete_project(st.session_state.selected_project):
                                st.session_state.selected_project = None
                                st.session_state.step = 0
                                st.rerun()
            st.divider()

        with st.container(border=True):
            st.subheader(t('create_new_project_header'))
            with st.form("new_project_form"):
                new_project_name = st.text_input(t('new_project_name_label'), key="new_proj_name").strip()
                if st.form_submit_button(t('start_new_project_button'), use_container_width=True):
                    if new_project_name:
                        if new_project_name in get_saved_projects():
                            st.error(t('project_name_exists_error'))
                        else:
                            for key in CSV_COLUMNS: st.session_state.pop(key, None)
                            st.session_state.selected_project = new_project_name
                            st.session_state.step = 1
                            st.rerun()
                    else:
                        st.warning(t('enter_project_name_warning'))
        
        saved_projects = get_saved_projects()
        if saved_projects:
            with st.container(border=True):
                st.subheader(t('load_existing_project_header'))
                selected_to_load = st.selectbox(t('select_project_placeholder'), options=saved_projects, index=None, placeholder=t('select_project_placeholder'))
                if st.button(t('load_project_button'), use_container_width=True, disabled=not selected_to_load):
                    load_project(selected_to_load)
                    st.rerun()

        st.info(t('disclaimer_info'), icon="📢")

def display_step1_user_details():
    st.subheader(t('step1_header'))
    with st.form("user_details_form"):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input(t('full_name_label'), key='name')
            st.date_input(t('dob_label'), min_value=date(1940, 1, 1), max_value=date.today(), key='dob')
        with c2:
            st.text_input(t('contact_label'), key='contact')
            st.number_input(t('income_label'), min_value=100000, step=50000, key='income', format="%d")
        if st.form_submit_button(t('next_goal_button'), use_container_width=True, type="primary"):
            if all([st.session_state.name, st.session_state.contact, st.session_state.dob, st.session_state.income]):
                st.session_state.step = 2
                st.rerun()
            else:
                st.error(t('fill_all_details_error'))

def display_step2_intent():
    st.subheader(t('step2_header'))
    with st.form("intent_form"):
        intent_options = {
            'buy_flat': t('buy_flat'),
            'build_house': t('build_house'),
            'buy_plot': t('buy_plot'),
            'mixed_investment': t('mixed_investment')
        }
        st.session_state.intent_type_display = st.selectbox(t('select_goal_label'), options=list(intent_options.values()))
        if st.form_submit_button(t('next_specifics_button'), use_container_width=True, type="primary"):
            # Map back display name to a consistent key
            st.session_state.intent_type = next(key for key, value in intent_options.items() if value == st.session_state.intent_type_display)
            st.session_state.step = 3
            st.rerun()

def display_step3_details():
    intent_type_display = t(st.session_state.get('intent_type', 'buy_flat'))
    st.subheader(t('step3_header').format(intent_type=intent_type_display))
    
    with st.form("details_form"):
        st.markdown(f"#### {t('location_budget_header')}")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input(t('target_city_label'), key='loc_city')
            st.text_input(t('localities_label'), key='loc_locality')
        with c2:
            st.text_input(t('pincode_label'), max_chars=6, key='loc_pincode')
            st.number_input(t('budget_label'), min_value=100000, step=100000, key='fin_budget')
        c3, c4 = st.columns(2)
        with c3: st.checkbox(t('need_loan_checkbox'), key='fin_loan')
        with c4: st.checkbox(t('subsidy_checkbox'), key='fin_subsidy')
        
        purpose_options = {'self_use': t('self_use'), 'rental_income': t('rental_income'), 'resale_investment': t('resale_investment')}
        st.session_state.intent_purpose_display = st.selectbox(t('main_purpose_label'), options=list(purpose_options.values()))
        st.divider()
        
        components_to_render = []
        if st.session_state.intent_type == 'mixed_investment':
            mixed_options = {'buy_flat': t('buy_flat'), 'build_house': t('build_house'), 'buy_plot': t('buy_plot')}
            st.session_state.mixed_components_display = st.multiselect(t('mixed_components_label'), options=list(mixed_options.values()))
            components_to_render = [key for key, value in mixed_options.items() if value in st.session_state.mixed_components_display]
        else:
            components_to_render = [st.session_state.intent_type]
        
        if 'buy_flat' in components_to_render: render_flat_specifics()
        if any(c in components_to_render for c in ['build_house', 'buy_plot']): render_plot_specifics()
        if 'build_house' in components_to_render: render_build_specifics()
        
        st.divider()
        st.markdown(f"#### {t('preferences_concerns_header')}")
        c5, c6 = st.columns(2)
        with c5:
            st.select_slider(t('connectivity_label'), ['Low', 'Medium', 'High'], key='qual_connectivity')
            st.select_slider(t('amenities_label'), ['Not Important', 'Somewhat', 'Very Important'], key='qual_amenities')
        with c6:
            st.select_slider(t('pollution_label'), ['Low', 'Medium', 'High'], key='risk_pollution')
            st.select_slider(t('crime_label'), ['Low', 'Medium', 'High'], key='risk_crime')
        
        if st.session_state.intent_purpose_display in [t('rental_income'), t('resale_investment')]:
            st.markdown(f"##### {t('investment_goals_header')}")
            render_investment_specifics(st.session_state.intent_purpose_display)
        
        if st.form_submit_button(t('save_proceed_button'), use_container_width=True, type="primary"):
            st.session_state.intent_purpose = next(key for key, value in purpose_options.items() if value == st.session_state.intent_purpose_display)
            if 'mixed_components_display' in st.session_state:
                st.session_state.mixed_components = components_to_render
            if save_project():
                st.session_state.step = 4
                st.rerun()

def display_step4_analysis():
    st.subheader(t('step4_header'))
    st.success(t('project_saved_success'))
    
    project_details = {key: st.session_state.get(key) for key in CSV_COLUMNS if st.session_state.get(key)}
    
    with st.expander(t('view_details_expander')):
        display_details = {key.replace('_', ' ').title(): val for key, val in project_details.items() if val and key != 'project_name'}
        st.json(display_details)

    st.divider()
    city = project_details.get('loc_city', "Your City")
    st.subheader(t('market_snapshot_header').format(city=city.title()))
    st.dataframe(get_price_data(city), use_container_width=True, hide_index=True)
    st.divider()

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button(t('generate_strategy_button'), type="primary", use_container_width=True):
            prompt = build_initial_prompt(project_details, st.session_state.language)
            with st.spinner(t('analyzing_spinner')):
                st.session_state.ai_response = ask_gemini(prompt)
            st.session_state.follow_up_response = None
    with col2:
        if st.button(t('edit_details_button'), use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    if st.session_state.get('ai_response'):
        st.markdown("---")
        st.subheader(t('strategy_header'))
        st.markdown(st.session_state.ai_response, unsafe_allow_html=True)
        st.markdown("---")
        with st.expander(t('follow_up_expander')):
            question = st.text_area(t('follow_up_expander'), placeholder=t('follow_up_placeholder'))
            if st.button(t('ask_gemini_button')):
                if question:
                    prompt = build_follow_up_prompt(project_details, st.session_state.ai_response, question, st.session_state.language)
                    with st.spinner(t('thinking_spinner')):
                        st.session_state.follow_up_response = ask_gemini(prompt, temperature=0.5)
                else:
                    st.warning(t('enter_question_warning'))
        if st.session_state.get('follow_up_response'):
            st.info(st.session_state.follow_up_response)

# ─────────────────────────────────────────────────────────────────────────────
# AI Prompt Engineering Functions
# ─────────────────────────────────────────────────────────────────────────────

def build_initial_prompt(details, lang_code):
    language_name = TRANSLATIONS[lang_code]['language_name']
    dob_obj = details.get('dob')
    age_str = calculate_age(dob_obj) if isinstance(dob_obj, date) else "N/A"
    income_val = int(details.get('income', 0))
    budget_val = int(details.get('fin_budget', 0))
    city = details.get('loc_city', 'your city')

    client_profile = f"""
        **CLIENT'S BASE PROFILE:**
        - Name: {details.get('name', 'User')}
        - Age: {age_str} years
        - Annual Income: ₹{income_val:,}
        - Primary Goal: {details.get('intent_type', 'N/A')}
        - Main Purpose: {details.get('intent_purpose', 'N/A')}
        - Target City: {city}
        - Total Budget: ₹{budget_val:,}
        - Needs Loan: {'Yes' if details.get('fin_loan') else 'No'}
    """

    return textwrap.dedent(f"""
        Act as a meticulous financial real estate analyst in India. Your primary goal is to provide a report that is 85% quantitative data, in clear Markdown tables.
        IMPORTANT: Your entire response, including all headers, table content, and text, MUST be in the {language_name} language.

        {client_profile}

        **MARKET DATA for {city}:**
        {get_price_data(city).to_markdown(index=False)}

        ---
        **YOUR TASK: Generate a detailed, number-focused financial report in Markdown with these strict sections. Base all calculations on the client's profile and market data.**

        ### 1. Financial Snapshot
        - **Total Estimated Project Cost:** (Use client's budget)
        - **Down Payment (20%):**
        - **Loan Amount (80%):**
        - **Estimated EMI:** (Assume 20-year loan at 8.7% interest)
        - **EMI as % of Monthly Income:**

        ### 2. Detailed Cost Breakdown (Table)
        Create a table itemizing costs based on the Total Project Cost.
        | Item | Amount (₹) | Notes |
        |---|---|---|
        | Base Property Cost | | Budget minus other fees |
        | Stamp Duty & Registration (est. 7%) | | |
        | Brokerage (if applicable, est. 1%) | | |
        | Interiors/Furnishing (est. 10%) | | |
        | Contingency Fund (5%) | | For unexpected expenses |
        | **Total Estimated Project Cost** | **₹{budget_val:,}** | **Matches client budget** |

        ### 3. Loan Amortization Schedule (Table)
        Show the schedule for a 20-year term. Show years 1, 2, 3, 4, 5, 10, 15, and 20.
        | Year | Principal Paid (₹) | Interest Paid (₹) | Annual Payment (₹) | Remaining Balance (₹) |
        |---|---|---|---|---|
        | 1 | | | | |
        | 2 | | | | |
        | 3 | | | | |
        | 4 | | | | |
        | 5 | | | | |
        | 10 | | | | |
        | 15 | | | | |
        | 20 | | | | |

        ### 4. Future Value & Equity Projections (Table)
        Project the property's value assuming a 6% annual appreciation.
        | Year | Projected Value (₹) | Total Equity (Value - Loan Balance) |
        |---|---|---|
        | 2 | | |
        | 5 | | |
        | 10 | | |
        | 15 | | |
        | 20 | | |

        ### 5. Rental Income Analysis (if purpose is Rental)
        **Only include this section if purpose is 'Rental Income'.**
        - **Target Monthly Rent:** ₹{int(details.get('fin_target_rent', 0)):,}
        - **Gross Annual Rent:**
        - **Less Expenses (30%):** (Property Tax, Maintenance, Insurance)
        - **Net Operating Income (NOI):**
        - **Capitalization (Cap) Rate:** (NOI / Total Project Cost)
        - **Recommendation:** Briefly state if the rental yield seems viable.

        ### 6. Summary & Next Steps
        Provide a friendly closing summary and a short, actionable checklist of next steps.
    """)

def build_follow_up_prompt(details, initial_report, question, lang_code):
    language_name = TRANSLATIONS[lang_code]['language_name']
    return textwrap.dedent(f"""
        You are a real estate financial analyst continuing a conversation. You already provided a detailed financial report. Now, answer a follow-up question.
        IMPORTANT: Your entire answer MUST be in the {language_name} language.

        **CONTEXT: YOUR PREVIOUS REPORT (which was in {language_name})**
        ---
        {initial_report}
        ---

        **CLIENT'S FOLLOW-UP QUESTION:**
        "{question}"

        **YOUR TASK:**
        Answer the question concisely in {language_name}. Base your answer on the report's data. If it requires a new calculation (e.g., "what if interest is 9%?"), perform it and show the result. Do not repeat large parts of the report.
    """)

# ─────────────────────────────────────────────────────────────────────────────
# Main App Controller
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="AI Real Estate Advisor", page_icon="🏠", layout="wide")
    
    # Initialize session state keys
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    defaults = {
        'step': 0, 'selected_project': None, 'ai_response': None, 'follow_up_response': None,
        'name': '', 'contact': '', 'dob': date(2000, 1, 1), 'income': 1000000,
        'intent_type': 'buy_flat', 'intent_purpose': 'self_use', 'loc_city': 'Nagpur', 
        'loc_locality': '', 'loc_pincode': '', 'fin_budget': 5000000, 'fin_loan': True, 
        'fin_subsidy': False, 'mixed_components': [], 'plan_flat_size': '2BHK', 
        'plan_plot_area': 1200, 'plan_built_up': 1800, 'plan_floors': 1,
        'extra_floors_rent': False, 'const_contract': 'With Material (Turnkey)', 'const_vendors': [],
        'const_green': [], 'const_timeline': 12, 'qual_connectivity': 'Medium', 'qual_amenities': 'Somewhat',
        'risk_pollution': 'Low', 'risk_crime': 'Low', 'fin_target_rent': 0, 'fin_target_resale': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    display_sidebar()
    st.title(f"🏠 {t('app_title')}")

    if not st.session_state.selected_project:
        st.info(t('welcome_message'))
    else:
        st.markdown(t('current_project_header').format(project_name=st.session_state.selected_project))
        st.divider()
        
        if st.session_state.step == 1: display_step1_user_details()
        elif st.session_state.step == 2: display_step2_intent()
        elif st.session_state.step == 3: display_step3_details()
        elif st.session_state.step == 4: display_step4_analysis()

if __name__ == "__main__":
    main()
