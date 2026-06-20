import streamlit as st
import google.generativeai as genai
import random

# --- Page Config ---
st.set_page_config(page_title="AI Director Master Shot-List Studio", layout="wide")

# --- Custom CSS Stylesheet ---
custom_css = """
<style>
    /* 1. Raw Background Photo - High Clarity */
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* 2. Content Layout Top Spacing */
    .main-content { padding-top: 30vh; }
    
    /* 3. Deep Dark Contrast Typography */
    h1 { color: #0f172a !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }
    .sub-text { text-align: center; color: #1e293b; font-size: 16px; margin-bottom: 25px; letter-spacing: 0.5px; font-weight: 700; }
    
    /* 4. Translucent Input Box & Placeholder Color Fix */
    .stTextInput > div > div > input {
        border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.95);
        color: #0f172a !important;
        border: 2px solid #334155;
        padding: 14px 20px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .stTextInput > div > div > input::placeholder {
        color: #475569 !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus {
        border: 2px solid #1e40af;
        box-shadow: 0 0 12px rgba(30, 64, 175, 0.25);
    }
    
    /* 5. Sleek Full-Width Action Button */
    div.stButton > button {
        background: linear-gradient(45deg, #0f172a, #1e40af);
        color: white !important;
        font-weight: bold;
        font-size: 16px;
        border-radius: 25px;
        width: 100% !important;
        border: none;
        padding: 14px 30px !important;
        display: block;
        margin: 0 auto;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(15, 23, 42, 0.2);
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #1e40af, #2563eb);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35);
        transform: translateY(-2px);
    }
    
    /* 6. Luxury Deep Navy Blue Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important; 
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] .stMarkdown h2 { color: #ffbc00 !important; font-weight: bold; letter-spacing: 0.5px; }
    [data-testid="stSidebar"] label { color: #f8fafc !important; font-weight: 600 !important; font-size: 14px !important; }
    [data-testid="stSidebar"] .stCheckbox p { color: #f8fafc !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] .stRadio div { color: #f8fafc !important; }
    
    /* 7. Editable Text Area Design Upgrades */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.98) !important;
        color: #0f172a !important;
        font-size: 12pt !important;
        line-height: 1.8 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Session State Initialize
if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""

# --- ⚙️ Sidebar Navigation Panel ---
st.sidebar.markdown("<h2 style='font-size: 22px;'>⚙️ Production Settings</h2>", unsafe_allow_html=True)

story_language = st.sidebar.radio(
    "Output Language",
    ["Myanmar", "English"]
)

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# Target Duration Sliders
st.sidebar.markdown("<label>Target Video Duration</label>", unsafe_allow_html=True)
duration_min = st.sidebar.slider("Minutes", 0, 10, 1)
duration_sec = st.sidebar.slider("Seconds", 0, 50, 0, step=10)

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# Character Profiles for Consistency
st.sidebar.markdown("<label>🎭 Character Reference Profile</label>", unsafe_allow_html=True)
char_profile = st.sidebar.text_area(
    label="Character Description",
    placeholder="ဥပမာ- 'မင်းသား: အသက် ၂၅ နှစ်ခန့်၊ ဆံပင်အညိုကောက်ကောက်၊ ဂျင်းဂျာကင်အပြာ ဝတ်ဆင်ထားသည်။'",
    height=80,
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

story_type = st.sidebar.selectbox(
    "Genre / Story Type",
    ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"]
)

art_style = st.sidebar.selectbox(
    "Visual Art Style",
    ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"]
)

image_ratio = st.sidebar.selectbox("Midjourney Ratio (--ar)", ["16:9", "9:16", "4:3", "1:1"])

st.
