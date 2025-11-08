#!/bin/bash
# Start both backend and frontend dev servers automatically
(cd backend && uvicorn server:app --reload --host 0.0.0.0 --port 8000 &)
sleep 3
(cd frontend && yarn start &)
echo "Both backend (port 8000) and frontend (port 3000) are starting..."
