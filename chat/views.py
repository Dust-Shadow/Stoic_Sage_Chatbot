from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chat.models import StoicQuote
import re


def index(request):
    return render(request, "chat/index.html")


@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        try:
            user_message = request.POST.get("message")
            response_message = generate_stoic_response(user_message)
            return JsonResponse({"message": response_message})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    return JsonResponse({"message": "Invalid request"}, status=400)


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def contains_excluded_keywords(text):
    # Define the phrases to exclude
    excluded_phrases = {"i am", "we are", "what", "why", "when", "where", "who", "how"}
    text_lower = text.lower()

    # Check if any of the excluded phrases are in the input text
    for phrase in excluded_phrases:
        if phrase in text_lower:
            return True

    return False


def generate_stoic_response(user_input):
    user_tokens = set(tokenize(user_input))
    best_match = None
    max_matches = 0

    for quote in StoicQuote.objects.all():
        quote_tokens = set(tokenize(quote.quote))
        num_matches = len(user_tokens & quote_tokens)

        if num_matches > max_matches:
            max_matches = num_matches
            best_match = quote

    if best_match:
        return f"Quote: {best_match.quote}\nPhilosopher: {best_match.philosopher}\nExplanation: {best_match.explanation}"

    fallback_quote = "You have power over your mind - not outside events. Realize this, and you will find strength."
    fallback_philosopher = "Marcus Aurelius"
    fallback_explanation = (
        "This quote reminds us that while we cannot control external circumstances, "
        "we do have control over our own thoughts and reactions. Embracing this understanding "
        "can help us navigate uncertainty and focus on what truly matters within our own minds."
    )

    return f"Quote: {fallback_quote}\nPhilosopher: {fallback_philosopher}\nExplanation: {fallback_explanation}"
