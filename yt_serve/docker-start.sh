#!/bin/bash

echo "Starting YouTube Playlist Manager..."

# Start backend
cd /app/backend
python run.py &

# Serve frontend
cd /app/frontend
npx serve dist -l 5173 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
