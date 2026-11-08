import streamlit as st
from google import genai
from dotenv import load_dotenv
import base64
import os
from groq import Groq
from gtts import gTTS
import io
from PIL import Image

load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
   page_title="AI Multi-Modal TRANSLATOR",
   page_icon="🔤",
   layout="centered"
)

if "translation_history" not in st.session_state:
    st.session_state.translation_history = []

if "current_translation" not in st.session_state:
    st.session_state.current_translation = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GEMINI_API_KEY and not GROQ_API_KEY:
   st.error("Please set at least one provider API key in your .env file (GEMINI_API_KEY or GROQ_API_KEY).")
   st.stop()

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

st.title("🔤 AI Multi-Modal Two-Way Translator")
st.write("Translate text or images across languages with audio playback")

# Input Selection (Text or Image Upload)
input_mode = st.radio("Choose Input Type:", ["Text Input", "Image OCR"])

source_text = ""
uploaded_image = None
uploaded_file = None

# List of popular languages for selection
languages = [
    "English",
    "Spanish",
    "French",
    "German",
    "Hindi",
    "Marathi",
    "Japanese",
    "Mandarin Chinese",
    "Arabic",
    "Portuguese",
    "Russian"
]

# Side-by-side dropdowns for source and target languages
col1, col2 = st.columns(2)
with col1:
   source_lang = st.selectbox("Source Language", ["Auto-Detect"] + languages)
with col2:
   # Default target language is set to English (index 0)
   target_lang = st.selectbox("Target Language", languages, index=0)

if input_mode == "Text Input":
    source_text = st.text_area(
        "Enter the Text you want to Translate:",
        placeholder="Type or paste text here (in any language)..."
    )

