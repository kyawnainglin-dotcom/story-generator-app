import streamlit as st
import google.generativeai as genai
import random
import time

# --- Page Config ---
st.set_page_config(page_title="AI Director Master Shot-List Studio", layout="wide")

# --- Custom CSS Stylesheet with Black Cursor Fix ---
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
    
    /* 4. Translucent Input Box & Cursor Black Color Fix (Caret Color) */
    .stTextInput > div > div > input {
        border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.95);
        color: #0f172a !important;
        border: 2px solid #334155;
        padding: 14px 20px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        caret-color: #000000 !important; /* Cursor Black */
    }
    .stTextInput > div > div > input::placeholder {
        color: #475569 !important;
        opacity: 1 !important;
    }
    .stTextInput > div > div > input:focus {
        border: 2px solid #1e40af;
        box-shadow: 0 0 12px rgba(30, 64, 175, 0.25);
        caret-color: #000000 !important; /* Cursor Black */
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
    
    /* 7. Editable Text Area Design Upgrades with Black Cursor */
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.98) !important;
        color: #0f172a !important;
        font-size: 12pt !important;
        line-height: 1.8 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        caret-color: #000000 !important; /* Cursor Black */
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Session State Initialize
if "generated_script" not in st.session_state:
    st.session_state.generated_script = ""

# --- Sidebar Production Panel ---
st.sidebar.markdown("<h2 style='font-size: 22px;'>⚙️ Production Settings</h2>", unsafe_allow_html=True)
story_language = st.sidebar.radio("Output Language", ["Myanmar", "English"])
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# Duration Sliders
st.sidebar.markdown("<label>Target Video Duration</label>", unsafe_allow_html=True)
duration_min = st.sidebar.slider("Minutes", 0, 10, 1)
duration_sec = st.sidebar.slider("Seconds", 0, 50, 0, step=10)
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# Character Consistency
st.sidebar.markdown("<label>🎭 Character Reference Profile</label>", unsafe_allow_html=True)
char_profile = st.sidebar.text_area(label="Character Description", placeholder="မင်းသား: ၂၅ နှစ်ခန့်၊ ဆံပင်အညို၊ ဂျင်းဂျာကင်...", height=80, label_visibility="collapsed")
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

story_type = st.sidebar.selectbox("Genre", ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"])
art_style = st.sidebar.selectbox("Art Style", ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"])
image_ratio = st.sidebar.selectbox("Midjourney Ratio", ["16:9", "9:16", "4:3", "1:1"])

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get Free API Key](https://aistudio.google.com)")

# --- Main Interface ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Director's Master Script & Shot Board")
st.markdown("<div class='sub-text'>Professional Scene Splitter & Prompt Sync Engine</div>", unsafe_allow_html=True)

story_concept = st.text_input("", placeholder="ဇတ်လမ်းအကျဉ်း သို့မဟုတ် အိုင်ဒီယာ ရေးရန်")

if st.button("Generate Production Board"):
    if not user_api_key:
        st.error("API Key လိုအပ်ပါသည်။")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            # 🚀 HIGH CREATIVITY SETTINGS - Prevents Duplicate Plots Completely
            generation_config = {
                "temperature": 0.95,  # Increased for maximum narrative variation
                "top_p": 0.95,
                "top_k": 50
            }
            
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config=generation_config)
            
            total_seconds = (duration_min * 60) + duration_sec
            
            # Generate a truly unpredictable seed & time-based key to force unique responses
            random_seed = random.randint(1, 999999)
            timestamp_key = int(time.time())
            
            # --- Handle Style Filter Overrides ---
            if "Disney" in art_style:
                mj_ver = ""
                img_style = "3D Pixar Disney Animation Style, Vibrant Clay Render, Smooth Shading, Raytracing, Cute Character Design"
                vid_style = "Disney Pixar Animation Style, Smooth 3D Motion, Whimsical Feel"
            elif "Anime" in art_style:
                mj_ver = "--niji 6"
                img_style = "Anime Key Visual, Sharp Lineart, Vibrant Colors, Cel Shaded"
                vid_style = "Anime Shinkai Style Motion, Fluent 2D Animation"
            else:
                mj_ver = "--v 6.0"
                img_style = "Cinematic Still, Film Grain, --style raw"
                vid_style = "Cinematic Movie Style, Photorealistic, 8k Resolution, Masterpiece"
            
            # 🧠 Master Orchestrated Prompt Structure with Dynamic System Randomizers
            command = f"""
            [SYSTEM RANDOMIZER KEY: {random_seed}-{timestamp_key}]
            CRITICAL INSTRUCTION: You MUST create a completely fresh, unique, and unpredictable story plot line. Do NOT recycle or use standard cliche story paths. 
            
            You are a Legendary Screenplay Writer and Hollywood Film Director. 
            Generate a comprehensive production document according to the following strict layout.
            
            [Specifications]
            1. Target Duration: {duration_min}m {duration_sec}s.
            2. Genre: {story_type} | Style: {art_style}
            3. Language: Native text (Title, Story, Overview, Narration, Action, Dialogue) must be in {story_language}.
            4. Plot Base/Concept: '{story_concept if story_concept else "Generate a completely random epic concept from scratch based on the selected Genre."}' 
            5. Character Reference: '{char_profile}'
            
            [Pacing Rules]
            - Landscape/Establishing: 5-7s. 
            - Action/Dialogue: 1-3s.
            
            [OUTPUT LAYOUT - FOLLOW STRICTLY]
            
            📌 STORY TITLE
            📖 FULL STORY
            🎬 SCRIPT & STORY OVERVIEW
            🎭 CHARACTER PROMPTS
            🎬 SCENE & SHOT BREAKDOWN
            
            For each SCENE block:
            🎬 SCENE [Number]: [Location]
            🎙️ NARRATION: [Text in {story_language}]
            
            List of Shots:
              * SHOT [Scene Number].[Shot Number] - [Duration: X Seconds]
              * Camera Shot Type: [Type]
              * Action Description: [Myanmar Description]
              * 👥 DIALOGUE: [Character Name]: "[Dialogue in {story_language}]"
              
              * Image Prompt: [Subject Description] in [Setting/Atmosphere], [Framing] with [Lens], [Lighting Type], [Color Palette], {img_style} --ar {image_ratio} {mj_ver}
              
              * Video Prompt & Direction: [Cinematic Camera Movement (e.g. Slow Dolly In, Fast Tracking, Crane Shot)], [Subject description + Kinetic Action matching the 'Action Description' above], [Environment with dynamic elements like blowing leaves, rain, or flickering neon], [Lighting & Color Palette], {vid_style}
              
              * Sound Style & Music Mood: [English Description]
            """
            
            with st.spinner("⚡ Director AI is brainstorming an entirely new custom plot..."):
                response = model.generate_content(command)
                st.session_state.generated_script = response.text
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

# --- Editable Board ---
if st.session_state.generated_script:
    st.markdown("<br><hr/>", unsafe_allow_html=True)
    st.markdown("### 🎬 Director's Production Board (Editable)")
    edited_script = st.text_area(label="Master Board", value=st.session_state.generated_script, height=600, label_visibility="collapsed")
    st.download_button(label="📥 Download Master Script", data=edited_script, file_name=f"master_{story_type.lower()}.txt")

st.markdown("</div>", unsafe_allow_html=True)
