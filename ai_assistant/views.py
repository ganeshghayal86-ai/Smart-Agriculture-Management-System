
from django.shortcuts import render, redirect
from django.http import JsonResponse

from .services import ask_gemini, transcribe_audio



def chatbot(request):
    chat_history = request.session.get('chat_history', [])
    error = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        language = request.LANGUAGE_CODE
        language = language.split("-")[0]

        if question:
            try:
                answer = ask_gemini(question, language)

                chat_history.append({
                    'question': question,
                    'answer': answer
                })

                request.session['chat_history'] = chat_history

            except Exception as e:
                print("CHATBOT ERROR:", repr(e))
                error = str(e)

    return render(
        request,
        "ai_assistant/chatbot.html",
        {
            "chat_history": chat_history,
            "error": error
        }
    )



def clear_chat(request):
    if request.method == "POST":
        request.session['chat_history'] = []

    return redirect('chatbot')


def voice_transcribe(request):
    if request.method == "POST":

        audio_file = request.FILES.get("audio")
        language = request.POST.get("language", "mr-IN")

        if not audio_file:
            return JsonResponse(
                {"error": "Audio not received"},
                status=400
            )

        print("========== VOICE DEBUG ==========")
        print("Audio Name:", audio_file.name)
        print("Audio Type:", audio_file.content_type)
        print("Audio Size:", audio_file.size)
        print("Selected Language:", language)

        try:
            transcript = transcribe_audio(audio_file, language)

            print("Transcript:", repr(transcript))
            print("=================================")

            if not transcript:
                return JsonResponse(
                    {"error": "Empty transcription received"},
                    status=500
                )

            return JsonResponse({
                "transcript": transcript
            })

        except Exception as e:
            import traceback

            print("VOICE TRANSCRIPTION ERROR:", repr(e))
            traceback.print_exc()

            return JsonResponse(
                {"error": str(e)},
                status=500
            )

    return JsonResponse(
        {"error": "Invalid request"},
        status=405
    )
