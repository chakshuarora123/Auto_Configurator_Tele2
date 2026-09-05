#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Setting up Tele2 Auto-Configurator dev environment..."

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

uv python install 3.12
uv sync

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example — please edit it with your credentials."
fi

uv run pre-commit install

echo "✅ Setup complete."
echo "Run: uv run tele2-configurator watch   (or)   uv run tele2-configurator dashboard"
