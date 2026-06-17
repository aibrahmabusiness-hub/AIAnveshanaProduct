#!/bin/bash
# Start the lightweight engine in the background
echo "Starting lightweight Node engine..."
cd lightweight-engine
npm install --production
node index.js &
cd ..

# Start the python backend
echo "Starting Python FastAPI backend..."
cd backend
PORT="${PORT:-8000}"
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
