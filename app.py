import streamlit as st
import google.generativeai as genai
import random

# App Layout အလှဆင်ခြင်း
st.set_page_config(page_title="AI Director & Storyboard Generator", page_icon="🎬", layout="wide")
st.title("🎬 AI Director & Storyboard Script Generator")
st.write("ကမ္ဘာကျော် စာရေးဆရာများနှင့် ဒါရိုက်တာများ၏ စတိုင်အတိုင်း Multi-media Content များ ထုတ်လုပ်ရန်")

# Side bar
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
scene_every_sec = st.sidebar.number_input("Scene Breakdown (Every X Seconds)", min_value=5, max_value=60, value=10, step=5)

# ၆။ Image / Video Prompt ထုတ်မထုတ် Option
get_image_prompt = st.sidebar.checkbox("Generate Image Prompts", value=True)
get_video_prompt = st.sidebar.checkbox("Generate Video Prompts", value=False)

# ၇။ Midjourney Ratio ရွေးရန်
image_ratio = st.sidebar.selectbox("Midjourney Ratio (--ar)", ["16:9", "9:16", "4:3", "1:1"])

st.sidebar.markdown("---")
user_api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
st.sidebar.markdown("[Get Free API Key](https://aistudio.google.com)")

# --- 💡 ပုံစံမတူအောင် ပြင်ဆင်ထားသည့် Main Screen Area အသစ် ---
st.markdown("### ✍️ ဇာတ်လမ်း အိုင်ဒီယာ ထည့်ရန် (Optional)")
# အသုံးပြုသူကို ဇာတ်လမ်းအမြုတေ အနည်းငယ် ရိုက်ထည့်ခိုင်းခြင်း (မရိုက်လည်း ရပါတယ်)
story_concept = st.text_input(
    "ဇာတ်လမ်းကို ဘာအကြောင်း ရေးစေချင်ပါလဲ? (ဥပမာ - ရွာတစ်ရွာက ရတနာသိုက်အကြောင်း၊ ကျောင်းသားတစ်ယောက် အောင်မြင်သွားပုံ စသဖြင့် အကြမ်းဖျင်း ရေးပေးနိုင်ပါတယ်)",
    placeholder="ဘာမှမရေးထားပါက AI က စိတ်ကူးသစ်တစ်ခုကို (Random) စဉ်းစားပြီး အမြဲတမ်း ပုံစံမတူအောင် ရေးပေးပါမည်။"
)

