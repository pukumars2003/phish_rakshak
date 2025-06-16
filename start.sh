#!/bin/bash
echo "🔁 Starting Gunicorn server..."
exec gunicorn -b 0.0.0.0:$PORT app:app
