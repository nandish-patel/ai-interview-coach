import json
import os
import traceback

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq
import groq

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
client = Groq(api_key=GROQ_API_KEY)


def _mask_api_key(api_key):
    if not api_key:
        return None
    if len(api_key) <= 8:
        return "(too short to mask)"
    return f"{api_key[:4]}...{api_key[-4:]}"


def _verify_env():
    print("[Groq] " + "=" * 50)
    print(f"[Groq] Provider: Groq")
    print(f"[Groq] Model: {GROQ_MODEL}")
    if GROQ_API_KEY:
        print("[Groq] GROQ_API_KEY loaded: yes")
        print(f"[Groq] GROQ_API_KEY length: {len(GROQ_API_KEY)}")
        print(f"[Groq] GROQ_API_KEY hint: {_mask_api_key(GROQ_API_KEY)}")
    else:
        print("[Groq] GROQ_API_KEY loaded: no")
        print("[Groq] Create a .env file with GROQ_API_KEY=your_key")
    print("[Groq] " + "=" * 50)


_verify_env()


def safe_json(text):
    """Extract JSON safely even if AI wraps it in markdown."""
    try:
        text = text.strip()
        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()
        elif text.startswith("```"):
            text = text.replace("```", "").strip()
        return json.loads(text)
    except Exception:
        return None


def _log_exception(exc):
    print("\n[Groq] Error:")
    traceback.print_exc()
    print()


def _call_groq(prompt):
    if not GROQ_API_KEY:
        msg = "Groq API key missing. Add GROQ_API_KEY in your .env file."
        print(f"[Groq] {msg}")
        return {"error": msg}

    try:
        print(f"[Groq] Calling model: {GROQ_MODEL}")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert AI interview coach."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=800,
        )

        ai_text = ""
        if response and response.choices:
            message = response.choices[0].message
            ai_text = message.content if message and message.content else ""

        if not ai_text.strip():
            msg = "Groq returned an empty response."
            print(f"[Groq] {msg}")
            return {"error": msg}

        print(f"[Groq] Success with model: {GROQ_MODEL}")
        return {"text": ai_text.strip()}

    except groq.AuthenticationError as exc:
        _log_exception(exc)
        return {
            "error": "Invalid Groq API key. Check GROQ_API_KEY in your .env file."
        }
    except groq.RateLimitError as exc:
        _log_exception(exc)
        return {"error": f"Groq rate limit exceeded: {exc}"}
    except (groq.APIConnectionError, groq.APITimeoutError) as exc:
        _log_exception(exc)
        return {"error": f"Groq network error: {exc}"}
    except groq.APIStatusError as exc:
        _log_exception(exc)
        return {"error": f"Groq API error [{exc.status_code}]: {exc.message}"}
    except groq.APIError as exc:
        _log_exception(exc)
        return {"error": f"Groq API error: {exc}"}
    except Exception as exc:
        _log_exception(exc)
        return {"error": f"Groq error ({type(exc).__name__}): {exc}"}


def generate_questions(role, level, question_type, count):
    prompt = f"""
Generate interview questions for this candidate.

Role: {role}
Level: {level}
Question type: {question_type}
Number of questions: {count}

Return ONLY valid JSON in this format:
{{
  "questions": [
    {{
      "id": 1,
      "question": "question text",
      "ideal_points": ["point 1", "point 2", "point 3"]
    }}
  ]
}}
No markdown. No explanation outside JSON.
"""

    result = _call_groq(prompt)
    if "error" in result:
        return result

    data = safe_json(result["text"])
    if not data or "questions" not in data:
        return {"error": "AI response was not in valid JSON format. Try again."}
    return data


def evaluate_answer(role, question, answer):
    prompt = f"""
Evaluate the user's interview answer.

Role: {role}
Question: {question}
User answer: {answer}

Return ONLY valid JSON in this format:
{{
  "score": 0,
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "better_answer": "A stronger sample answer in simple language.",
  "confidence_tip": "One short speaking/confidence tip."
}}
Score should be from 0 to 10.
No markdown. No explanation outside JSON.
"""

    result = _call_groq(prompt)
    if "error" in result:
        return result

    data = safe_json(result["text"])
    if not data or "score" not in data:
        return {"error": "AI response was not in valid JSON format. Try again."}
    return data


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    role = data.get("role", "Software Engineer")
    level = data.get("level", "Beginner")
    question_type = data.get("question_type", "Mixed")
    count = int(data.get("count", 5))

    if not role.strip():
        return jsonify({"error": "Please enter a job role."}), 400

    count = max(1, min(count, 10))
    result = generate_questions(role, level, question_type, count)
    status = 500 if "error" in result else 200
    return jsonify(result), status


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    role = data.get("role", "Software Engineer")
    question = data.get("question", "")
    answer = data.get("answer", "")

    if not question.strip() or not answer.strip():
        return jsonify({"error": "Question and answer are required."}), 400

    result = evaluate_answer(role, question, answer)
    status = 500 if "error" in result else 200
    return jsonify(result), status


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "groq_api_key_exists": bool(GROQ_API_KEY),
        "provider": "Groq",
        "model": GROQ_MODEL,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)