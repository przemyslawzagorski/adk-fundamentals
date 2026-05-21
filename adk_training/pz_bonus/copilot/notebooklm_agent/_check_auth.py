"""Szybki test dostępności API."""
import os
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

project = os.getenv("GOOGLE_CLOUD_PROJECT", "(not set)")
api_key = os.getenv("GOOGLE_API_KEY", "")
print(f"GCP Project: {project}")
print(f"API Key: {'set' if api_key else '(not set)'}")

try:
    import google.auth
    creds, proj = google.auth.default()
    print(f"ADC OK: project={proj}, creds={type(creds).__name__}")
except Exception as e:
    print(f"ADC: {e}")
