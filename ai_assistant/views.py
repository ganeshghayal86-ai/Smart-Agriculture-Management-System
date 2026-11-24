
from django.shortcuts import render,redirect
from .services import ask_gemini


def chatbot(request):
    chat_history = request.session.get('chat_history', [])
    error = ""

    if request.method == "POST":
        question = request.POST.get("question", "").strip()

        if question:
            try:
                answer = ask_gemini(question)

                chat_history.append({
                    'question': question,
                    'answer': answer
                })

                request.session['chat_history'] = chat_history

            except Exception:
                error = "AI is temporarily unavailable. Please try again later."

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

