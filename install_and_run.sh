#!/bin/bash
# Nightclimb Arcade - One-command install & run
# Paste this ENTIRE script into Terminal.app and press Enter

set -e

echo "🎮 Installing Nightclimb Arcade..."
python3 -m pip install --quiet git+https://github.com/kaushalboii/Nightclimb.git

echo "✅ Installed! Adding to PATH for this session..."
export PATH="/Users/kaushal/Library/Python/3.9/bin:$PATH"

echo "🚀 Launching Nightclimb..."
nightclimb
