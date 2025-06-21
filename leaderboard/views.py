from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.crypto import get_random_string
from four_pics_one_word.db import create_connection


@api_view(['POST'])
def register_user(request):
    import random
    user_id = request.data.get("user_id")
    email = request.data.get("email")

    if not user_id or not email:
        return Response({"error": "Missing user_id or email"}, status=400)

    conn = create_connection()
    if not conn:
        return Response({"error": "DB connection failed"}, status=500)

    # Realistic name pool
    name_pool = [
        "Max", "Brave", "Nova", "Shadow", "Zara", "Rogue", "Knight",
        "Storm", "Blaze", "Axel", "Jinx", "Luna", "Hunter", "Ghost",
        "Sage", "Echo", "Titan", "Frost", "Skye", "Dusk", "Flame", "Lord",
        "Phoenix", "Drake", "Lyra", "Viper", "Onyx", "Orion", "Zephyr",
        "Raven", "Thorne", "Ash", "Maverick", "Cypher", "Nyx", "Archer",
        "Jet", "Kairo", "Ember", "Silva", "Ryder", "Halo", "Noir", "Nash",
        "Artemis", "Koda", "Indigo", "Hawk", "Stryker", "NovaX", "Zen"
    ]


    try:
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT username, score, puzzles_solved FROM leaderboard_entries WHERE user_id = %s", (user_id,))
        row = cur.fetchone()

        if row:
            username, score, puzzles_solved = row
            status = "existing"
        else:
            random_name = random.choice(name_pool)
            random_number = random.randint(100, 9999)
            username = f"{random_name}{random_number}"

            score = 0
            puzzles_solved = 0

            insert_sql = """
                INSERT INTO leaderboard_entries (user_id, email, username, score, puzzles_solved)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(insert_sql, (user_id, email, username, score, puzzles_solved))
            conn.commit()
            status = "created"

        cur.close()
        conn.close()

        return Response({
            "status": status,
            "username": username,
            "score": score,
            "puzzles_solved": puzzles_solved
        })

    except Exception as e:
        conn.rollback()
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_top_100(request):
    conn = create_connection()
    if not conn:
        return Response({"error": "DB connection failed"}, status=500)

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT username, score, puzzles_solved 
            FROM leaderboard_entries 
            ORDER BY score DESC 
            LIMIT 100
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        data = [
            {
                "username": row[0],
                "score": row[1],
                "puzzles_solved": row[2]
            } for row in rows
        ]
        return Response(data)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
def update_score(request):
    user_id = request.data.get("user_id")
    increment = int(request.data.get("increment", 10))

    if not user_id:
        return Response({"error": "Missing user_id"}, status=400)

    conn = create_connection()
    if not conn:
        return Response({"error": "DB connection failed"}, status=500)

    try:
        cur = conn.cursor()

        # Update score
        cur.execute("""
            UPDATE leaderboard_entries
            SET score = score + %s,
                puzzles_solved = puzzles_solved + 1,
                last_updated = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING score, puzzles_solved
        """, (increment, user_id))

        result = cur.fetchone()

        if not result:
            return Response({"error": "User not found"}, status=404)

        conn.commit()
        cur.close()
        conn.close()

        return Response({
            "message": "Score updated",
            "new_score": result[0],
            "puzzles_solved": result[1]
        })

    except Exception as e:
        conn.rollback()
        return Response({"error": str(e)}, status=500)
