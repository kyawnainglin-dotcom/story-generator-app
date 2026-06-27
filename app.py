import streamlit as st
import google.generativeai as genai
import random
import time
import re

# --- Page Config ---
st.set_page_config(page_title="AI Director Master Shot-List Studio", layout="wide")

# --- Custom CSS Stylesheet (With Image Background & Text Visibility Fixes) ---
custom_css = """
<style>
    .stApp {
        background-image: url('https://w0.peakpx.com/wallpaper/705/104/HD-wallpaper-anime-girls-playing-games-bed-short-hair-blond.jpg');
        background-size: cover; 
        background-position: center; 
        background-attachment: fixed;
    }
    .main-content { padding-top: 25vh; }
    
    /* Titles with high contrast text-shadow for dark/complex backgrounds */
    h1 { 
        color: #ffffff !important; 
        text-align: center; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-weight: 800; 
        letter-spacing: 1px; 
        margin-bottom: 5px; 
        text-shadow: 3px 3px 6px rgba(0,0,0,0.9), -1px -1px 0 rgba(0,0,0,0.9), 1px -1px 0 rgba(0,0,0,0.9), -1px 1px 0 rgba(0,0,0,0.9), 1px 1px 0 rgba(0,0,0,0.9);
    }
    .sub-text { 
        text-align: center; 
        color: #ffbc00 !important; 
        font-size: 18px; 
        margin-bottom: 25px; 
        letter-spacing: 0.5px; 
        font-weight: 700; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px; background-color: rgba(255, 255, 255, 0.95);
        color: #0f172a !important; border: 2px solid #334155; padding: 14px 20px; font-weight: 600; caret-color: #000000 !important;
    }
    
    div.stButton > button {
        background: linear-gradient(45deg, #0f172a, #1e40af); color: white !important;
        font-weight: bold; font-size: 15px; border-radius: 25px; width: 100% !important; border: none; padding: 12px 25px !important; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background: linear-gradient(45deg, #1e40af, #2563eb); transform: translateY(-1px); }
    
    /* Mobile Safe Danger/Reset Button */
    div.stButton > button[data-testid="baseButton-secondary"] {
        background: linear-gradient(45deg, #7f1d1d, #b91c1c) !important; color: white !important;
    }
    
    [data-testid="stSidebar"] { background-color: rgba(15, 23, 42, 0.95) !important; border-right: 1px solid #1e293b; }
    [data-testid="stSidebar"] .stMarkdown h2 { color: #ffbc00 !important; font-weight: bold; }
    [data-testid="stSidebar"] label { color: #f8fafc !important; font-weight: 600 !important; }
    
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.98) !important; color: #0f172a !important;
        font-size: 11pt !important; line-height: 1.7 !important; border: 2px solid #cbd5e1 !important; border-radius: 12px !important; padding: 15px !important; caret-color: #000000 !important;
    }
    
    .critique-card { background-color: rgba(15, 23, 42, 0.9); border: 2px solid #ffbc00; border-radius: 12px; padding: 20px; margin-bottom: 20px; color: #f8fafc; }
    .scene-box { background-color: rgba(255, 255, 255, 0.95); border-left: 5px solid #1e40af; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #0f172a; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Session State Management ---
if "story_stage" not in st.session_state: st.session_state.story_stage = "input"
if "approved_story" not in st.session_state: st.session_state.approved_story = ""
if "story_analysis" not in st.session_state: st.session_state.story_analysis = {}
if "extracted_scenes" not in st.session_state: st.session_state.extracted_scenes = []
if "scene_boards" not in st.session_state: st.session_state.scene_boards = {}

# --- Sidebar Panel ---
st.sidebar.markdown("<h2 style='font-size: 22px;'>⚙️ Production Settings</h2>", unsafe_allow_html=True)
story_language = st.sidebar.radio("Output Language", ["Myanmar", "English"])
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

st.sidebar.markdown("<label>⏰ Target Video Duration</label>", unsafe_allow_html=True)
col_min, col_sec = st.sidebar.columns(2)
with col_min: duration_min = st.number_input("Minutes (Max 40)", min_value=0, max_value=40, value=1, step=1)
with col_sec: duration_sec = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=5)
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

st.sidebar.markdown("<label>🎭 Character Reference Profile (Locked for Prompts)</label>", unsafe_allow_html=True)
char_profile = st.sidebar.text_area(label="Char Profile", placeholder="e.g., A 25-year-old man, brown hair, wearing a rugged blue denim jacket...", height=100, label_visibility="collapsed")
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

story_type = st.sidebar.selectbox("Primary Genre", ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"])
secondary_type = st