else:
    uploaded_file = st.file_uploader("Upload an Image containing Text:", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        uploaded_image = Image.open(uploaded_file)
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
    source_text = st.text_input(
        "Optional context or specific instruction for the image:", 
        placeholder="e.g., Translate the main menu items"
        )

# Handle Translation Logic
if st.button("Translate Text", type="primary"):
    st.session_state.current_translation = None

    if input_mode == "Text Input" and not source_text.strip():
        st.warning("Please enter some text to Translate!")

    elif input_mode == "Image OCR" and uploaded_image is None:
        st.warning("Please Upload an Image first!")

    else:
        if uploaded_image is not None:
            source_instruction = (
                "Detect the image's source language automatically."
                if source_lang == "Auto-Detect"
                else f"The text in the image is in {source_lang}."
            )
            prompt = f"""
            You are a professional, accurate translator. Read the text visible in the supplied image,
            {source_instruction} Translate it into fluent, natural {target_lang}.
            Use this context or instruction if provided: {source_text or "None"}.
            Provide ONLY the translated text without extra conversational filler.
            """
        elif source_lang == "Auto-Detect":
           prompt = f"""
            You are a professional, accurate translator.
            Translate the supplied text into fluent, natural {target_lang}.
             
            Text to translate:
            {source_text}
            
            Provide ONLY the translated text without extra conversational filler.
            """
        else:
           prompt = f"""
            You are a professional, accurate translator. 
            Translate the following text from {source_lang} into fluent, natural {target_lang}. 
            
            Text to translate:
            {source_text}
            
            Provide ONLY the translated text without extra conversational filler.
            """

        response_text = ""
        active_provider = ""
        success = False
        groq_error = "Groq fallback is unavailable because no GROQ_API_KEY is set."

        with st.spinner("Translating via AI Fallback Network..."):

            if gemini_client is not None:
                try:
                    contents = [prompt, uploaded_image] if uploaded_image is not None else prompt
                    response = gemini_client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=contents
                    )

                    response_text = response.text
                    active_provider = "Google Gemini (gemini-3.6-flash)"
                    success = True

                except Exception as e1:
                    groq_error = "Groq fallback is unavailable because no GROQ_API_KEY is set."
                    if groq_client is not None:
                        try:
                            if uploaded_file is not None:
                                image_data = base64.b64encode(uploaded_file.getvalue()).decode("ascii")
                                image_mime_type = uploaded_file.type or "image/jpeg"
                                image_url = f"data:{image_mime_type};base64,{image_data}"
                                groq_user_content = [
                                    {
                                        "type": "text",
                                        "text": "Read the attached image and follow the system instructions."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {"url": image_url}
                                    }
                                ]
                            else:
                                groq_user_content = source_text

                            groq_completion = groq_client.chat.completions.create(
                                model="qwen/qwen3.8-27b",
                                messages=[
                                    {"role": "system", "content": prompt},
                                    {"role": "user", "content": groq_user_content}
                                ]
                            )

                            response_text = groq_completion.choices[0].message.content
                            active_provider = "Groq qwen/qwen3.8-27b"
                            success = True

                        except Exception as e2:
                            groq_error = e2

                    if not success and gemini_client is not None:
                        try:
                            contents = [prompt, uploaded_image] if uploaded_image is not None else prompt
                            response = gemini_client.models.generate_content(
                                model="gemini-3.5-flash-lite",
                                contents=contents
                            )

                            response_text = response.text
                            active_provider = "Google Gemini (gemini-3.5-flash-lite)"
                            success = True

                        except Exception as e3:
                            st.error(f"All Model Providers Failed! Errors: {e1} | {groq_error} | {e3}")
            elif groq_client is not None:
                try:
                    if uploaded_file is not None:
                        image_data = base64.b64encode(uploaded_file.getvalue()).decode("ascii")
                        image_mime_type = uploaded_file.type or "image/jpeg"
                        image_url = f"data:{image_mime_type};base64,{image_data}"
                        groq_user_content = [
                            {
                                "type": "text",
                                "text": "Read the attached image and follow the system instructions."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url}
                            }
                        ]
                    else:
                        groq_user_content = source_text

                    groq_completion = groq_client.chat.completions.create(
                        model="qwen/qwen3.8-27b",
                        messages=[
                            {"role": "system", "content": prompt},
                            {"role": "user", "content": groq_user_content}
                        ]
                    )

                    response_text = groq_completion.choices[0].message.content
                    active_provider = "Groq qwen/qwen3.8-27b"
                    success = True

                except Exception as e2:
                    st.error(f"All Model Providers Failed! Errors: {e2}")

            if not success:
                st.session_state.current_translation = None
                        
            # Display Results if Successful
            if success:
                st.session_state.current_translation = {
                    "text": response_text,
                    "target_lang": target_lang,
                    "provider": active_provider,
                }

                source_description = (
                source_text.strip()
                if input_mode == "Text Input"
                else "Image upload"
                + (f" — {source_text.strip()}" if source_text.strip() else "")
            )

                history_item = {
                    "source": source_description,
                    "source_lang": source_lang,
                    "target_lang": target_lang,
                    "translated": response_text,
                    "provider": active_provider,
                }

                history = st.session_state.translation_history
                history.insert(0, history_item)
                del history[10:]

current_translation = st.session_state.current_translation
if current_translation is not None:
    st.subheader("Here is your Translation:")
    st.code(current_translation["text"], language=None)
    st.caption(f"⚡Handled Securely by: '{current_translation['provider']}'")

    if st.button("Listen Audio"):
        try:
            lang_codes = {
                "English": "en", "Spanish": "es", "French": "fr", "German": "de",
                "Hindi": "hi", "Marathi": "mr", "Japanese": "ja", "Mandarin Chinese": "zh-CN",
                "Arabic": "ar", "Portuguese": "pt", "Russian": "ru"
            }
            tts_lang = lang_codes.get(current_translation["target_lang"], "en")

            tts = gTTS(text=current_translation["text"], lang=tts_lang, slow=False)
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            audio_bytes.seek(0)
            st.audio(audio_bytes, format="audio/mp3")

        except Exception as tts_error:
            st.info(f"Could not generate audio playback: {tts_error}")

with st.sidebar:
    st.header("Translation history")

    if st.button("Clear history"):
        st.session_state.translation_history.clear()
        st.rerun()

    if not st.session_state.translation_history:
        st.caption("Your translations will appear here.")
    else:
        for index, item in enumerate(st.session_state.translation_history):
            title = f"{item['source_lang']} → {item['target_lang']}"
            with st.expander(title):
                st.caption(f"Provider: {item['provider']}")
                st.code(item["translated"], language=None)
                st.caption(f"Input: {item['source']}")