import streamlit as st
import openai  # OpenRouter သည် OpenAI client ကို သုံးရပါသည်
import random
import time
import re
import base64
import os

st.set_page_config(page_title="AI Director Master Shot-List Studio (FREE AI)", layout="wide")

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

image_file = "bg.jpg"
if os.path.exists(image_file):
    bin_str = get_base64_of_bin_file(image_file)
    bg_img_style = f"background-image: url('data:image/jpeg;base64,{bin_str}');"
else:
    bg_img_style = "background-image: url('https://w0.peakpx.com/wallpaper/705/104/HD-wallpaper-anime-girls-playing-games-bed-short-hair-blond.jpg');"

custom_css = f"""
<style>
    .stApp {{ {bg_img_style} background-size: cover; background-position: center top; background-attachment: fixed; }}
    .main-content {{ padding: 15px; background-color: rgba(15, 23, 42, 0.7); border-radius: 16px; margin-top: 10px; }}
    h1 {{ color: #ffffff !important; text-align: center; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }}
    .sub-text {{ text-align: center; color: #ffbc00 !important; font-size: 16px; margin-bottom: 25px; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }}
    .stTextInput > div > div > input {{ border-radius: 12px; background-color: rgba(255, 255, 255, 0.95); color: #0f172a !important; font-weight: 600; caret-color: #000000 !important; }}
    div.stButton > button {{ background: linear-gradient(45deg, #0f172a, #1e40af); color: white !important; font-weight: bold; border-radius: 25px; width: 100% !important; padding: 12px 25px !important; }}
    [data-testid="stSidebar"] {{ background-color: rgba(15, 23, 42, 0.95) !important; }}
    .stTextArea textarea {{ background-color: rgba(255, 255, 255, 0.98) !important; color: #0f172a !important; line-height: 1.7 !important; border-radius: 12px !important; padding: 15px !important; }}
    .scene-box {{ background-color: rgba(255, 255, 255, 0.95); border-left: 5px solid #1e40af; padding: 15px; border-radius: 8px; color: #0f172a; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

if "story_stage" not in st.session_state: st.session_state.story_stage = "input"
if "approved_story" not in st.session_state: st.session_state.approved_story = ""
if "story_analysis" not in st.session_state: st.session_state.story_analysis = {}
if "extracted_scenes" not in st.session_state: st.session_state.extracted_scenes = []
if "scene_boards" not in st.session_state: st.session_state.scene_boards = {}

st.sidebar.markdown("<h2>⚙️ Production Settings</h2>", unsafe_allow_html=True)
story_language = st.sidebar.radio("Output Language", ["Myanmar", "English"])
col_min, col_sec = st.sidebar.columns(2)
duration_min = col_min.number_input("Minutes", min_value=0, max_value=40, value=1)
duration_sec = col_sec.number_input("Seconds", min_value=0, max_value=59, value=0)

story_type = st.sidebar.selectbox("Genre 1", ["Drama", "Horror", "Romance", "Fantasy", "Sci-Fi", "Comedy", "Action"])
secondary_type = st.sidebar.selectbox("Genre 2", ["None", "Action", "Drama", "Thriller", "Comedy", "Romance", "Mystery"])
art_style = st.sidebar.selectbox("Style", ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"])
image_ratio = st.sidebar.selectbox("Ratio", ["16:9", "9:16", "4:3", "1:1"])

# OpenRouter Free AI Models ရွေးချယ်မှုအပိုင်း
model_choice = st.sidebar.selectbox(
    "Choose Free AI Model", 
    ["Claude 3 Haiku (Highly Creative)", "Gemini 2.5 Flash (Recommended)", "Llama 3.3 70B"]
)

if model_choice == "Claude 3 Haiku (Highly Creative)":
    free_model = "anthropic/claude-3-haiku:free"
elif model_choice == "Gemini 2.5 Flash (Recommended)":
    free_model = "google/gemini-2.5-flash:free"
else:
    free_model = "meta-llama/llama-3.3-70b-instruct:free"

# OpenRouter API Key ထည့်ရန်
user_api_key = st.sidebar.text_input("OpenRouter API Key (FREE)", type="password", help="openrouter.ai တွင် ရယူထားသော API Key အရှည်ကြီးကို အပြည့်အစုံထည့်ပါ")

st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("AI Director's Master Script & Shot Board")

# OpenRouter Client ဆောက်သည့် Function
def get_openrouter_client(api_key):
    return openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

if st.session_state.story_stage == "input":
    story_concept = st.text_input("Story Concept", placeholder="ဇတ်လမ်းအကျဉ်းကို စိတ်ကြိုက်ရေးပါ...")
    total_target_seconds = (duration_min * 60) + duration_sec
    
    if st.button("Step 1: Brainstorm Master Screenplay"):
        if not user_api_key: st.error("OpenRouter API Key လိုအပ်ပါသည်။ (openrouter.ai တွင် အခမဲ့ရယူပါ)")
        elif total_target_seconds == 0: st.error("ကျေးဇူးပြု၍ အချိန်သတ်မှတ်ပေးပါ။")
        else:
            try:
                client = get_openrouter_client(user_api_key)
                combo_genre = story_type if secondary_type == "None" else f"{story_type} + {secondary_type}"
                
                if total_target_seconds <= 60:
                    length_instruction = "SHORT SCREENPLAY. Must strictly be 1-2 distinct scenes."
                elif total_target_seconds <= 300:
                    length_instruction = "MEDIUM SCREENPLAY. Must strictly be 3-4 structured scenes."
                else:
                    length_instruction = "EPIC MULTI-ACT SCRIPT. Detailed multi-scene timeline (5+ scenes)."

                with st.spinner(f"🔄 {model_choice} မှ Master Screenplay ကို ဖန်တီးပေးနေပါသည်..."):
                    story_command = f"""
                    Write a 100% highly original, creative fictional movie screenplay based loosely on: '{story_concept}'. 
                    Do NOT copy any existing copyrighted dialogues, real movies, or books. Make it unique.
                    Genre: {combo_genre}. Language: Write in {story_language}.
                    Scale Constraint: {length_instruction}
                    
                    Format:
                    📌 SCRIPT TITLE: [Title]
                    📖 FULL SCREENPLAY: [Write scene headings and character dialogues]
                    """
                    
                    response = client.chat.completions.create(
                        model=free_model,
                        messages=[{"role": "user", "content": story_command}]
                    )
                    
                    ai_text = response.choices[0].message.content
                    
                    if ai_text:
                        st.session_state.approved_story = ai_text.strip()
                        st.session_state.story_analysis = {"genre": combo_genre}
                        st.session_state.story_stage = "story_ready"
                        st.rerun()
            except Exception as e: st.error(f"Error: {str(e)}")

if st.session_state.story_stage in ["story_ready", "scenes_extracted"]:
    st.markdown("<h3 style='color: white;'>📖 Approved Screenplay Script</h3>", unsafe_allow_html=True)
    st.text_area("Story View", value=st.session_state.approved_story, height=200, label_visibility="collapsed")
    
    if st.button("❌ Discard Project"):
        st.session_state.story_stage = "input"
        st.session_state.approved_story = ""
        st.session_state.extracted_scenes = []
        st.session_state.scene_boards = {}
        st.rerun()

    if st.session_state.story_stage == "story_ready":
        if st.button("Separate Screenplay Into Scene Chunks"):
            try:
                client = get_openrouter_client(user_api_key)
                chunk_command = f"Break this script into logical individual scenes using format SCENE_BLOCK_START Scene X: Description Content: Text SCENE_BLOCK_END. Script: {st.session_state.approved_story}"
                
                res = client.chat.completions.create(
                    model=free_model,
                    messages=[{"role": "user", "content": chunk_command}]
                )
                
                raw_text = res.choices[0].message.content
                raw_scenes = re.findall(r"SCENE_BLOCK_START(.*?)SCENE_BLOCK_END", raw_text, flags=re.DOTALL)
