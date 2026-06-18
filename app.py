import streamlit as st
import google.generativeai as genai
import random

# --- Page Config ---
st.set_page_config(page_title="AI Director Shot-List & Script Generator", layout="wide")

# --- Custom CSS for Premium Visuals, Clean Contrast & Full Width Buttons ---
st.markdown("""
    <style>
        /* 1. Raw Background Photo (NO MASK) - High Clarity */
        .stApp {
            background-image: url('https://wallpaperaccess.com/full/288747.jpg');
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
""", unsafe_allow_html=True)

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
            
            # 🧠 Advanced Film Director & Disney-style Shot Multi-Splitter Prompt
            command = f"""
            You are a world-class Film Director and Animation Storyboard Artist from Disney and Pixar.
            Analyze the concept and create a highly professional shooting script broken down into structural Scenes, and sub-divided into independent cinematic SHOTS. (Seed: {random_seed})
            
            [Specifications]
            1. Target Video Duration: {duration_min} minutes and {duration_sec} seconds (Total: {total_seconds} seconds).
            2. Genre: {story_type}
            3. Main Language: Script narrative and action lines must be written in {story_language}. Technical AI prompts must be in English.
            4. Plot Concept: '{story_concept}'
            
            [Strict Director's Multi-Shot Breakdown Rules]
            - First, output a high-level **SCRIPT & STORY** text overview in {story_language}.
            - Next, break the master story down into broad **SCENES** based on locations (e.g., Scene 1: Living Room, Scene 2: Dark Forest).
            - [CRITICAL] Inside EACH SCENE, you must break it down into MULTIPLE separate **SHOTS** (just like Disney animation pacing). 
            - Each SHOT must be assigned a random dynamic pacing cut of either 3sec, 4sec, 5sec, 6sec, or 7sec. Cumulative shot times should target the total video length.
            
            [Output Format Structure for each Scene block]
            Write: "🎬 SCENE [Number]: [Location Name] - [Time of Day]"
            Then list the multiple shots inside it:
              * SHOT [Scene Number].[Shot Number] (e.g., SHOT 1.1) - [Duration: X Seconds (Choose between 3s to 7s)]
              * Action / Character Dialogue: (Written in {story_language} detailing what happens in this specific 3-7s snippet)
            """
            
            if get_image_prompt:
                command += f"\n              * Image Prompt: Detailed Midjourney text prompt in English matching visual style '{art_style}' with aspect ratio '--ar {image_ratio}'. Set exact spatial positions of characters/objects (e.g., 'On the left side...')."
              
            if get_video_prompt:
                command += "\n              * Video Prompt & Direction: Dynamic generative video prompt (Sora/Runway) in English. Must maintain 100% spatial alignment with the Image Prompt above. If the subject is on the left in the image, camera/action directions must reference the left side. Specify camera techniques (Pan, Zoom, Dolly, Close-up, Wide)."
                
            command += "\n\nFormat the output beautifully and structurally so the user can easily review or edit."
            
            with st.spinner("⚡ Disney-Style Shot Multi-Splitter Engine is producing your master board..."):
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
