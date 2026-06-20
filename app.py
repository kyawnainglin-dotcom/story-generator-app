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

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)

get_image_prompt = st.sidebar.checkbox("Generate Image Prompts", value=True)
get_video_prompt = st.sidebar.checkbox("Generate Video Prompts & Directions", value=True)

st.sidebar.markdown("<hr style='border-color: #1e293b;'/>", unsafe_allow_html=True)
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get Free API Key](https://aistudio.google.com)")


# --- 🎬 Main Frame Screen Display ---
st.markdown("<div class='main-content'>", unsafe_allow_html=True)
st.title("Director's Master Script & Shot Board")
st.markdown("<div class='sub-text'>Professional Scene Splitter & Prompt Sync Engine</div>", unsafe_allow_html=True)

story_concept = st.text_input("", placeholder="ဇတ်လမ်းအကျဉ်း သို့မဟုတ် အိုင်ဒီယာ ရေးရန်")

if st.button("Generate Production Board"):
    if not user_api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            generation_config = {
                "temperature": 0.85, 
                "top_p": 0.95,
                "top_k": 40,
            }
            
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                generation_config=generation_config
            )
            
            total_seconds = (duration_min * 60) + duration_sec
            random_seed = random.randint(1, 100000)
            
            # --- Determine Midjourney Version Tag based on Style Selection ---
            mj_version = "--v 6.0"
            if "Anime" in art_style:
                mj_version = "--niji 6"
            
            # 🧠 Master Ordered Prompt Structure
            command = f"""
            You are a Legendary Screenplay Writer, Hollywood Film Director, and Disney Animation Storyboard Artist.
            Generate a comprehensive production document according to the following strict layout. (Seed: {random_seed})
            
            [Specifications]
            1. Target Video Duration: {duration_min} minutes and {duration_sec} seconds.
            2. Genre: {story_type}
            3. Main Language: Text content for Story Title, Full Story, Script & Story Overview, Narration, Action lines, and Dialogue blocks MUST be written beautifully in {story_language}. Technical prompts (Image, Video, Sound) must be in English.
            4. Plot Concept: '{story_concept}'
            5. Character Reference Profile: '{char_profile if char_profile else "Automatically define unique character visuals."}'
            
            [Strict Director's Dynamic Pacing Rules]
            - Inside Scenes, break them down into separate shots using smart variable pacing:
              * [RULE A] If a shot is a Landscape, Scenery, Establishing View, or Drone View -> Assign a duration of 5sec, 6sec, or 7sec (Long Slow Takes).
              * [RULE B] If a shot contains character actions, movements, or dialogue -> Assign a fast-paced duration of 1sec, 2sec, or 3sec (Fast Dynamic Cuts).
            
            [OUTPUT LAYOUT STRUCTURE - You MUST output exactly in this sequence]
            
            📌 STORY TITLE
            (Generate a creative title in {story_language})
            
            ---
            
            📖 FULL STORY
            (Expand the input concept into a cohesive, beautifully structured full narrative story in {story_language})
            
            ---
            
            🎬 SCRIPT & STORY OVERVIEW
            (Provide a cinematic high-level breakdown of the script structure and target vision in {story_language})
            
            ---
            
            🎭 CHARACTER PROMPTS
            (Based on the story, generate specialized English Midjourney prompts for each main character to ensure 100% appearance consistency across independent image generation tasks. Format as: Character Name - English Midjourney Prompt with style tags)
            
            ---
            
            🎬 SCENE & SHOT BREAKDOWN
            (Output each scene systematically following this internal block design):
            
            🎬 SCENE [Number]: [Location Name] - [Time of Day]
            🎙️ NARRATION: (Write deep, immersive voiceover narration in {story_language})
            
            List of Shots inside this scene:
              * SHOT [Scene Number].[Shot Number] - [Duration: X Seconds]
              * Camera Shot Type: (e.g., Wide Establishing Shot, Close-up, Dolly Zoom)
              * Action Description: (Detail what happens in {story_language})
              * 👥 DIALOGUE: [Character Name]: "[Dialogue line in {story_language}]" (If none, omit)
            """
            
            if get_image_prompt:
                command += f"""
              * Image Prompt: Format exactly as: [Subject Description] in [Setting/Atmosphere], [Framing] with [Lens], [Lighting Type], [Color Palette], Cinematic Still, Film Grain, --ar {image_ratio} {mj_version} --style raw"""
              
            if get_video_prompt:
                command += """
              * Video Prompt & Direction: Format exactly as: [Camera Movement], [Subject description + Action], [Environment with dynamic elements], [Lighting & Color Palette], [Cinematic Terms]"""
                
            command += "\n              * Sound Style & Music Mood: Generate descriptive SFX, ambient noise profiles, and orchestral cues in English."
                
            command += "\n\nFormat the output beautifully, separated cleanly by sections using Markdown formatting."
            
            with st.spinner("⚡ Director AI is constructing your complete structured masterpiece..."):
                response = model.generate_content(command)
                st.session_state.generated_script = response.text
                
        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")

# --- ✍️ Editable Output Board Section ---
if st.session_state.generated_script:
    st.markdown("<br><hr style='border-color: #cbd5e1;'/>", unsafe_allow_html=True)
    st.markdown("### 🎬 Director's Production Board (Editable)")
    st.info("💡 အောက်က Box ထဲက စာသားတွေကို စိတ်ကြိုက် ပြင်ဆင်၊ ဖျက်၊ တိုး ရေးသားနိုင်ပါတယ်ဗျာ။ ပြင်ပြီးရင် အောက်က ခလုတ်နဲ့ ဒေါင်းလုဒ် ဆွဲနိုင်ပါတယ်။")
    
    edited_script = st.text_area(
        label="Edit Script & Prompt Board Here",
        value=st.session_state.generated_script,
        height=550,
        label_visibility="collapsed"
    )
    
    st.session_state.generated_script = edited_script
    
    st.download_button(
        label="📥 Download Edited Master Script (.txt)",
        data=st.session_state.generated_script,
        file_name=f"director_edited_{story_type.lower()}_script.txt",
        mime="text/plain"
    )

st.markdown("</div>", unsafe_allow_html=True)
