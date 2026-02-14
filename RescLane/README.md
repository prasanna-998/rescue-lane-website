# Rescue Lane

Simple Flask-based rescue/mechanic-request web app.

## Project layout
- `app.py` — Flask application and routes.
- `templates/` — HTML templates used by the app.
- `static/` — static assets (CSS, JS, images) and `static/uploads/` for uploaded documents.
- `users.db` — SQLite DB created automatically on first run.

## Requirements
- Python 3.10+ (tested with 3.13)
- Flask (the project's venv already had Flask installed)

## Quick start (Windows)
Open a terminal in the project folder `RescLane/RescLane` and run:

```powershell
# create a venv (optional if you already have one)
python -m venv .venv
.\.venv\Scripts\activate
# install dependencies (create a requirements.txt if you want reproducible installs)
pip install flask
# run the app
python app.py
```

Example (if you already have the workspace venv):

```powershell
"D:\car parking project\.venv\Scripts\python.exe" app.py
```

Then open: http://127.0.0.1:5000/

## Notes
- The app initializes `users.db` automatically on startup. Do not commit the DB to git; add it to `.gitignore`.
- Uploaded mechanic documents are saved to `static/uploads/`.
- The app secret key is set in `app.py` (currently `app.secret_key = 'your_secret_key'`). Replace it with a secure value or use environment variables for production use.
- There is no `requirements.txt` in the repo; consider creating one:

```powershell
pip freeze > requirements.txt
```

## Suggested next steps
- Add `requirements.txt` and `.gitignore` to the project root.
- Move configuration (secret key, upload path) into a separate config file or environment variables.
- Use a production WSGI server (gunicorn / waitress) for deployment.

---
If you want, I can create `requirements.txt` and the `.gitignore` file now and/or open the app endpoints to test forms and DB writes.