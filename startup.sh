#!/usr/bin/env bash

# =========================
# Config
# =========================
APP_PATH="ai_ceo/dashboard/streamlit_app.py"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/streamlit_$(date +%Y%m%d_%H%M%S).log"

# =========================
# Prepare
# =========================
mkdir -p "$LOG_DIR"

echo "Starting Streamlit..."
echo "Log file: $LOG_FILE"

# =========================
# Env setup
# =========================
export PYTHONPATH=$(pwd)

export STREAMLIT_SERVER_FILE_WATCHER_TYPE="none"
export STREAMLIT_SERVER_RUN_ON_SAVE=false
export STREAMLIT_SERVER_ENABLE_WATCHDOG=false

export TRANSFORMERS_NO_TORCHVISION=1

# =========================
# Run
# =========================
streamlit run "$APP_PATH" 2>&1 | tee "$LOG_FILE"