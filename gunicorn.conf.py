import os

# Read PORT from environment (defaults to 10000 on Render if unset, or 5000 if configured)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Worker processes (1 for free tier to stay well within memory limits)
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))

# Log to stdout / stderr so logs appear in Render dashboard
accesslog = "-"
errorlog = "-"
