# AI Interview Coach

A Flask + Groq AI project where users can generate interview questions and get feedback on their answers.

## Features

- Generate interview questions by role, level, and question type
- Answer selected questions
- Get AI score out of 10
- Get strengths, improvements, better sample answer, and confidence tip
- Clean web interface
- API key validation and safer error handling

## Setup

### 1. Open terminal in this folder

```bash
cd ai-interview-coach
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` file

Copy `.env.example` and rename it to `.env`.

```bash
cp .env.example .env
```

Then paste your Groq API key:

```env
GROQ_API_KEY=your_actual_api_key_here
```

Get a key from [Groq Console](https://console.groq.com/keys).

### 5. Run project

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Common Errors

### ModuleNotFoundError: No module named 'dotenv'

Run:

```bash
pip install -r requirements.txt
```

### API key not valid

Check:

- `.env` file exists
- variable name is exactly `GROQ_API_KEY`
- key is copied from Groq Console
- no extra quotes or spaces
- restart Flask after changing `.env`

### AI response not valid JSON

This app tries to clean markdown-wrapped JSON using `safe_json()`.
# ai-interview-coach
