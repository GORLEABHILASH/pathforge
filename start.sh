#!/bin/bash
set -e

echo "Starting PathForge..."
echo ""

# Check API key
if [ ! -f backend/.env ] || ! grep -q "ANTHROPIC_API_KEY" backend/.env; then
  echo "ERROR: backend/.env is missing or ANTHROPIC_API_KEY not set"
  echo "Run: echo 'ANTHROPIC_API_KEY=your_key' > backend/.env"
  exit 1
fi

# Install backend deps if needed
echo "Setting up backend..."
cd backend
if [ ! -d venv ]; then
  python3.12 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo "Backend ready."

# Start backend in background
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Start frontend
cd ../frontend
echo "Starting frontend..."
npm run dev &
FRONTEND_PID=$!
echo "Frontend running on http://localhost:3000 (PID: $FRONTEND_PID)"

echo ""
echo "PathForge is running:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" INT
wait
