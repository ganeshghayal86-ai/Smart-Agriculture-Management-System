
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def ask_gemini(question):
    prompt = f"""
    You are an AI Farming Assistant.

    Rules:
    1. Answer only agriculture and farming-related questions.
    2. If the question is not related to farming, politely say:
       "Sorry, I can only answer agriculture and farming-related questions."
    3. Detect the language of the user's question.
    4. If the question is in Marathi, answer in Marathi.
    5. If the question is in Hindi, answer in Hindi.
    6. If the question is in English, answer in English.
    7. Give simple, clear and helpful answers to farmers.

    User Question: {question}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text



def analyze_leaf_image(image_file, crop_name):
    image_bytes = image_file.read()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=image_file.content_type
    )

    prompt = f"""
    You are an AI plant disease analysis assistant.

    Crop name: {crop_name}

    Analyze the uploaded leaf image.

    Provide the following information:
    1. Possible disease name.
    2. Visible symptoms.
    3. Basic prevention suggestions.
    4. When to consult an agriculture expert.

    IMPORTANT:
    Give the complete result in THREE languages.

    SECTION 1: ENGLISH
    Explain all information in simple English.

    SECTION 2: MARATHI
    Explain the same information in simple Marathi.

    SECTION 3: HINDI
    Explain the same information in simple Hindi.

    If the image is unclear or disease cannot be identified,
    clearly mention that the result is uncertain in all languages.

    Do not claim a confirmed diagnosis.
    Do not suggest specific chemical pesticides or dosages.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=[prompt, image_part]
    )

    return response.text
