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
        border-radius: 12px; background-color: rgba(255, 255, 255, 0.95);
        color: #0f172a !important; border: 2px solid #334155; padding: 14px 20px; font-weight: 600; caret-color: #000000 !important;
    }
    
    div.stButton > button {
        background: linear-gradient(45deg, #0f172a, #1e40af); color: white !important;
        font-weight: bold; font-size: 15px; border-radius: 25px; width: 100% !important; border: none; padding: 12px 25px !important; transition: all 0.3s ease;
    }
    div.stButton > button:hover { background: linear-gradient(45deg, #1e40af, #2563eb); transform: translateY(-1px); }
    
    [data-testid="stSidebar"] { background-color: #0f172a !important; border-right: 1px solid #1e293b; }
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

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- Main Interface ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Director's Master Script & Shot Board")
st.markdown("<div class='sub-text'>Two-Step High-Capacity AI Production Suite</div>", unsafe_allow_html=True)

story_concept = st.text_input("", placeholder="ဇတ်လမ်းအကျဉ်း သို့မဟုတ် အိုင်ဒီယာ ရေးရန်")
total_target_seconds = (duration_min * 60) + duration_sec

# --- STEP 1: GENERATE & VERIFY STORY ---
if st.session_state.story_stage == "input":
    if st.button("Step 1: Brainstorm Master Story"):
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
                
                if total_target_seconds <= 60: length_instruction = "SHORT & CRISP. Max 1-2 paragraphs (~150 words). Heavy plot twist."
                elif total_target_seconds <= 300: length_instruction = "MEDIUM LENGTH. 3-4 structured paragraphs (~500 words)."
                else: length_instruction = f"LONG DETAILED FORMAT. Large chronological narrative with multiple distinct events to fit a massive {duration_min}-minute timeline."

                while attempt < max_attempts and not passed_gate:
                    attempt += 1
                    status_box.markdown(f"🧠 **AI Director (Story Loop {attempt}/{max_attempts}):** Tailoring script for {duration_min}m {duration_sec}s...")
                    
                    story_command = f"""
                    Write a cinematic story based on: '{story_concept}'. Genre: {combo_genre}. Language: Output in {story_language}.
                    Constraint: Story length must follow: {length_instruction}. Include a great plot twist.
                    
                    Evaluate yourself at the end within these tags:
                    CRITIQUE_START
                    Plot Twist Score: [1-10]
                    Emotional Depth Score: [1-10]
                    Reasoning: [One sentence in English]
                    CRITIQUE_END
                    
                    Structure:
                    📌 STORY TITLE: [Title]
                    📖 FULL STORY: [Narrative Text]
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

# --- DISPLAY STORY & SCENE CHUNKER ---
if st.session_state.story_stage in ["story_ready", "scenes_extracted"]:
    analysis = st.session_state.story_analysis
    st.markdown(f"""
    <div class="critique-card">
        <h4 style="color: #ffbc00; margin-top:0;">🛡️ AI Director Critic Board</h4>
        <p><b>🎭 Genre:</b> {analysis['genre']} | <b>⏱️ Duration:</b> {duration_min}m {duration_sec}s | <b>⭐ IMDb Rating:</b> {analysis['rating']}/10</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📖 Approved Master Story")
    st.text_area("Story View", value=st.session_state.approved_story, height=200, label_visibility="collapsed")
    
    if st.button("❌ Discard & Reset"):
        st.session_state.story_stage = "input"
        st.session_state.approved_story = ""
        st.session_state.extracted_scenes = []
        st.session_state.scene_boards = {}
        st.rerun()

    st.markdown("<br><hr/>", unsafe_allow_html=True)

    # --- STEP 2: CHUNK SCENES TO PREVENT TIMEOUT ---
    if st.session_state.story_stage == "story_ready":
        st.markdown("#### 🎬 Step 2: Extracting Scenes & Timelines")
        if st.button("Analyze & Separate Into Scene Chunks"):
            try:
                genai.configure(api_key=user_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                chunk_command = f"""
                You are a film editor. Read this story: '{st.session_state.approved_story}'
                Break it down strictly into chronological sequential individual scenes. Do not miss any plot points.
                Output exactly in this format for parsing:
                SCENE_BLOCK_START
                Scene [Number]: [Location/Context Summary]
                Content: [The exact narrative excerpt belonging to this scene]
                SCENE_BLOCK_END
                """
                res = model.generate_content(chunk_command)
                raw_scenes = re.findall(r"SCENE_BLOCK_START(.*?)SCENE_BLOCK_END", res.text, flags=re.DOTALL)
                
                scenes_list = []
                for s in raw_scenes:
                    title_match = re.search(r"Scene \d+:.*", s)
                    content_match = re.search(r"Content:\s*(.*)", s, flags=re.DOTALL)
                    if title_match and content_match:
                        scenes_list.append({"title": title_match.group(0).strip(), "content": content_match.group(1).strip()})
                
                if scenes_list:
                    st.session_state.extracted_scenes = scenes_list
                    st.session_state.story_stage = "scenes_extracted"
                    st.rerun()
                else:
                    st.error("Scene splitting parsing error. Please try again.")
            except Exception as e: st.error(f"Error: {str(e)}")

    # --- STEP 3: INTERACTIVE INDIVIDUAL SCENE GENERATION ---
    if st.session_state.story_stage == "scenes_extracted":
        st.markdown("### 🎬 Continuity Production Board (Chunked Processing System)")
        st.info("Timeout အားနည်းချက်ကို ကုသရန် ဇာတ်လမ်းကို အောက်ပါအတိုင်း အခန်းခွဲပေးထားပါသည်။ တစ်ခန်းချင်းစီကို ကလစ်နှိပ်ပြီး အမှားအယွင်းမရှိ အသေးစိတ် Shot-list ထုတ်ယူနိုင်ပါပြီ။")
        
        # Art Style Rules Setup
        if "Disney" in art_style:
            mj_style = "3D Pixar Disney Animation Style, Vibrant Clay Render, Raytracing"
            v_style = "Disney Pixar Animation Style, Smooth Motion"
        elif "Anime" in art_style:
            mj_style = "Anime Key Visual, Sharp Lineart, Vibrant Colors, --niji 6"
            v_style = "Anime Motion, Fluent 2D Animation"
        else:
            mj_style = "Cinematic Still, Film Grain, 8k Resolution, Photorealistic, --style raw --v 6.0"
            v_style = "Cinematic Movie Style, Photorealistic, Masterpiece Motion"

        for idx, scene in enumerate(st.session_state.extracted_scenes):
            with st.container():
                st.markdown(f"<div class='scene-box'><h4>📌 {scene['title']}</h4><p>{scene['content']}</p></div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(f"🎬 Generate Shots", key=f"gen_{idx}"):
                        try:
                            genai.configure(api_key=user_api_key)
                            model = genai.GenerativeModel('gemini-2.5-flash')
                            
                            # Strict injection of character reference to lock character drift
                            character_lock = f"Maintain strict character consistency: {char_profile}." if char_profile else ""
                            
                            shot_command = f"""
                            You are a Director of Photography. Write a comprehensive Shot-by-Shot breakdown for this specific scene segment:
                            Title: {scene['title']}
                            Content: {scene['content']}
                            
                            CRITICAL LAWS:
                            1. CHARACTER LOCK RULE: {character_lock} Every single Image and Video prompt must explicitly start by describing the character exactly as defined.
                            2. Language: Narration and Dialogue in {story_language}. Technical prompts in English.
                            
                            Format per Shot:
                            * SHOT [Scene Number].[Shot Number]
                            * Camera Shot Type: [e.g. Close Up, Wide Shot]
                            * Action Description: [Myanmar detailed description]
                            * 👥 DIALOGUE/NARRATION: [Text]
                            * 🎨 Image Prompt (Midjourney): [Strictly start with Character Description if present], in [Setting], [Framing], [Lighting], {mj_style} --ar {image_ratio}
                            * 🎥 Video Prompt & Direction (Runway/Luma): [Camera Movement], [Subject with matching kinetic action from Action Description], {v_style}
                            """
                            
                            with st.spinner(f"{scene['title']} အတွက် Prompt များကို စိစစ်ထုတ်လုပ်နေသည်..."):
                                shot_res = model.generate_content(shot_command)
                                st.session_state.scene_boards[idx] = shot_res.text
                        except Exception as e: st.error(f"Error: {str(e)}")
                
                with col2:
                    if idx in st.session_state.scene_boards:
                        st.text_area("Shot Output", value=st.session_state.scene_boards[idx], height=250, key=f"text_{idx}")
                        st.download_button(label=f"📥 Download {scene['title']} Board", data=st.session_state.scene_boards[idx], file_name=f"scene_{idx}_board.txt", key=f"dl_{idx}")

st.markdown("</div>", unsafe_allow_html=True)
