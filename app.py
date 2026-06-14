import streamlit as st
import google.generativeai as genai

# App Layout အလှဆင်ခြင်း
st.set_page_config(page_title="AI Director & Storyboard Generator", page_icon="🎬", layout="wide")
st.title("🎬 AI Director & Storyboard Script Generator")
st.write("ကမ္ဘာကျော် စာရေးဆရာများနှင့် ဒါရိုက်တာများ၏ စတိုင်အတိုင်း Multi-media Content များ ထုတ်လုပ်ရန်")

# ဘေးဘောင် Settings
st.sidebar.header("⚙️ Production Settings")

# ၁။ ကြာချိန် (Min / Sec)
duration_min = st.sidebar.slider("Duration (Minutes)", 0, 10, 1)
duration_sec = st.sidebar.slider("Duration (Seconds)", 0, 50, 0, step=10)

# ၂။ Story Type
story_type = st.sidebar.selectbox(
    "Story Type",
    ["Horror (သရဲ)", "Romance (အချစ်)", "Fantasy (ဒဏ္ဍာရီ)", "Sci-Fi (သိပ္ပံ)", "Comedy (ဟာသ)", "Action (အက်ရှင်)", "Drama (ဒရမ်မာ)"]
)

# ၃။ ဘာသာစကား ရွေးချယ်မှု
language = st.sidebar.radio("Language (ဘာသာစကား)", ["Myanmar (မြန်မာလို)", "English (အင်္ဂလိပ်လို)"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Prompt Generation Options")

# ၄။ Art Style ရွေးချယ်မှု
art_style = st.sidebar.selectbox(
    "Visual Art Style",
    ["Japan Animation Style (Anime)", "3D Disney Cartoon Style", "Realistic Cinematic Movie", "Cyberpunk Art"]
)

# ၅။ Scene Breakdown ခွဲမည့် စက္ကန့်
scene_every_sec = st.sidebar.number_input("Scene Breakdown (Every X Seconds)", min_value=5, max_value=60, value=10, step=1)

# ၆။ Image / Video Prompt ထုတ်မထုတ် Option
get_image_prompt = st.sidebar.checkbox("Generate Image Prompts", value=True)
get_video_prompt = st.sidebar.checkbox("Generate Video Prompts", value=False)

# ၇။ Midjourney Ratio ရွေးရန်
image_ratio = st.sidebar.selectbox("Midjourney Ratio (--ar)", ["16:9", "9:16", "4:3", "1:1"])

st.sidebar.markdown("---")
# API Key ထည့်ရန်နေရာ
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get Free API Key](https://aistudio.google.com)")

# Generate ခလုတ်
if st.button("Generate Master Script & Prompts ✨"):
    if not user_api_key:
        st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ဘောင်တွင် Gemini API Key အရင်ထည့်ပေးပါဦး။")
    else:
        try:
            genai.configure(api_key=user_api_key)
            model = genai.GenerativeModel('gemini-2.5-pro') # ပိုကောင်းပြီး အရှည်ကြီး ထုတ်နိုင်တဲ့ Model ပြောင်းသုံးထားပါတယ်
            
            # ခန့်မှန်း Scene အရေအတွက် တွက်ချက်ခြင်း
            total_seconds = (duration_min * 60) + duration_sec
            estimated_scenes = max(1, total_seconds // scene_every_sec)
            
            # --- AI ဆီ ပို့မည့် Master Command (System Prompt) တည်ဆောက်ခြင်း ---
            command = f"""
            သင်သည် ကမ္ဘာကျော် စာရေးဆရာကြီးများ (ဥပမာ- Stephen King, J.K. Rowling) နှင့် နာမည်ကြီး ဒါရိုက်တာများ ကဲ့သို့ အဆင့်မြင့် ဇာတ်ညွှန်းနှင့် Content များ ထုတ်ပေးနိုင်သော 'AI Director' ဖြစ်သည်။
            
            အောက်ပါ သတ်မှတ်ချက်များအတိုင်း Master Script တစ်ခုကို ရေးသားပေးပါ။
            
            [သတ်မှတ်ချက်များ]
            ၁။ ပုံပြင်ကြာချိန် - {duration_min} မိနစ် နှင့် {duration_sec} စက္ကန့် (စုစုပေါင်း {total_seconds} စက္ကန့် ခန့် ရှိရမည်)
            ၂။ ပုံပြင်အမျိုးအစား - {story_type} ဖြစ်ရမည်။ (အောင်မြင်သော Story တစ်ပုဒ်တွင် ပါဝင်ရမည့် အခြေခံ Story Structure ဇာတ်ကွက် အတက်အကျ၊ စိတ်လှုပ်ရှားဖွယ်ရာများ ပါဝင်ရမည်။)
            ၃။ ရေးသားရမည့် ဘာသာစကား - {language} ဖြစ်ရမည်။
            """
            
            # အကယ်၍ Image သို့မဟုတ် Video Options တွေ ရွေးထားရင် ပိုမိုအဆင့်မြင့်တဲ့ Prompt Formula ကို ညွှန်ကြားမယ်
            if get_image_prompt or get_video_prompt:
                command += f"""
                
                ၄။ Visual Art Style - {art_style}
                ၅။ Scene ခွဲခြားမှု - စုစုပေါင်း ကြာချိန် {total_seconds} စက္ကန့်ကို {scene_every_sec} စက္ကန့် လျှင် '၁ ကွက် (Scene)' နှုန်းဖြင့် စုစုပေါင်း ခန့်မှန်းခြေ {estimated_scenes} Scenes တိတိ အသေးစိတ် ခွဲခြားပေးရမည်။
                
                [Output Format ပုံစံကို အောက်ပါအတိုင်း အတိအကျ ထုတ်ပေးပါ]
                
                =========================================
                PART 1: THE FULL STORY (ဇာတ်လမ်းအပြည့်အစုံ)
                =========================================
                (ဤနေရာတွင် ကမ္ဘာကျော်စာရေးဆရာ စတိုင်ဖြင့် ရေးထားသော ပုံပြင်အပြည့်အစုံကို ဖတ်ရမည့် ကြာချိန်နှင့် ကိုက်ညီအောင် အရင်ဆုံး ချရေးပေးပါ။)
                
                =========================================
                PART 2: CHARACTER PROMPTS (ဇာတ်ကောင်ဒီဇိုင်းများ)
                =========================================
                (ပုံပြင်ထဲတွင် ပါဝင်သော ဇာတ်ကောင် အရေအတွက်အပေါ် မူတည်ပြီး ဇာတ်ကောင် တစ်ယောက်ချင်းစီအတွက် Midjourney Character Prompt ကို အင်္ဂလိပ်လို ထုတ်ပေးပါ။)
                ဥပမာ - Character 1 (Name): [Description in English for Midjourney]
                
                =========================================
                PART 3: SCENE BY SCENE BREAKDOWN (ရုပ်ရှင်ဇာတ်ကွက် ခွဲခြားမှု)
                =========================================
                (Scene တစ်ခုချင်းစီအလိုက် အောက်ပါ တည်ဆောက်ပုံအတိုင်း တစ်ဆင့်ချင်းစီ (Sequence) သွားပေးပါ-)
                
                ## SCENE 1 (Time: 0s - {scene_every_sec}s)
                - **Narration and Dialogue:** (ဤအခန်းအတွက် ပြောမည့်စာသား သို့မဟုတ် စကားပြောများကို ရွေးချယ်ထားသော {language} ဖြင့် ရေးရန်)
                """
                
                if get_image_prompt:
                    command += f"""
                - **Image Prompt:** (Midjourney အတွက် အင်္ဂလိပ်လို သီးသန့်ရေးပေးရန်။ Formula အတိအကျမှာ - [Subject Description] in [Setting/Atmosphere], [Framing] with [Lens], [Lighting Type], [Color Palette], Cinematic Still, Film Grain, --ar {image_ratio} --style raw) (ဤနေရာတွင် Visual Art Style က {art_style} ဖြစ်ရမည်။)
                    """
                
                if get_video_prompt:
                    command += f"""
                - **Video Prompt:** (AI Video tool များအတွက် အင်္ဂလိပ်လို သီးသန့်ရေးပေးရန်။ Formula အတိအကျမှာ - [Camera Movement], [Subject description + Action], [Environment with dynamic elements], [Lighting & Color Palette], [Cinematic Terms])
                    """
                
                command += """
                - **Sound Style:** (ဤအခန်း နောက်ခံတွင် ပါဝင်ရမည့် Background Music သို့မဟုတ် Sound Effects (SFX) စတိုင်ကို အင်္ဂလိပ်လို ရေးရန်)
                
                (ဤပုံစံအတိုင်း နောက်ထပ် Scene 2, Scene 3 စသည်ဖြင့် နောက်ဆုံး Scene အထိ ဆက်သွားပေးပါ။)
                """
            else:
                # အကယ်၍ အောက်ကဟာတွေ ဘာမှ မရွေးထားရင် ပုံပြင် သီးသန့်ပဲ ထုတ်ပေးမယ်
                command += """
                ၄။ Output အနေဖြင့် အခြား မလိုအပ်သော Prompt များ ထည့်သွင်းရန်မလိုဘဲ အဆင့်မြင့် ကမ္ဘာကျော်စာရေးဆရာ စတိုင်ဖြင့် ပုံပြင် (Story) သီးသန့်ကိုသာ Format လှလှပပဖြင့် ထုတ်ပေးပါ။
                """
                
            command += "\n\nကျေးဇူးပြု၍ သတ်မှတ်ချက် Formula အားလုံး ပြည့်စုံအောင် တစ်သွေမတိမ်း ထုတ်ပေးပါ။"

            with st.spinner("🎬 AI Director က ဇာတ်ညွှန်းနှင့် Prompts များကို အချောသတ်နေပါသည်... (Gemini 1.5 Pro သုံးထားသဖြင့် စက္ကန့် ၃၀ ခန့် ကြာနိုင်ပါသည်)"):
                response = model.generate_content(command)
                result_text = response.text
                
                st.success("Master Script ထွက်ပေါ်လာပါပြီ။")
                st.markdown("### 📝 Generated Script & Production Board")
                st.write(result_text)
                
                # ဒေါင်းလုဒ် ခလုတ် (100% Free)
                st.download_button(
                    label="📥 Download Master Script (.txt)",
                    data=result_text,
                    file_name=f"ai_{story_type}_production_script.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"အမှားအယွင်းတစ်ခု ရှိသွားပါသည်- {str(e)}")
