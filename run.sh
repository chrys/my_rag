#!/bin/bash

# Configuration
VPS_SSH_USER="chrys"
VPS_IP="167.99.197.215"
LOCAL_PORT=5432
REMOTE_HOST="127.0.0.1"
REMOTE_PORT=5432

echo "🚀 Spinning up SSH Tunnel in the background..."
# Opens the tunnel and runs in background. -f runs in background, -N disables shell
ssh -o ExitOnForwardFailure=yes -L $LOCAL_PORT:$REMOTE_HOST:$REMOTE_PORT $VPS_SSH_USER@$VPS_IP -N &
TUNNEL_PID=$!

# Trap Ctrl+C (SIGINT) and cleanup the background SSH process when Django stops
cleanup() {
    echo -e "\n🛑 Stopping Django and shutting down SSH Tunnel..."
    kill $TUNNEL_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Wait a split second for the tunnel to bind
sleep 0.5

# Start Django
python manage.py runserver
