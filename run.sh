#!/bin/bash

# Configuration
VPS_SSH_USER="chrys"
VPS_IP="167.99.197.215"
LOCAL_PORT=5432
REMOTE_HOST="127.0.0.1"
REMOTE_PORT=5432

# Activate virtual environment if present
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Ensure python binary is available
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        echo "❌ Error: Python not found in environment."
        exit 1
    fi
fi

# Clean up any existing process on LOCAL_PORT (e.g. orphaned SSH tunnel from a previous run)
EXISTING_PID=$(lsof -ti :$LOCAL_PORT 2>/dev/null)
if [ -n "$EXISTING_PID" ]; then
    echo "⚠️ Port $LOCAL_PORT is already in use by PID $EXISTING_PID. Cleaning up..."
    kill -9 $EXISTING_PID 2>/dev/null || true
    sleep 0.5
fi

echo "🚀 Spinning up SSH Tunnel in the background..."
# Opens the tunnel and runs in background.
ssh -o ExitOnForwardFailure=yes -L $LOCAL_PORT:$REMOTE_HOST:$REMOTE_PORT $VPS_SSH_USER@$VPS_IP -N &
TUNNEL_PID=$!

# Cleanup function to kill SSH tunnel when script finishes or is interrupted
cleanup() {
    echo -e "\n🛑 Shutting down SSH Tunnel..."
    if [ -n "$TUNNEL_PID" ]; then
        kill $TUNNEL_PID 2>/dev/null
    fi
}
trap cleanup EXIT SIGINT SIGTERM

# Wait a split second for the tunnel to bind
sleep 0.5

# Start Django
$PYTHON_CMD manage.py runserver