# Generate ခလုတ်
if st.button("Generate Master Script & Prompts ✨"):
    if not user_api_key:
        st.error("ကျေးဇူးပြု၍ ဘယ်ဘက်ဘောင်တွင် Gemini API Key အရင်ထည့်ပေးပါဦးဗျာ။")
    else:
        try:
            genai.configure(api_key=user_api_key)
            
            # --- 🚀 အဓိက ပြင်ဆင်လိုက်သည့်အပိုင်း (Temperature မြှင့်ခြင်း နှင့် ကျပန်းနံပါတ်ထည့်ခြင်း) ---
            # Temperature = 0.9 က AI ကို ပိုပြီး တီထွင်ဖန်တီးစေပါတယ် (Creative ဖြစ်စေပြီး ပုံစံမတူတော့ပါဘူး)
            generation_config = {
                "temperature": 0.95, 
                "top_p": 0.95,
                "top_k": 40,
            }
            
            model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                generation_config=generation_config
            )
            
            total_seconds = (duration_min * 60) + duration_sec
            estimated_scenes = max(1, total_seconds // scene_every_sec)
            
            # ဇာတ်လမ်း မထပ်စေရန် AI ကို ကွဲပြားခြားနားသော ဇာတ်ကွက် စဉ်းစားခိုင်းသည့် လှည့်ကွက်
            random_seed = random.randint(1, 100000)
            
            command = f"""
            သင်သည် ကမ္ဘာကျော် စာရေးဆရာကြီးများ နှင့် နာမည်ကြီး ဒါရိုက်တာများ ကဲ့သို့ အဆင့်မြင့် ဇာတ်ညွှန်းနှင့် Content များ ထုတ်ပေးနိုင်သော 'AI Director' ဖြစ်သည်။
            
            [အရေးကြီးသော သတိပြုရန်ချက်]
            ပြီးခဲ့သော အကြိမ်များက ပုံစံတူ ဇာတ်လမ်းများ ထွက်ပေါ်ခဲ့သဖြင့် ယခုအကြိမ်တွင် လုံးဝ လတ်ဆတ်ဆန်းသစ်ပြီး မထပ်မတူညီသော ဇာတ်အိမ်၊ ဇာတ်ကွက်သစ်ကိုသာ စဉ်းစားရမည်။ (Random Seed ID: {random_seed})
            
            [သတ်မှတ်ချက်များ]
            ၁။ ပုံပြင်ကြာချိန် - {duration_min} မိနစ် နှင့် {duration_sec} စက္ကန့် ခန့် ရှိရမည်။
            ၂။ ပုံပြင်အမျိုးအစား - {story_type} ဖြစ်ရမည်။ ( ပုံစံတူ မဟုတ်ဘဲ စိတ်ဝင်စားဖွယ် ဇာတ်လမ်းအလှည့်အပြောင်း ပါရမည်။)
            ၃။ ရေးသားရမည့် ဘာသာစကား - {language} ဖြစ်ရမည်။
            """
            
            # တကယ်လို့ အသုံးပြုသူက ဇာတ်လမ်းအိုင်ဒီယာ ပေးထားရင် အဲဒါကို သုံးမယ်၊ မပေးထားရင် ကျပန်းအသစ် စဉ်းစားခိုင်းမယ်
            if story_concept:
                command += f"\n၄။ ဇာတ်လမ်း၏ ပင်မအမြုတေ စိတ်ကူး (Concept): {story_concept} ကို အခြေခံ၍ ရေးသားပါ။"
            else:
                command += f"\n၄။ ဇာတ်လမ်း၏ ပင်မအမြုတေ စိတ်ကူး (Concept): ယခင်ရေးဖူးသော အကြောင်း၊ သာမန်အကြောင်းအရာများ လုံးဝ (လုံးဝ) မဖြစ်ရပါ။ အလွန်ထူးခြားပြီး ဆန်းသစ်သော Concept အသစ်တစ်ခုကို ကိုယ်တိုင် ဖန်တီး၍ ရေးသားပါ။"
            
            if get_image_prompt or get_video_prompt:
                command += f"""
                
                ၅။ Visual Art Style - {art_style}
                ၆။ Scene ခွဲခြားမှု - စုစုပေါင်း ကြာချိန် {total_seconds} စက္ကန့်ကို {scene_every_sec} စက္ကန့် လျှင် '၁ ကွက် (Scene)' နှုန်းဖြင့် စုစုပေါင်း ခန့်မှန်းခြေ {estimated_scenes} Scenes တိတိ အသေးစိတ် ခွဲခြားပေးရမည်။
                
                [Output Format ပုံစံကို အောက်ပါအတိုင်း အတိအကျ ထုတ်ပေးပါ]
                
                =========================================
                PART 1: THE FULL STORY (ဇာတ်လမ်းအပြည့်အစုံ)
                =========================================
                (ဤနေရာတွင် ကမ္ဘာကျော်စာရေးဆရာ စတိုင်ဖြင့် ရေးထားသော ပုံပြင်အပြည့်အစုံကို ဖတ်ရမည့် ကြာချိန်နှင့် ကိုက်ညီအောင် အရင်ဆုံး ချရေးပေးပါ။)
                
                =========================================
                PART 2: CHARACTER PROMPTS (ဇာတ်ကောင်ဒီဇိုင်းများ)
                =========================================
                (ပုံပြင်ထဲတွင် ပါဝင်သော ဇာတ်ကောင် အရေအတွက်အပေါ် မူတည်ပြီး ဇာတ်ကောင် တစ်ယောက်ချင်းစီအတွက် Midjourney Character Prompt ကို အင်္ဂလိပ်လို ထုတ်ပေးပါ။)
                
                =========================================
                PART 3: SCENE BY SCENE BREAKDOWN (ရုပ်ရှင်ဇာတ်ကွက် ခွဲခြားမှု)
                =========================================
                ## SCENE 1 (Time: 0s - {scene_every_sec}s)
                - **Narration and Dialogue:** (ဤအခန်းအတွက် ပြောမည့်စာသား သို့မဟုတ် စကားပြောများကို {language} ဖြင့် ရေးရန်)
                """
                
                if get_image_prompt:
                    command += f"""
                - **Image Prompt:** (Midjourney Formula: [Subject Description] in [Setting/Atmosphere], [Framing] with [Lens], [Lighting Type], [Color Palette], Cinematic Still, Film Grain, --ar {image_ratio} --style raw) (Visual Style: {art_style})
                    """
                
                if get_video_prompt:
                    command += f"""
                - **Video Prompt:** (Video Formula: [Camera Movement], [Subject description + Action], [Environment with dynamic elements], [Lighting & Color Palette], [Cinematic Terms])
                    """
                
                command += """
                - **Sound Style:** (Background Music သို့မဟုတ် Sound Effects စတိုင်ကို အင်္ဂလိပ်လို ရေးရန်)
                
                (ဤပုံစံအတိုင်း နောက်ထပ် Scene များအထိ ဆက်သွားပေးပါ။)
                """
            else:
                command += """
                ၅။ Output အနေဖြင့် အခြား မလိုအပ်သော Prompt များ ထည့်သွင်းရန်မလိုဘဲ အဆင့်မြင့် ကမ္ဘာကျော်စာရေးဆရာ စတိုင်ဖြင့် ပုံပြင် (Story) သီးသန့်ကိုသာ Format လှလှပပဖြင့် ထုတ်ပေးပါ။
                """
                
            command += "\n\nကျေးဇူးပြု၍ သတ်မှတ်ချက် Formula အားလုံး ပြည့်စုံအောင် တစ်သွေမတိမ်း ထုတ်ပေးပါ။"

            with st.spinner("🎬 AI Director က မထပ်မတူညီသော ဇာတ်လမ်းအသစ်ကို ဖန်တီးပေးနေပါသည်..."):
                response = model.generate_content(command)
                result_text = response.text
                
                st.success("Master Script ထွက်ပေါ်လာပါပြီ။")
                st.markdown("### 📝 Generated Script & Production Board")
                st.write(result_text)
                
                # ဒေါင်းလုဒ် ခလုတ်
                st.download_button(
                    label="📥 Download Master Script (.txt)",
                    data=result_text,
                    file_name=f"ai_{story_type}_production_script.txt",
                    mime="text/plain"
                )
        except Exception as e:
            st.error(f"အမှားအယွင်းတစ်ခု ရှိသွားပါသည်- {str(e)}")
