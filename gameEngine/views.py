import os
from itertools import cycle
import random
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .structures.categories import all_categories

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from django.http import JsonResponse 
from four_pics_one_word.db import create_connection


# Load API keys
groq_api_key = os.getenv("GROQ_API_KEY")
unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")

# Initialize LLM
llm = ChatGroq(
    model_name="gemma2-9b-it",
    temperature=0.45,
    api_key=groq_api_key,
)

# Setup parser
parser = JsonOutputParser()

prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an expert at creating perfect '4 Pics 1 Word' puzzles.

Your job is to generate a high-quality puzzle where:
- You choose a **single common noun** as the answer.
- Then, write **four short, concrete, visual image descriptions** that show strong, direct clues about the answer.
- These descriptions will be used to search Unsplash for real images — they must be **real-world objects or scenes** someone could clearly photograph.

🔒 RULES (Strict):
1. All image descriptions:
   - Must be **tangible**, **real**, and **visible** in a photo
   - Must relate to the answer in a **literal**, **physical**, or **functional** way
   - Must be 1–3 words long, searchable, and **not include** the answer itself

2. The answer:
   - Must be a **single, everyday, physical noun**
   - Must be clearly hinted by ALL four image descriptions
   - Must NOT appear inside any image description (even as a substring)

3. No abstract, poetic, emotional, or symbolic ideas.

📤 OUTPUT FORMAT (JSON only):
{{
  "answer": "correct_word",
  "image_descriptions": ["desc1", "desc2", "desc3", "desc4"],
  "close_guesses": ["guess1", "guess2", "guess3"],
  "explanations": {{
    "desc1": "How this image connects to the answer",
    "desc2": "How this image connects to the answer",
    "desc3": "How this image connects to the answer",
    "desc4": "How this image connects to the answer"
  }}
}}"""
    ),
    (
        "user",
        "Create a '4 Pics 1 Word' puzzle for the category: {category}. Only output the JSON."
    )
])


chain = prompt | llm | parser

# Image search function
def fetch_unsplash_image(description):
    clean_desc = ' '.join(description.lower().strip().split()[:2])
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": clean_desc,
        "per_page": 1,
        "client_id": unsplash_access_key,
        "content_filter": "high",
        "orientation": "squarish"
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            return {
                "url": data["results"][0]["urls"]["small"],
                "alt_text": data["results"][0].get("alt_description", clean_desc)
            }
    except Exception as e:
        print(f"Image fetch error: {str(e)}")
    return None



@api_view(['POST'])
def generate_question(request):
    try:
        shuffled_categories = random.sample(all_categories, len(all_categories))
        category_iterator = cycle(shuffled_categories)
        category = next(category_iterator)

        result = chain.invoke({"category": category})

        if not all(key in result for key in ["answer", "image_descriptions", "close_guesses"]):
            return Response({"error": "Invalid puzzle format"}, status=500)

        image_results = []
        for desc in result["explanations"]:
            img = fetch_unsplash_image(desc)
            if not img:
                return Response({"error": f"Could not fetch image for: {desc}"}, status=500)
            image_results.append(img)

        return Response({
            "answer": result["answer"],
            "image_urls": [img["url"] for img in image_results],
            "image_alt_texts": [img["alt_text"] for img in image_results],
            "close_guesses": result["close_guesses"],
            "category": category,
            "explanations": result["explanations"]  # <-- include this
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


