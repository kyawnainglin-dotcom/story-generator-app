import streamlit as st
import google.generativeai as genai
import random
import time
import re

# --- Page Config ---
st.set_page_config(page_title="AI Director Master Shot-List Studio", layout="wide")

# --- Custom CSS Stylesheet ---
custom_css = """
<style>
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main-content { padding-top: 30vh; }
    h1 { color: #0f172a !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }
    .sub-text { text-align: center; color: #1e293b; font-size: 16px; margin-bottom: 25px; letter-spacing: 0.5px; font-weight: 700; }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        background-color: rgba(255, 255, 255, 0.95);
        color: #0f172a !important;
        border: 2px solid #334155;
        padding: 14px 20px;
        font-size: 16px;
        font-weight: 600;
        caret-color: #000000 !important;
    }
    
    /* Number Input Custom Styling */
    .stNumberInput div div input {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #0f172a !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        caret-color: #000000 !important;
    }
    
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
    }
    
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
    [data-testid="stSidebar"] .stMarkdown h2 { color: #ffbc00 !important; font-weight: bold; }
    [data-testid="stSidebar"] label { color: #f8fafc !important; font-weight: 600 !important; }
    [data-testid="stSidebar"] .stRadio div { color: #f8fafc !important; }
    
    .stTextArea textarea {
        background-color: rgba(255, 255, 255, 0.98) !important;
        color: #0f172a !important;
        font-size: 12pt !important;
        line-height: 1.8 !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        caret-color: #000000 !important;
    }
    
    .critique-card {
        background-color: rgba(15, 23, 42, 0.9);
        border: 2px solid #ffbc00;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        color: #f8fafc;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Session State Management ---
if "story_stage" not in st.session_state:
    st.session_state.story_stage = "input"
if "approved_story" not in st.session_state:
    st.session_state.approved_story = ""
if "story_analysis" not in st.session_state:
    st.session_state.story_analysis = {}
if "final_production_board" not in st.session_state:
    st.session_state.final_production_board = ""

# --- Sidebar Production Panel ---
st.sidebar.markdown("<h2 style='font-size: 22px;'>⚙️ Production Settings</h2>", unsafe_allow_html=True)
story_language = st.sidebar.radio("Output Language", ["Myanmar", "English"])
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# Typing Number Inputs instead of Sliders (Up to 40 Minutes)
st.sidebar.markdown("<label>⏰ Target Video Duration</label>", unsafe_allow_html=True)
col_min, col_sec = st.sidebar.columns(2)
with col_min:
    duration_min = st.number_input("Minutes (Max 40)", min_value=0, max_value=40, value=1, step=1)
with col_sec:
    duration_sec = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=5)

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

# Character Consistency
st.sidebar.markdown("<label>🎭 Character Reference Profile</label>", unsafe_allow_html=True)
char_profile = st.sidebar.text_area(label="Character Profile", placeholder="မင်းသား: ၂၅ နှစ်ခန့်၊ ဆံပင်အညို၊ ဂျင်းဂျာကင်...", height=80, label_visibility="collapsed")
st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

story_type = st.sidebar.selectbox("Primary Genre", ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"])
secondary_type = st.sidebar.selectbox("Secondary Genre (Optional Combo)", ["None", "Action", "Drama", "Thriller", "Comedy", "Romance", "Mystery"])

art_style = st.sidebar.selectbox("Art Style", ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"])
image_ratio = st.sidebar.selectbox("Midjourney Ratio", ["16:9", "9:16", "4:3", "1:1"])

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- Main Interface ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Director's Master Script & Shot Board")
st.markdown("<div class='sub-text'>Two-Step High-Capacity AI Production Suite</div>", unsafe_allow_html=True)

story_concept = st.text_input("", placeholder="ဇတ်လမ်းအကျဉ်း သို့မဟုတ် အိုင်ဒီယာ ရေးရန်")

# Total Targeted Seconds Calculation
total_target_seconds = (duration_min * 60) + duration_sec

# --- STEP 1: GENERATE & VERIFY STORY BASED ON TIME ---
if st.session_state.story_stage == "input":
    if st.button("Step 1: Brainstorm Master Story"):
        if not user_api_key:
            st.error("API Key လိုအပ်ပါသည်။")
        elif total_target_seconds == 0:
            st.error("ကျေးဇူးပြု၍ မိနစ် သို့မဟုတ် စက္ကန့် အနည်းဆုံးတစ်ခု ထည့်ပေးပါဗျာ။")
        else:
            try:
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"temperature": 0.95, "top_p": 0.95})
                
                max_attempts = 5
                attempt = 0
                passed_gate = False
                status_box = st.empty()
                combo_genre = story_type if secondary_type == "None" else f"{story_type} + {secondary_type}"
                
                # Extended Pacing Logic for Long Formats up to 40 Mins
                if total_target_seconds <= 60:
                    length_instruction = "SHORT & CRISP. Max 1-2 concise paragraphs. Total words around 130-150 words. Focus heavily on one immediate plot twist."
                elif total_target_seconds <= 300:
                    length_instruction = "MEDIUM LENGTH. 3-4 structured paragraphs. Total words around 400-600 words. Good build-up with a solid twist."
                elif total_target_seconds <= 900:
                    length_instruction = f"LONG FORMAT SCRIPT ({duration_min} Mins). Multi-paragraph structured act layout. Word count around 1200-1500 words. Build profound narrative depth."
                else:
                    length_instruction = f"EPIC LONG FEATURE FORMAT. Massive chronicle with extensive scene notes, divided into explicit story parts or acts. Word count must be highly detailed up to 2500-3500 words to comprehensively support a full {duration_min}-minute presentation. Include deep multi-layered plots and dynamic character shifts."

                while attempt < max_attempts and not passed_gate:
                    attempt += 1
                    status_box.markdown(f"🧠 **AI Director (Story Tuning Loop {attempt}/{max_attempts}):** Tailoring script pacing for {duration_min}m {duration_sec}s...")
                    st.toast(f"Scaling Narrative Canvas to {duration_min} Minutes...")
                    
                    random_seed = random.randint(1, 999999)
                    story_command = f"""
                    You are a Hollywood Script Consultant. Write a compelling cinematic story based on this concept: '{story_concept}'.
                    Genre Context: {combo_genre}
                    Language: Write the Title and Full Story in {story_language}.
                    
                    CRITICAL DURATION CONSTRAINT:
                    The targeted video length is {duration_min} minutes and {duration_sec} seconds. 
                    Therefore, the story length and detail density must be strictly: {length_instruction}
                    
                    Evaluate yourself at the very end of the output exactly within these tags:
                    CRITIQUE_START
                    Plot Twist Score: [1-10]
                    Emotional Depth Score: [1-10]
                    Reasoning: [One sentence explanation in English]
                    CRITIQUE_END
                    
                    Structure:
                    📌 STORY TITLE: [Title]
                    📖 FULL STORY: [Deep Narrative strictly following the length instruction]
                    """
                    
                    response = model.generate_content(story_command)
                    res_text = response.text
                    
                    twist_s = int(re.search(r"Plot Twist Score:\s*(\d+)", res_text).group(1)) if re.search(r"Plot Twist Score:\s*(\d+)", res_text) else 5
                    depth_s = int(re.search(r"Emotional Depth Score:\s*(\d+)", res_text).group(1)) if re.search(r"Emotional Depth Score:\s*(\d+)", res_text) else 5
                    reason = re.search(r"Reasoning:\s*(.*)", res_text).group(1) if re.search(r"Reasoning:\s*(.*)", res_text) else "Standard pacing."
                    
                    final_rating = (twist_s + depth_s) / 2.0
                    
                    if final_rating >= 7.0:
                        passed_gate = True
                        st.session_state.approved_story = re.sub(r"CRITIQUE_START.*?CRITIQUE_END", "", res_text, flags=re.DOTALL).strip()
                        st.session_state.story_analysis = {"rating": final_rating, "twist": twist_s, "depth": depth_s, "reason": reason, "genre": combo_genre}
                        st.session_state.story_stage = "story_ready"
                        break
                    time.sleep(0.5)
                    
                status_box.empty()
                if not passed_gate:
                    st.session_state.approved_story = re.sub(r"CRITIQUE_START.*?CRITIQUE_END", "", res_text, flags=re.DOTALL).strip()
                    st.session_state.story_analysis = {"rating": final_rating, "twist": twist_s, "depth": depth_s, "reason": "Fallback version.", "genre": combo_genre}
                    st.session_state.story_stage = "story_ready"
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- DISPLAY STORY & ASK FOR STEP 2 ---
if st.session_state.story_stage in ["story_ready", "board_ready"]:
    analysis = st.session_state.story_analysis
    st.markdown(f"""
    <div class="critique-card">
        <h4 style="color: #ffbc00; margin-top:0;">🛡️ AI Director Critic Board (Verified Content)</h4>
        <p><b>🎭 Blended Genre:</b> {analysis['genre']} | <b>⏱️ Target Video Duration:</b> {duration_min}m {duration_sec}s | <b>⭐ Total Rating:</b> {analysis['rating']}/10</p>
        <p>🔍 <b>Plot Twist Metric:</b> {analysis['twist']}/10 | 🎯 <b>Emotional Depth:</b> {analysis['depth']}/10</p>
        <p style="font-style: italic; color: #cbd5e1;">"Analysis: {analysis['reason']}"</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📖 Approved Narrative Story Baseline")
    edited_story = st.text_area("Story View", value=st.session_state.approved_story, height=250, label_visibility="collapsed")
    st.session_state.approved_story = edited_story
    
    if st.button("❌ Discard & Brainstorm New Story"):
        st.session_state.story_stage = "input"
        st.session_state.approved_story = ""
        st.session_state.final_production_board = ""
        st.rerun()
        
    st.markdown("<br><hr style='border-color: #334155;'/>", unsafe_allow_html=True)

    # --- STEP 2: SCENE SPLITTING WITH DYNAMIC CALCULATED SHOTS ---
    if st.session_state.story_stage == "story_ready":
        st.markdown("#### 🎬 Next Step: Construct Shot-List & Sync AI Prompts")
        
        if st.button("Step 2: Generate Verified Production Board"):
            try:
                genai.configure(api_key=user_api_key)
                
                # Maximum layout tokens enabled to support massive chronological output
                config_board = {
                    "temperature": 0.7,
                    "max_output_tokens": 8192
                }
                model = genai.GenerativeModel('gemini-2.5-flash', generation_config=config_board)
                
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
                
                prompt_passed = False
                p_attempt = 0
                status_box2 = st.empty()
                
                # Density scaling for timeline calculation
                estimated_shots_needed = max(4, int(total_target_seconds / 6)) 
                
                while p_attempt < 3 and not prompt_passed:
                    p_attempt += 1
                    status_box2.markdown(f"🎥 **AI Cinematographer (Shot Density Loop {p_attempt}/3):** Structuring chronological production timeline...")
                    
                    board_command = f"""
                    You are a meticulous Hollywood Continuity Director. 
                    Based on this APPROVED STORY pre-scaled for a {duration_min}m {duration_sec}s run-time:
                    '{st.session_state.approved_story}'
                    
                    CRITICAL SHOT-COUNT COMPLIANCE:
                    The video must run for exactly {duration_min}m {duration_sec}s.
                    You must meticulously break down the story into comprehensive sequential shots (target around {estimated_shots_needed} shots for long form). Do NOT condense, truncate, or drop any plot details. Every scene progression must have explicit production prompts.
                    
                    Character Profiles: '{char_profile}'
                    Language: Script layout in {story_language}. Image/Video prompts in English.
                    
                    Formats:
                    - Image Prompt: [Subject Description] in [Setting/Atmosphere], [Framing] with [Lens], [Lighting Type], [Color Palette], {img_style} --ar {image_ratio} {mj_ver}
                    - Video Prompt & Direction: [Cinematic Camera Movement], [Subject description + Kinetic Action matching the specific scene action], [Environment with dynamic elements], [Lighting & Color Palette], {vid_style}
                    
                    At the absolute end, rate your prompt accuracy exactly like this:
                    PROMPT_GATE_START
                    Prompt Quality Score: [1-10 based on whether the shot mapping spans the full requested timeline of {total_target_seconds} seconds without cutting corners]
                    PROMPT_GATE_END
                    
                    Structure:
                    🎬 SCENE & SHOT BREAKDOWN
                    
                    🎬 SCENE [Number]: [Location]
                    🎙️ NARRATION: [Text]
                    
                    List of Shots:
                      * SHOT [Scene Number].[Shot Number] - [Duration: X Seconds]
                      * Camera Shot Type: [Type]
                      * Action Description: [Myanmar Description]
                      * 👥 DIALOGUE: [Character]: "[Text]"
                      * Image Prompt: [Format]
                      * Video Prompt & Direction: [Format]
                      * Sound Style & Music Mood: [English profile]
                    """
                    
                    response = model.generate_content(board_command)
                    board_text = response.text
                    
                    p_score = int(re.search(r"Prompt Quality Score:\s*(\d+)", board_text).group(1)) if re.search(r"Prompt Quality Score:\s*(\d+)", board_text) else 5
                    
                    if p_score >= 8:
                        prompt_passed = True
                        st.session_state.final_production_board = re.sub(r"PROMPT_GATE_START.*?PROMPT_GATE_END", "", board_text, flags=re.DOTALL).strip()
                        st.session_state.story_stage = "board_ready"
                        break
                        
                status_box2.empty()
                if not prompt_passed:
                    st.session_state.final_production_board = re.sub(r"PROMPT_GATE_START.*?PROMPT_GATE_END", "", board_text, flags=re.DOTALL).strip()
                    st.session_state.story_stage = "board_ready"
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # --- DISPLAY FINAL PRODUCTION BOARD ---
    if st.session_state.story_stage == "board_ready":
        st.markdown("### 🎬 Verified Master Production Board (Editable)")
        st.success(f"🎉 **Perfect Pacing Synced!** {duration_min}မိနစ် {duration_sec}စက္ကန့်စာ ဗီဒီယိုအတွက် အချိုးကျ အကဲဖြတ်ပြီးသား Shot-List ထွက်လာပါပြီ။")
        
        final_board = st.text_area(label="Production Board Output", value=st.session_state.final_production_board, height=550, label_visibility="collapsed")
        st.session_state.final_production_board = final_board
        
        st.download_button(
            label="📥 Download Approved Master Production Board (.txt)",
            data=st.session_state.final_production_board,
            file_name=f"production_board_{story_type.lower()}.txt",
            mime="text/plain"
        )

st.markdown("</div>", unsafe_allow_html=True)
