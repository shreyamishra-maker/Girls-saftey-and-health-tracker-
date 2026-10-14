# Girls Safety & Health Assistant

A women's safety and wellness project with the original **Python Tkinter desktop prototype** and a new **Flask web app** for Render deployment.

## Web app features
- Account registration and login with Werkzeug password hashing, CSRF protection, and rate limits.
- Trusted/emergency contact management and SOS/location message previews.
- Period logs and estimated cycle insights; symptom and mood tracking.
- Private health notes, reminders, profile editing, and safety tips.
- SQLAlchemy database support for SQLite or PostgreSQL, health check endpoint, and GitHub Actions tests.

## Run locally
Use Python 3.11 or newer:
1. Create and activate a virtual environment.
2. Install dependencies with: pip install -r requirements.txt
3. Set a strong local SECRET_KEY environment variable.
4. Run: python app.py
5. Open http://127.0.0.1:5000. Run tests with: pytest -q

## Deploy on Render
1. Push or merge the deployment branch to GitHub.
2. In Render, choose New -> Blueprint, connect this repository, and select render.yaml.
3. Review the web service and persistent disk plan/cost before creating it. The blueprint stores SQLite data on a persistent disk at /var/data.
4. Render generates SECRET_KEY. Keep it private; never hard-code secrets.
5. Wait for deployment and check /healthz. Render will show the public website URL.
The app also supports PostgreSQL through DATABASE_URL. SQLite on an ephemeral filesystem can lose data after restarts or redeploys; use persistent storage and regular backups.

## Safety and privacy limitations
- Browser geolocation is requested only when the user chooses a message preview. It requires permission and usually HTTPS; accuracy can vary and location is not continuously tracked.
- SOS/location sharing only prepares text. It does NOT send SMS/WhatsApp, place calls, or notify saved contacts. Copy and send manually if appropriate. For immediate danger in India, call 112 directly when safe.
- Cycle estimates are not diagnosis or contraception advice.
- Health and contact data is stored in the configured database. Use a unique password, log out on shared devices, restrict access, back up carefully, and provide a suitable privacy notice before real use.
- The tracked safety_app.db file is removed from this deployment branch and database files are ignored. Removing a database from the latest commit does not remove it from older Git history; if it ever contained private records, review repository history and rotate any exposed secrets.

## Desktop version
The original Tkinter app remains available as main_app.py on a computer with Tkinter installed. Render's standard web service does not run Tkinter windows; use the Flask app for browser deployment.

## Security and tests
Production uses an environment-based secret, HTTP-only SameSite session cookie, CSRF protection, login/register rate limits, per-user record ownership checks, request-size limits, and security headers. Run pytest -q locally or use the included GitHub Actions workflow.
