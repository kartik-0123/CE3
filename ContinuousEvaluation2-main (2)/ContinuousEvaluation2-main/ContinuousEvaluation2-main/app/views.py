from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.http import JsonResponse

@csrf_exempt
def booky_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')

        # Use HuggingFace's public inference API for a demo chatbot
        api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        payload = {"inputs": user_message}
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "generated_text" in data:
                    reply = data["generated_text"]
                elif isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                    reply = data[0]["generated_text"]
                else:
                    reply = "Sorry, I didn't get that. Can you rephrase?"
            else:
                reply = "Sorry, I couldn't reach my AI brain right now."
        except Exception as e:
            reply = "Sorry, I couldn't reach my AI brain right now."

        return JsonResponse({'reply': reply})
    return JsonResponse({'reply': "Invalid request."}) 