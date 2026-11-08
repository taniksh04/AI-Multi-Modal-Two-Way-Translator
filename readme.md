# AI Multi-Modal Two-Way Translator

A Streamlit application that translates text or text found in an uploaded image. It supports multiple target languages, keeps a short translation history for the current session, and can generate spoken audio for a translation on request.

## Features

- Translate typed text or text contained in a PNG, JPG, or JPEG image.
- Select a source language or use automatic detection, then select a target language.
- Use Google Gemini as the primary translation provider, with Groq and a secondary Gemini model as fallbacks.
- Copy translated text using the copy control on the displayed text block.
- Generate audio only after clicking **Listen Audio**.
- View up to 10 recent translations in the sidebar and clear the history. History is session-only and is not saved permanently.

## Requirements

- Python 3.9 or newer
- At least one API key: Google Gemini or Groq
- Both keys are recommended to enable the complete provider fallback chain.

## Setup

1. Clone the repository and open its directory.
2. Create and activate a virtual environment:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project directory and add your API keys:

   ```dotenv
   GEMINI_API_KEY=your_gemini_api_key
   GROQ_API_KEY=your_groq_api_key
   ```

   At least one key is required. With only `GEMINI_API_KEY`, translation uses Gemini models. With only `GROQ_API_KEY`, Groq handles translations. Both keys enable the full fallback chain. Keep `.env` private; do not commit real API keys.

5. Start the application:

   ```powershell
   streamlit run app.py
   ```

Streamlit will print a local URL to open in your browser.

## Usage

1. Choose **Text Input** or **Image OCR**.
2. Enter text or upload an image. For image translation, the context/instruction field is optional.
3. Choose source and target languages, then select **Translate Text**.
4. Use the copy control on the translation text block to copy the result.
5. Select **Listen Audio** to generate audio; then press play in the audio player.
6. Use the sidebar to review recent translations or clear the session history.

## Notes

- Translation history is held in Streamlit session state. It is temporary and limited to the active session.
- Image translation sends the uploaded image to the selected AI provider. Do not upload sensitive images unless you are comfortable sharing them with that provider.
- Text-to-speech requires network access to the gTTS service.
