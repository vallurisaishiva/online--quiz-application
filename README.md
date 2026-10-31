# Online Quiz Application
Responsive Flask + MySQL MCQ quiz with countdown timer, server-side scoring and result review.

## Setup
1. Start MySQL and run `mysql -u root -p < database/schema.sql`.
2. `python -m venv venv`
3. Activate venv: Windows `venv\\Scripts\\activate`; macOS/Linux `source venv/bin/activate`.
4. `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure MySQL.
6. `python app.py`; open http://127.0.0.1:5001.

Correct answers are only queried by Flask when the user submits. For production, add authentication, CSRF protection, saved attempts, HTTPS and a production WSGI server.
