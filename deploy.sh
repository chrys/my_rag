#!/usr/bin/env bash

# ==============================================================================
# Manual Deployment Script for my_rag Dashboard
#
# Usage:
#   ./deploy.sh              # Run tests, push to github, push to myVPS3 (triggers server hook)
#   ./deploy.sh --skip-tests  # Skip running tests before pushing (emergency)
#   ./deploy.sh --dry-run     # Run tests and checks without pushing to remotes
# ==============================================================================

set -e

COLOR_RESET="\033[0m"
COLOR_GREEN="\033[1;32m"
COLOR_RED="\033[1;31m"
COLOR_YELLOW="\033[1;33m"
COLOR_BLUE="\033[1;34m"

SKIP_TESTS=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
    esac
done

echo -e "${COLOR_BLUE}🚀 Starting deployment check for my_rag...${COLOR_RESET}"

# 1. Activate virtual environment if available
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 2. Check working directory status
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${COLOR_YELLOW}⚠️ Warning: You have uncommitted changes in your working tree.${COLOR_RESET}"
    git status --short
    echo -e "${COLOR_RED}❌ Aborting deployment. Please commit or stash your changes before deploying.${COLOR_RESET}"
    exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${COLOR_YELLOW}⚠️ Current branch is '$CURRENT_BRANCH' (not 'main').${COLOR_RESET}"
    read -p "Do you want to continue deploying '$CURRENT_BRANCH' to production? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${COLOR_RED}❌ Deployment cancelled.${COLOR_RESET}"
        exit 1
    fi
fi

# 3. Run unit and regression tests
if [ "$SKIP_TESTS" = true ]; then
    echo -e "${COLOR_YELLOW}⏭️ Skipping local test suite (--skip-tests flag detected)...${COLOR_RESET}"
else
    echo -e "${COLOR_BLUE}🧪 Running local test suite with DJANGO_ENV=testing...${COLOR_RESET}"
    if DJANGO_ENV=testing .venv/bin/pytest Testing/unit Testing/regression -v; then
        echo -e "${COLOR_GREEN}✅ All tests passed successfully!${COLOR_RESET}"
    else
        echo -e "${COLOR_RED}❌ Tests failed! Aborting deployment to production.${COLOR_RESET}"
        exit 1
    fi
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${COLOR_GREEN}🔍 Dry run complete. No code was pushed to remotes.${COLOR_RESET}"
    exit 0
fi

# 4. Push to github
echo -e "${COLOR_BLUE}📤 Pushing branch '$CURRENT_BRANCH' to GitHub ('github' remote)...${COLOR_RESET}"
git push github "$CURRENT_BRANCH"
echo -e "${COLOR_GREEN}✅ Pushed to GitHub.${COLOR_RESET}"

# 5. Push to myVPS3 production (triggers server post-receive hook)
echo -e "${COLOR_BLUE}🚀 Pushing branch '$CURRENT_BRANCH' to production ('myVPS3' remote)...${COLOR_RESET}"
git push myVPS3 "$CURRENT_BRANCH"
echo -e "${COLOR_GREEN}🎉 Code pushed to myVPS3! Production post-receive hook triggered successfully.${COLOR_RESET}"
