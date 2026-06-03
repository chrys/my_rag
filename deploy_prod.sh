#!/bin/bash
# ==============================================================================
# Google File Search Dashboard - Production Deployment Script
# Usage: ./deploy_prod.sh
# ==============================================================================

set -e

# Configuration
APP_DIR="/srv/rag-dashboard"
VENV_DIR="${APP_DIR}/.venv"
PIP="${VENV_DIR}/bin/pip"
PYTHON="${VENV_DIR}/bin/python"
export DJANGO_SETTINGS_MODULE="src.apps.my_rag_project.settings"

# Color outputs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}====================================================${NC}"
echo -e "${YELLOW}Starting Production Deployment...${NC}"
echo -e "${YELLOW}====================================================${NC}"

# 1. Ensure we are in the correct directory
if [ "$(pwd)" != "${APP_DIR}" ]; then
    echo -e "${YELLOW}Navigating to app directory: ${APP_DIR}${NC}"
    cd "${APP_DIR}"
fi

# 2. Pull latest changes (optional, usually done before running the script)
# echo -e "${YELLOW}[1/6] Pulling latest git changes...${NC}"
# git pull
# echo -e "${GREEN}✓ Git pull complete.${NC}\n"

# 3. Install/upgrade production dependencies
echo -e "${YELLOW}[1/5] Installing production python dependencies...${NC}"
if [ -f "${PIP}" ]; then
    "${PIP}" install --upgrade pip
    "${PIP}" install -r requirements/requirements-prod.txt
    echo -e "${GREEN}✓ Python dependencies updated.${NC}\n"
else
    echo -e "${RED}✗ Virtual environment pip not found at ${PIP}${NC}"
    exit 1
fi

# 4. Run Django Migrations (using DJANGO_ENV=production)
echo -e "${YELLOW}[2/5] Running Django database migrations (PostgreSQL)...${NC}"
DJANGO_ENV=production "${PYTHON}" manage.py migrate
echo -e "${GREEN}✓ Database migrated successfully.${NC}\n"

# 5. Collect Static Assets (using DJANGO_ENV=production)
echo -e "${YELLOW}[3/5] Collecting static assets...${NC}"
DJANGO_ENV=production "${PYTHON}" manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static assets collected.${NC}\n"

# 6. Restart Systemd Services
echo -e "${YELLOW}[4/5] Restarting application services...${NC}"
sudo systemctl restart rag-dashboard
sudo systemctl restart rag-api-dashboard
echo -e "${GREEN}✓ Services restarted.${NC}\n"

# 7. Verification / Health Checks
echo -e "${YELLOW}[5/5] Verifying service status...${NC}"
sleep 2

# Check main Django dashboard service
if systemctl is-active --quiet rag-dashboard; then
    echo -e "${GREEN}✓ Dashboard service (rag-dashboard) is RUNNING.${NC}"
else
    echo -e "${RED}✗ Dashboard service (rag-dashboard) is FAILED.${NC}"
    sudo systemctl status rag-dashboard --no-pager
fi

# Check RAG API service
if systemctl is-active --quiet rag-api-dashboard; then
    echo -e "${GREEN}✓ API service (rag-api-dashboard) is RUNNING.${NC}"
else
    echo -e "${RED}✗ API service (rag-api-dashboard) is FAILED.${NC}"
    sudo systemctl status rag-api-dashboard --no-pager
fi

echo -e "${YELLOW}====================================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}====================================================${NC}"
