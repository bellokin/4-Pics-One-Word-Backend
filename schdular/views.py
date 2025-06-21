import requests
import os
import json

from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from four_pics_one_word.db import create_connection
from psycopg2.extras import Json

api_server = os.getenv("API_SERVER")
API_GENERATE_ENDPOINT = f"{api_server}/api/gameEngine/"



@api_view(['POST'])
def generate_and_insert_riddles(request):
    """Call internal riddle API 100 times and insert each result into DB."""
    conn = create_connection()
    if not conn:
        return Response({"error": "DB connection failed"}, status=500)

    insert_sql = """
        INSERT INTO questions (
            answer, image_urls, image_alt_texts, close_guesses, category, explanations
        ) VALUES (%s, %s, %s, %s, %s, %s)
    """

    inserted = 0
    errors = []
    cur = conn.cursor()

    for _ in range(10):
        try:
            res = requests.post(API_GENERATE_ENDPOINT, timeout=15)
            if res.status_code != 200:
                errors.append(f"API error: {res.status_code}")
                continue

            data = res.json()
          
            # Serialize lists and JSONB
            values = (
                data["answer"],
                data["image_urls"],
                data["image_alt_texts"],
                data["close_guesses"],
                data.get("category"),
                Json(data["explanations"]),  # psycopg2.extras.Json for JSONB
            )

            cur.execute(insert_sql, values)
            inserted += 1

        except Exception as e:
            errors.append(str(e))

    conn.commit()
    cur.close()
    conn.close()

    return Response({
        "status": "completed",
        "inserted": inserted,
        "errors": errors
    })

@api_view(['GET'])
def get_all_riddles(request):
    """Return all riddle records."""
    conn = create_connection()
    if not conn:
        return Response({"error": "DB connection failed"}, status=500)

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions ORDER BY created_at DESC")
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()

        riddles = [dict(zip(columns, row)) for row in rows]
        return Response(riddles)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
