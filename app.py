import streamlit as st
import google.generativeai as genai
import random
import time
import re

# --- Page Config ---
st.set_page_config(page_title="AI Director Master Shot-List Studio", layout="wide")

# --- Custom CSS Stylesheet (Fixed Mobile Height & Black Screen Issue) ---
custom_css = """
<style>
    .stApp {
        background-image: url('https://w0.peakpx.com/wallpaper/705/104/HD-wallpaper-anime-girls-playing-games-bed-short-hair-blond.jpg');
        background-size: cover; 
        background-position: center top; 
        background-attachment: fixed;
    }
    
    .main-content { 
        padding: 15px; 
        background-color: rgba(15, 23, 42, 0.7); 
        border-radius: 16px;
        margin-top: 10px;
    }
    
    h1 { 
        color: #ffffff !important; 
        text-align: center; 
        font-family: 'Helvetica Neue', sans-serif; 
        font-weight: 800; 
        letter-spacing: 1px; 
        margin-bottom: 5px; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
    }
    .sub-text { 
        text-align: center; 
        color: #ffbc00 !important; 
        font-size: 16px; 
        margin-bottom: 25px; 
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
secondary_type = st.sidebar.selectbox("Secondary Genre (Optional Combo)", ["None", "Action", "Drama", "Thriller", "Comedy", "Romance", "Mystery"])
art_style = st.sidebar.selectbox("Art Style", ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"])
image_ratio = st.sidebar.selectbox("Midjourney Ratio", ["16:9", "9:16", "4:3", "1:1"])

# Persistent Project Reset Button in Sidebar
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
if st.sidebar.button("🔄 Start Entire New Project", type="secondary"):
    st.session_state.story_stage = "input"
    st.session_state.approved_story = ""
    st.session_state.extracted_scenes = []
    st.session_state.scene_boards = {}
    st.rerun()

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- Main Interface Wrapper ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Director's Master Script & Shot Board")
st.markdown("<div class='sub-text'>Dialogue, Action & Time-Synced Production Suite</div>", unsafe_allow_html=True)

st.caption(f"**Current Workspace Status:** Active Stage - `{st.session_state.story_stage.upper()}`")

# --- STEP 1: GENERATE SCREENPLAY SCRIPT ---
if st.session_state.story_stage == "input":
    story_concept = st.text_input("Story Concept", placeholder="ဇတ်လမ်းအကျဉ်း (ဘာမှမရေးဘဲ နှိပ်ပါက AI က ဂျန်ရာအလိုက် အလိုအလျောက် ကြံဆပေးမည်)", label_visibility="collapsed")
    total_target_seconds = (duration_min * 60) + duration_sec
    
    if st.button("Step 1: Brainstorm Master Screenplay"):
        if not user_api_key: st.error("API Key လိုအပ်ပါသည်။")
        elif total_target_seconds == 0: st.error("ကျေးဇူးပြု၍ အချိန်တစ်ခု သတ်မှတ်ပေးပါဗျာ။")
        else:
            try:
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.95})
                
                max_attempts = 5
                attempt = 0
                passed_gate = False
                status_box = st.empty()
                combo_genre = story_type if secondary_type == "None" else f"{story_type} + {secondary_type}"
                
                concept_clause = f"based on this raw user concept: '{story_concept}'" if story_concept.strip() else f"based completely on your own highly original and creative brainstormed premise for the selected genre context."
                
                if total_target_seconds <= 60: length_instruction = "SHORT SCREENPLAY. 1-2 distinct scenes with immediate action, punchy characters dialogues, and a sharp plot twist."
                elif total_target_seconds <= 300: length_instruction = "MEDIUM SCREENPLAY. 3-4 structured dramatic scenes with deep character interactions, character physical movements, and high-stakes dialogues."
                else: length_instruction = f"EPIC MULTI-ACT SCRIPT. A highly detailed multi-scene screenplay timeline with dense situational character action, dialogue exchanges, and world-building blocks tailored for {duration_min} minutes."

                while attempt < max_attempts and not passed_gate:
                    attempt += 1
                    status_box.markdown(f"🧠 **AI Director (Script Loop {attempt}/{max_attempts}):** Designing Screenplay & Dialogues...")
                    
                    story_command = f"""
                    Write a theatrical movie script/screenplay {concept_clause}. 
                    Genre: {combo_genre}. Language: Write in {story_language}.
                    Constraint: Script scale must follow: {length_instruction}.
                    
                    CRITICAL REQUIREMENT: Do NOT write like a storybook/prose. Write it as an interactive screenplay script containing active physical CHARACTER ACTIONS and explicit DIALOGUES between characters.
                    
                    Evaluate yourself at the end within these tags:
                    CRITIQUE_START
                    Plot Twist Score: [1-10]
                    Emotional Depth Score: [1-10]
                    Reasoning: [One sentence in English]
                    CRITIQUE_END
                    
                    Structure:
                    📌 SCRIPT TITLE: [Title]
                    📖 FULL SCREENPLAY: [Write utilizing explicit scene headings, character action lines, and character dialogues]
                    """
                    response = model.generate_content(story_command)
                    res_text = response.text
                    
                    twist_s = int(re.search(r"Plot Twist Score:\s*(\d+)", res_text).group(1)) if re.search(r"Plot Twist Score:\s*(\d+)", res_text) else 5
                    depth_s = int(re.search(r"Emotional Depth Score:\s*(\d+)", res_text).group(1)) if re.search(r"Emotional Depth Score:\s*(\d+)", res_text) else 5
                    reason = re.search(r"Reasoning:\s*(.*)", res_text).group(1) if re.search(r"Reasoning:\s*(.*)", res_text) else "Standard."
                    final_rating = (twist_s + depth_s) / 2.0
                    
                    if final_rating >= 7.0:
                        passed_gate = True
                        st.session_state.approved_story = re.sub(r"CRITIQUE_START.*?CRITIQUE_END", "", res_text, flags=re.DOTALL).strip()
                        st.session_state.story_analysis = {"rating": final_rating, "twist": twist_s, "depth": depth_s, "reason": reason, "genre": combo_genre}
                        st.session_state.story_stage = "story_ready"
                        break
                    time.sleep(0.3)
                
                status_box.empty()
                if not passed_gate:
                    st.session_state.approved_story = re.sub(r"CRITIQUE_START.*?CRITIQUE_END", "", res_text, flags=re.DOTALL).strip()
                    st.session_state.story_analysis = {"rating": final_rating, "twist": twist_s, "depth": depth_s, "reason": "Fallback.", "genre": combo_genre}
                    st.session_state.story_stage = "story_ready"
                st.rerun()
            except Exception as e: st.error(f"Error: {str(e)}")

# --- DISPLAY SCREENPLAY & SCENE CHUNKER ---
if st.session_state.story_stage in ["story_ready", "scenes_extracted"]:
    analysis = st.session_state.story_analysis
    st.markdown(f"""
    <div class="critique-card">
        <h4 style="color: #ffbc00; margin-top:0;">🛡️ AI Director Critic Board</h4>
        <p><b>🎭 Genre:</b> {analysis['genre']} | <b>⏱️ Duration:</b> {duration_min}m {duration_sec}s | <b>⭐ IMDb Rating:</b> {analysis['rating']}/10</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: white;'>📖 Approved Screenplay Script</h3>", unsafe_allow_html=True)
