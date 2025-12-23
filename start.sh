#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID
    kill $FRONTEND_PID
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# Start Backend
echo "Starting FastAPI Backend..."
uv run uvicorn server:app --reload --port 8081 &
BACKEND_PID=$!

# Start Frontend
echo "Starting React Frontend..."
cd web
npm run dev -- --host &
FRONTEND_PID=$!

# Wait for both
wait $BACKEND_PID $FRONTEND_PID
