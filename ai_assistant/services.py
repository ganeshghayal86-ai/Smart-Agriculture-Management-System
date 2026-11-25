
import os

import assemblyai as aai

from dotenv import load_dotenv
from google import genai
from google.genai import types
from groq import Groq

load_dotenv(override=True)


# GEMINI SETUP
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in .env file")

client = genai.Client(
    api_key=API_KEY,
    http_options={"api_version": "v1beta"}
)


# GROQ SETUP
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")

groq_client = Groq(api_key=GROQ_API_KEY)


# ASSEMBLYAI SETUP
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")

if not ASSEMBLYAI_API_KEY:
    raise ValueError("ASSEMBLYAI_API_KEY is missing in .env file")

aai.settings.api_key = ASSEMBLYAI_API_KEY


MODEL = "gemini-3.5-flash-lite"


# AI FARMING CHATBOT

def ask_gemini(question, language="en"):

    print("GROQ CHATBOT FUNCTION CALLED")
    print("Selected Language:", language)

    language_map = {
        "mr": "Marathi (मराठी)",
        "hi": "Hindi (हिंदी)",
        "en": "English"
    }

    selected_language = language_map.get(language, "English")

    prompt = f"""
    You are an AI Farming Assistant.

    IMPORTANT LANGUAGE RULE:
    Reply ONLY in {selected_language}.
    Do not reply in any other language.
    Use the correct native script for Marathi and Hindi.

    Answer only agriculture-related questions.

    If the question is unrelated to agriculture,
    politely explain that you only answer farming questions.
    Give simple and useful answers to farmers.

    Question: {question}
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    return response.choices[0].message.content.strip()



# VOICE TRANSCRIPTION - ASSEMBLYAI
def transcribe_audio(audio_file, language):

    audio_bytes = audio_file.read()

    if not audio_bytes:
        raise ValueError("Audio recording is empty")

    language_codes = {
        "mr-IN": "mr",
        "hi-IN": "hi",
        "en-IN": "en"
    }

    selected_language = language_codes.get(language, "mr")

    config = aai.TranscriptionConfig(
        speech_models=["assemblyai-stt-3-7"],
        language_code=selected_language
    )

    transcriber = aai.Transcriber(config=config)

    transcript = transcriber.transcribe(audio_bytes)

    print("========== ASSEMBLYAI DEBUG ==========")
    print("Audio Size:", len(audio_bytes))
    print("Transcript ID:", transcript.id)
    print("Status:", transcript.status)
    print("Error:", transcript.error)
    print("Model Used:", transcript.speech_model_used)
    print("Text:", repr(transcript.text))
    print("======================================")

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(
            f"AssemblyAI Error: {transcript.error}"
        )

    if not transcript.text or not transcript.text.strip():
        raise ValueError(
            f"Empty transcription. Status: {transcript.status}"
        )

    return transcript.text.strip()


# AI PLANT DISEASE DETECTION
def analyze_leaf_image(image_file, crop_name):

    image_bytes = image_file.read()

    if not image_bytes:
        raise ValueError("Uploaded image is empty")

    mime_type = image_file.content_type or "image/jpeg"

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type
    )

    prompt = f"""
    You are an AI Plant Disease Detection Assistant.

    Crop name: {crop_name}

    Analyze the uploaded plant leaf image.

    Give:
    1. Possible disease name.
    2. Visible symptoms.
    3. Prevention methods.
    4. Suggested next steps.
    5. When to consult an agriculture expert.

    Give results in:
    English, Marathi and Hindi.

    If image is unclear, mention uncertainty.

    Never claim a confirmed diagnosis.
    Do not suggest chemical pesticide dosages.
    """

    response = client.models.generate_content(
        model=MODEL,
        contents=[prompt, image_part]
    )

    if not response.text:
        raise ValueError("Disease analysis returned empty response")

    return response.text.strip()
