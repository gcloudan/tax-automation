#!/usr/bin/env bash
# =============================================================================
# bootstrap.sh — One-shot OCI Ubuntu 22.04 VM setup
# Run as: ubuntu user (not root)
# Usage:  chmod +x scripts/bootstrap.sh && ./scripts/bootstrap.sh
# =============================================================================

set -euo pipefail

echo "============================================"
echo "  tax-automation Bootstrap"
echo "  OCI Oracle Free VM (ARM Ubuntu 22.04)"
echo "============================================"

# --- 1. System update ---
echo "[1/6] Updating system packages..."
sudo apt-get update -qq && sudo apt-get upgrade -y -qq

# --- 2. Install Docker ---
echo "[2/6] Installing Docker..."
if ! command -v docker &> /dev/null; then
  curl -fsSL https://get.docker.com | sudo sh
  sudo usermod -aG docker "$USER"
  echo "  ✓ Docker installed. NOTE: Log out and back in for group to apply."
  echo "    Re-run this script after re-login if needed."
else
  echo "  ✓ Docker already installed"
fi

# --- 3. Install Docker Compose plugin ---
echo "[3/6] Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
  sudo apt-get install -y docker-compose-plugin -qq
fi
echo "  ✓ $(docker compose version)"

# --- 4. Check .env exists ---
echo "[4/6] Checking environment config..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

if [ ! -f "$REPO_ROOT/.env" ]; then
  echo "  ⚠️  .env file not found!"
  echo "     Copy .env.example → .env and fill in your secrets:"
  echo "     cp $REPO_ROOT/.env.example $REPO_ROOT/.env"
  echo "     nano $REPO_ROOT/.env"
  exit 1
fi
echo "  ✓ .env found"

# --- 5. Start services ---
echo "[5/6] Starting Docker services..."
cd "$REPO_ROOT"
docker compose pull --quiet
docker compose up -d --build
echo "  ✓ Services started"

# --- 6. Health check ---
echo "[6/6] Waiting for services to come up (15s)..."
sleep 15

N8N_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5678 || echo "000")
PDF_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health || echo "000")

echo ""
echo "============================================"
echo "  Bootstrap Complete"
echo "============================================"
echo "  n8n:         http://$(hostname -I | awk '{print $1}'):5678  [HTTP $N8N_STATUS]"
echo "  pdf-service: http://$(hostname -I | awk '{print $1}'):8001  [HTTP $PDF_STATUS]"
echo ""
echo "  Next steps:"
echo "  1. Open n8n in browser and import n8n/workflows/tax-pipeline-v2.json"
echo "  2. Configure Google Sheets credentials in n8n"
echo "  3. Run: ./scripts/healthcheck.sh"
echo "============================================"
